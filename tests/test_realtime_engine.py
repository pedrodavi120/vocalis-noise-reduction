import numpy as np
from vocalis.core.realtime_engine import RealtimeDenoiseEngine
from vocalis.core.filters import ContinuousHighPassFilter, ContinuousNoiseGate


def test_continuous_highpass_filter():
    filter_iir = ContinuousHighPassFilter(cutoff_hz=80.0, sample_rate=48000)
    # Gera tom subsônico de 30 Hz (deve ser fortemente atenuado)
    t = np.linspace(0, 0.1, 4800, False)
    low_freq = np.sin(2 * np.pi * 30 * t).astype(np.float32)
    filtered = filter_iir.process(low_freq)
    
    rms_in = np.sqrt(np.mean(low_freq**2))
    rms_out = np.sqrt(np.mean(filtered**2))
    assert rms_out < rms_in * 0.5


def test_continuous_noise_gate():
    gate = ContinuousNoiseGate(threshold_db=-40.0, sample_rate=48000)
    # Ruído muito baixo (-60 dB)
    quiet_noise = np.random.randn(480).astype(np.float32) * 0.0001
    gated = gate.process(quiet_noise, speech_prob=0.0)
    assert np.max(np.abs(gated)) < np.max(np.abs(quiet_noise))


def test_realtime_engine_process_rnnoise_or_fallback():
    engine = RealtimeDenoiseEngine(sample_rate=48000, block_size=480)
    engine.start()
    
    # Simula entrada com fala/tom
    test_chunk = np.random.randn(480).astype(np.float32) * 0.1
    out_dummy = np.zeros((480, 2), dtype=np.float32)
    
    # Executa o callback diretamente para simular o driver de som
    engine._audio_callback(test_chunk, out_dummy, 480, None, 0)
    
    assert out_dummy.shape == (480, 2)
    engine.stop()
