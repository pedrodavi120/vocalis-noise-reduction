import numpy as np
from scipy import signal


class AudioFilters:
    """
    Filtros acústicos e utilitários de sinal em tempo real e offline.
    """

    @staticmethod
    def butter_highpass_filter(data: np.ndarray, cutoff_hz: float = 80.0, sample_rate: int = 44100, order: int = 2) -> np.ndarray:
        """
        Filtro passa-alta Butterworth para eliminar ruídos graves subsônicos (hum elétrico e plosivas).
        """
        nyquist = 0.5 * sample_rate
        normal_cutoff = cutoff_hz / nyquist
        if normal_cutoff >= 1.0:
            return data
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        if data.size == 0:
            return data
        # Para evitar erros com áudios curtos
        padlen = min(15, len(data) - 1) if len(data) > 15 else 0
        if padlen > 0:
            return signal.filtfilt(b, a, data, padlen=padlen).astype(np.float32)
        return signal.lfilter(b, a, data).astype(np.float32)

    @staticmethod
    def apply_noise_gate(data: np.ndarray, threshold_db: float = -42.0, attack_ms: float = 5.0, release_ms: float = 80.0, sample_rate: int = 44100) -> np.ndarray:
        """
        Noise Gate adaptativo para silenciar fundo quando o usuário não estiver falando.
        """
        if data.size == 0:
            return data

        threshold_amp = 10.0 ** (threshold_db / 20.0)
        attack_samples = max(1, int(attack_ms * sample_rate / 1000.0))
        release_samples = max(1, int(release_ms * sample_rate / 1000.0))

        attack_coeff = np.exp(-1.0 / attack_samples)
        release_coeff = np.exp(-1.0 / release_samples)

        gain = np.zeros_like(data, dtype=np.float32)
        current_gain = 0.0

        abs_data = np.abs(data)
        for i in range(len(data)):
            target_gain = 1.0 if abs_data[i] >= threshold_amp else 0.0
            if target_gain > current_gain:
                current_gain = (1.0 - attack_coeff) * target_gain + attack_coeff * current_gain
            else:
                current_gain = (1.0 - release_coeff) * target_gain + release_coeff * current_gain
            gain[i] = current_gain

        return (data * gain).astype(np.float32)

    @staticmethod
    def calculate_rms_db(data: np.ndarray) -> float:
        """
        Calcula a potência média RMS do sinal em decibéis (dBFS).
        """
        if data.size == 0:
            return -100.0
        rms = np.sqrt(np.mean(np.square(data)))
        if rms < 1e-6:
            return -100.0
        return float(20.0 * np.log10(rms))
