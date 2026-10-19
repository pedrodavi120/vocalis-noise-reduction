import logging
import threading
from typing import Callable, Optional
import numpy as np
import sounddevice as sd

from vocalis.core.filters import AudioFilters, ContinuousHighPassFilter, ContinuousNoiseGate

logger = logging.getLogger(__name__)

# Tenta carregar RNNoise nativo (padrão ouro utilizado pelo Discord e OBS Studio)
try:
    from pyrnnoise.rnnoise import (
        FRAME_SIZE as RNNOISE_FRAME_SIZE,
        create as rnnoise_create,
        destroy as rnnoise_destroy,
        process_mono_frame as rnnoise_process_mono_frame,
    )
    RNNOISE_AVAILABLE = True
except Exception as e:
    logger.warning("RNNoise indisponível, utilizando fallback Overlap-Add DSP: %s", e)
    RNNOISE_AVAILABLE = False
    RNNOISE_FRAME_SIZE = 480


class RealtimeDenoiseEngine:
    """
    Motor de streaming de áudio contínuo de alta fidelidade e baixíssima latência.
    Utiliza RNNoise (rede neural recorrente GRU) e filtros causais com preservação de estado,
    eliminando artefatos de voz robótica e ruído metálico.
    """

    def __init__(
        self,
        input_device_index: Optional[int] = None,
        output_device_index: Optional[int] = None,
        sample_rate: int = 48000,
        block_size: int = 480,
        gate_threshold_db: float = -42.0,
        denoise_strength: float = 0.85,
        enable_highpass: bool = True,
        on_metrics_callback: Optional[Callable[[float, float], None]] = None,
    ):
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.gate_threshold_db = gate_threshold_db
        self.denoise_strength = denoise_strength
        self.enable_highpass = enable_highpass
        self.on_metrics_callback = on_metrics_callback

        self.is_running = False
        self._stream: Optional[sd.Stream] = None
        self._lock = threading.Lock()

        # Componentes de processamento com estado contínuo
        self.highpass_filter = ContinuousHighPassFilter(
            cutoff_hz=80.0,
            sample_rate=self.sample_rate
        )
        self.noise_gate = ContinuousNoiseGate(
            threshold_db=self.gate_threshold_db,
            attack_ms=5.0,
            release_ms=120.0,
            sample_rate=self.sample_rate
        )

        # Estado RNNoise
        self._rnnoise_state = None
        self.use_rnnoise = RNNOISE_AVAILABLE and (self.sample_rate == 48000)

        # Buffers FIFO para emparelhamento perfeito de blocos de 480 amostras (10 ms)
        self._in_buffer = np.zeros(0, dtype=np.float32)
        self._out_buffer = np.zeros(0, dtype=np.float32)

        # Buffers para fallback Overlap-Add 50%
        self._ola_prev_input = np.zeros(self.block_size // 2, dtype=np.float32)
        self._ola_prev_output = np.zeros(self.block_size // 2, dtype=np.float32)
        self._noise_profile = None

    def set_gate_threshold(self, threshold_db: float) -> None:
        self.gate_threshold_db = threshold_db
        self.noise_gate.set_threshold(threshold_db)

    def set_denoise_strength(self, strength: float) -> None:
        self.denoise_strength = max(0.0, min(1.0, strength))

    def _process_rnnoise(self, chunk: np.ndarray) -> np.ndarray:
        """
        Processa chunks de áudio utilizando RNNoise através de buffers contínuos de 480 amostras.
        """
        self._in_buffer = np.concatenate([self._in_buffer, chunk])
        target_len = len(chunk)

        processed_frames = []
        frame_len = RNNOISE_FRAME_SIZE

        while len(self._in_buffer) >= frame_len:
            frame = self._in_buffer[:frame_len]
            self._in_buffer = self._in_buffer[frame_len:]

            # Converte com segurança para int16 [-32768, 32767]
            int16_frame = (np.clip(frame, -1.0, 1.0) * 32767.0).astype(np.int16)
            denoised_int16, speech_prob = rnnoise_process_mono_frame(self._rnnoise_state, int16_frame)
            denoised_float = denoised_int16.astype(np.float32) / 32768.0

            # Blend com controle granular de intensidade (dry/wet)
            blended = (self.denoise_strength * denoised_float) + ((1.0 - self.denoise_strength) * frame)

            # Noise gate suave inteligente guiado por VAD neural
            gated = self.noise_gate.process(blended, speech_prob=speech_prob)
            processed_frames.append(gated)

        if processed_frames:
            new_output = np.concatenate(processed_frames)
            self._out_buffer = np.concatenate([self._out_buffer, new_output])

        # Se houver amostras suficientes no buffer de saída, consome target_len
        if len(self._out_buffer) >= target_len:
            output_chunk = self._out_buffer[:target_len]
            self._out_buffer = self._out_buffer[target_len:]
            return output_chunk
        
        # Buffer de aquecimento (startup): se ainda não houver amostras prontas, retorna silêncio
        output_chunk = np.zeros(target_len, dtype=np.float32)
        avail = len(self._out_buffer)
        if avail > 0:
            output_chunk[:avail] = self._out_buffer
            self._out_buffer = np.zeros(0, dtype=np.float32)
        return output_chunk

    def _process_overlap_add_fallback(self, chunk: np.ndarray, in_rms_db: float) -> np.ndarray:
        """
        Fallback DSP baseado em Overlap-Add (OLA) 50% de sobreposição com partição unitária,
        evitando modulação em anel e artefatos robóticos.
        """
        half = self.block_size // 2
        # Monta frame de tamanho completo com sobreposição
        frame = np.concatenate([self._ola_prev_input, chunk[:half]])
        self._ola_prev_input = chunk[half:].copy()

        # Janela senoidal de partição unitária: w^2(n) + w^2(n+N/2) = 1.0
        n = np.arange(self.block_size)
        win = np.sin(np.pi * n / self.block_size).astype(np.float32)

        fft_data = np.fft.rfft(frame * win)
        power_spec = np.abs(fft_data) ** 2
        phase = np.angle(fft_data)

        if self._noise_profile is None:
            self._noise_profile = power_spec.copy()
        elif in_rms_db < self.gate_threshold_db:
            self._noise_profile = 0.95 * self._noise_profile + 0.05 * power_spec

        # Ganho de Wiener suave
        floor = 0.08 * (1.0 - self.denoise_strength) + 0.04
        snr = np.maximum(0.0, power_spec - (self.denoise_strength * self._noise_profile)) / (power_spec + 1e-10)
        gain = np.maximum(floor, snr)

        clean_spec = np.sqrt(power_spec) * gain * np.exp(1j * phase)
        reconstructed = np.fft.irfft(clean_spec).astype(np.float32) * win

        # Overlap-add
        out_chunk = reconstructed[:half] + self._ola_prev_output
        self._ola_prev_output = reconstructed[half:].copy()

        # Noise gate suave
        return self.noise_gate.process(np.concatenate([out_chunk, chunk[half:]]))

    def _audio_callback(self, indata, outdata, frames, time_info, status):
        """
        Callback de áudio em tempo real de alta prioridade.
        """
        if status:
            pass

        # Converte para mono float32
        in_chunk = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        in_rms_db = AudioFilters.calculate_rms_db(in_chunk)

        processed = in_chunk.copy()

        # 1. Filtro passa-alta causal sem transientes
        if self.enable_highpass:
            processed = self.highpass_filter.process(processed)

        # 2. Processamento de redução de ruído
        with self._lock:
            if self.use_rnnoise and self._rnnoise_state is not None:
                final_chunk = self._process_rnnoise(processed)
            else:
                final_chunk = self._process_overlap_add_fallback(processed, in_rms_db)

        # 3. Proteção anti-clipping
        final_chunk = np.clip(final_chunk, -0.98, 0.98)

        # 4. Distribuição para os canais de saída
        if outdata.shape[1] == 1:
            outdata[:, 0] = final_chunk
        else:
            outdata[:, 0] = final_chunk
            outdata[:, 1] = final_chunk

        out_rms_db = AudioFilters.calculate_rms_db(final_chunk)

        if self.on_metrics_callback:
            self.on_metrics_callback(in_rms_db, out_rms_db)

    def start(self) -> None:
        """
        Inicializa o estado e abre a stream contínua de áudio.
        """
        if self.is_running:
            return

        # Inicializa o estado RNNoise em C
        if RNNOISE_AVAILABLE and (self.sample_rate == 48000):
            try:
                self._rnnoise_state = rnnoise_create()
                self.use_rnnoise = True
            except Exception as e:
                logger.error("Erro ao instanciar RNNoise state: %s", e)
                self.use_rnnoise = False
        else:
            self.use_rnnoise = False

        self._in_buffer = np.zeros(0, dtype=np.float32)
        self._out_buffer = np.zeros(0, dtype=np.float32)
        self.highpass_filter.reset()

        self._stream = sd.Stream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            device=(self.input_device_index, self.output_device_index),
            channels=(1, 2),
            dtype='float32',
            callback=self._audio_callback
        )
        self._stream.start()
        self.is_running = True

    def stop(self) -> None:
        """
        Interrompe a stream e desaloca os recursos do motor.
        """
        if not self.is_running:
            return

        self.is_running = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if self._rnnoise_state is not None:
            try:
                rnnoise_destroy(self._rnnoise_state)
            except Exception:
                pass
            self._rnnoise_state = None

        self._noise_profile = None
        self._in_buffer = np.zeros(0, dtype=np.float32)
        self._out_buffer = np.zeros(0, dtype=np.float32)
