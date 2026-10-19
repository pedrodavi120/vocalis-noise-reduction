import numpy as np
import pytest
from vocalis.core.filters import AudioFilters


def test_highpass_filter_attenuates_low_frequencies():
    sample_rate = 44100
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)

    # 30 Hz (grave subsônico / hum elétrico)
    sig_low = np.sin(2 * np.pi * 30 * t)
    # 1000 Hz (frequência de voz clara)
    sig_high = np.sin(2 * np.pi * 1000 * t)

    filtered_low = AudioFilters.butter_highpass_filter(sig_low, cutoff_hz=80.0, sample_rate=sample_rate)
    filtered_high = AudioFilters.butter_highpass_filter(sig_high, cutoff_hz=80.0, sample_rate=sample_rate)

    rms_low_orig = np.sqrt(np.mean(sig_low**2))
    rms_low_filt = np.sqrt(np.mean(filtered_low**2))

    rms_high_orig = np.sqrt(np.mean(sig_high**2))
    rms_high_filt = np.sqrt(np.mean(filtered_high**2))

    # O sinal de 30Hz deve ser drasticamente atenuado
    assert rms_low_filt < (rms_low_orig * 0.4)
    # O sinal de 1000Hz deve ser preservado quase integralmente
    assert abs(rms_high_filt - rms_high_orig) < 0.05


def test_noise_gate_mutes_low_energy_noise():
    sample_rate = 44100
    # Ruído muito baixo (-50 dBFS aproximadamente)
    noise = np.random.uniform(-0.003, 0.003, sample_rate).astype(np.float32)
    # Sinal de voz (+10 dB em relação ao ruído)
    voice = np.sin(np.linspace(0, 100, sample_rate)) * 0.5

    gated_noise = AudioFilters.apply_noise_gate(noise, threshold_db=-40.0, sample_rate=sample_rate)
    gated_voice = AudioFilters.apply_noise_gate(voice, threshold_db=-40.0, sample_rate=sample_rate)

    # O ruído deve ser atenuado a praticamente 0
    assert np.max(np.abs(gated_noise)) < 0.001
    # A voz deve passar com energia substancial
    assert np.max(np.abs(gated_voice)) > 0.4


def test_calculate_rms_db():
    zeros = np.zeros(1000, dtype=np.float32)
    assert AudioFilters.calculate_rms_db(zeros) == -100.0

    sine = np.sin(np.linspace(0, 10, 1000, dtype=np.float32))
    db = AudioFilters.calculate_rms_db(sine)
    assert -5.0 < db < 0.0
