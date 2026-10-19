import os
import numpy as np
import pytest
from vocalis.core.file_processor import AudioFileProcessor


def test_file_processor_clean_audio_data(tmp_path):
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Cria áudio de teste com voz (440Hz) + ruído branco
    clean_tone = 0.3 * np.sin(2 * np.pi * 440 * t)
    noise = 0.05 * np.random.normal(0, 1, len(t))
    noisy_audio = (clean_tone + noise).astype(np.float32)

    cleaned = AudioFileProcessor.clean_audio_data(
        noisy_audio,
        sample_rate=sample_rate,
        prop_decrease=0.9,
        apply_highpass=True,
        apply_gate=True
    )

    assert len(cleaned) == len(noisy_audio)
    assert isinstance(cleaned, np.ndarray)
    assert not np.isnan(cleaned).any()

    # Salva e recarrega
    test_file = str(tmp_path / "test_out.wav")
    AudioFileProcessor.save_audio(test_file, cleaned, sample_rate)
    assert os.path.exists(test_file)

    loaded, sr = AudioFileProcessor.load_audio(test_file)
    assert sr == sample_rate
    assert len(loaded) == len(cleaned)
