import os
import numpy as np
import soundfile as sf
import noisereduce as nr
from typing import Tuple, Optional
from vocalis.core.filters import AudioFilters


class AudioFileProcessor:
    """
    Processador de áudio para arquivos estáticos e gravações completas.
    """

    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """
        Carrega um arquivo de áudio e converte para float32 e canal mono.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        data, sr = sf.read(file_path, dtype='float32')
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        return data, sr

    @staticmethod
    def save_audio(file_path: str, data: np.ndarray, sample_rate: int) -> None:
        """
        Salva um array de áudio no disco.
        """
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        sf.write(file_path, data, sample_rate)

    @classmethod
    def clean_audio_data(
        cls,
        audio_mono: np.ndarray,
        sample_rate: int,
        prop_decrease: float = 1.0,
        apply_highpass: bool = True,
        apply_gate: bool = True,
        gate_threshold_db: float = -42.0
    ) -> np.ndarray:
        """
        Executa a cadeia de redução de ruído (High-Pass + Spectral Denoise + Noise Gate).
        """
        if audio_mono.size == 0:
            return audio_mono

        data = audio_mono.copy()

        # 1. Filtro passa-alta para remover subgraves indesejados
        if apply_highpass:
            data = AudioFilters.butter_highpass_filter(data, cutoff_hz=80.0, sample_rate=sample_rate)

        # 2. Redução de ruído espectral por IA (noisereduce)
        data = nr.reduce_noise(
            y=data,
            sr=sample_rate,
            prop_decrease=prop_decrease,
            stationary=True
        )

        # 3. Noise Gate para silêncio completo nos intervalos de fala
        if apply_gate:
            data = AudioFilters.apply_noise_gate(data, threshold_db=gate_threshold_db, sample_rate=sample_rate)

        # 4. Normalização suave para evitar clipping
        max_val = np.max(np.abs(data))
        if max_val > 0.98:
            data = data / max_val * 0.95

        return data.astype(np.float32)

    @classmethod
    def clean_file(
        cls,
        input_path: str,
        output_path: str,
        prop_decrease: float = 1.0,
        apply_highpass: bool = True,
        apply_gate: bool = True,
        gate_threshold_db: float = -42.0
    ) -> Tuple[str, float]:
        """
        Limpa um arquivo de entrada e salva no destino.
        Retorna o caminho do arquivo gerado e a duração em segundos.
        """
        data, sr = cls.load_audio(input_path)
        cleaned = cls.clean_audio_data(
            data,
            sr,
            prop_decrease=prop_decrease,
            apply_highpass=apply_highpass,
            apply_gate=apply_gate,
            gate_threshold_db=gate_threshold_db
        )
        cls.save_audio(output_path, cleaned, sr)
        duration = len(cleaned) / float(sr)
        return output_path, duration
