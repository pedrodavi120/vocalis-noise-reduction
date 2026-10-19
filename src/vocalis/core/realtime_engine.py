import threading
import time
import numpy as np
import sounddevice as sd
from typing import Callable, Optional
from vocalis.core.filters import AudioFilters


class RealtimeDenoiseEngine:
    """
    Motor de streaming contínuo de baixa latência para captura de microfone,
    tratamento em tempo real e redirecionamento para o dispositivo virtual de saída.
    """

    def __init__(
        self,
        input_device_index: Optional[int] = None,
        output_device_index: Optional[int] = None,
        sample_rate: int = 44100,
        block_size: int = 512,
        gate_threshold_db: float = -42.0,
        denoise_strength: float = 0.85,
        enable_highpass: bool = True,
        on_metrics_callback: Optional[Callable[[float, float], None]] = None
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
        self._noise_profile: Optional[np.ndarray] = None
        self._lock = threading.Lock()

        # Janelamento espectral
        self.window = np.hanning(self.block_size)
        self.prev_input = np.zeros(self.block_size // 2, dtype=np.float32)

    def set_gate_threshold(self, threshold_db: float) -> None:
        self.gate_threshold_db = threshold_db

    def set_denoise_strength(self, strength: float) -> None:
        self.denoise_strength = max(0.0, min(1.0, strength))

    def _audio_callback(self, indata, outdata, frames, time_info, status):
        """
        Callback de streaming executado em thread de alta prioridade do sounddevice.
        """
        if status:
            pass

        # Garante array 1D mono
        in_chunk = indata[:, 0] if indata.ndim > 1 else indata.flatten()

        # 1. Mede nível RMS de entrada
        in_rms_db = AudioFilters.calculate_rms_db(in_chunk)

        processed = in_chunk.copy()

        # 2. Filtro Passa-Alta rápido
        if self.enable_highpass:
            processed = AudioFilters.butter_highpass_filter(
                processed,
                cutoff_hz=80.0,
                sample_rate=self.sample_rate
            )

        # 3. Processamento Espectral Avançado: Filtro de Wiener Adaptativo + Spectral Floor
        # Elimina os artefatos de "musical noise" característicos de subtrações ingênuas
        fft_data = np.fft.rfft(processed * self.window)
        power_spectrum = np.abs(fft_data) ** 2
        phase = np.angle(fft_data)

        with self._lock:
            if self._noise_profile is None:
                self._noise_profile = power_spectrum.copy()
            else:
                # Estimador de ruído recursivo ponderado no tempo
                if in_rms_db < self.gate_threshold_db:
                    self._noise_profile = 0.92 * self._noise_profile + 0.08 * power_spectrum

            # Ganho de Wiener: H(w) = max(floor, (P_sig - P_noise) / P_sig)
            spectral_floor = 0.05 * (1.0 - self.denoise_strength) + 0.02
            estimated_snr = np.maximum(0.0, (power_spectrum - (self.denoise_strength * self._noise_profile))) / (power_spectrum + 1e-10)
            wiener_gain = np.maximum(spectral_floor, estimated_snr)

            # Aplica ganho e reconstrói fase
            clean_fft = np.sqrt(power_spectrum) * wiener_gain * np.exp(1j * phase)

        # Reconstrução por síntese IFFT
        reconstructed = np.fft.irfft(clean_fft).astype(np.float32)

        # 4. Noise gate adaptativo com transição suave
        final_chunk = AudioFilters.apply_noise_gate(
            reconstructed,
            threshold_db=self.gate_threshold_db,
            sample_rate=self.sample_rate
        )

        # Normalização anti-clipping
        final_chunk = np.clip(final_chunk, -0.98, 0.98)

        # Envia para a saída (espelha nos canais de saída)
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
        Inicia a transmissão contínua de áudio.
        """
        if self.is_running:
            return

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
        Interrompe a transmissão contínua de áudio e libera recursos.
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
        self._noise_profile = None
