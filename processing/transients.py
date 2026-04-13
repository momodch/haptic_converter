# processing/transients.py
from .audio_utils import compute_envelope, get_dominant_freq
import numpy as np

def detect_transients(signal, sample_rate, threshold=0.1, min_gap=0.3):
    step = int(sample_rate * 0.01)
    envelope = compute_envelope(signal, sample_rate)
    transients = []
    last_time = -min_gap

    for i in range(0, len(envelope), step):
        t = i / sample_rate
        if envelope[i] > threshold and (t - last_time) >= min_gap:
            dom_freq = get_dominant_freq(signal[max(0, i-5):i+1], sample_rate)
            gain = envelope[i]
            if dom_freq < 100:
                gain *= 2.0
            elif dom_freq > 350:
                gain *= 0.0
            else:
                gain *= 0.4

            transients.append({
                "m_gain": float(np.clip(gain, 0.0, 1.0)),
                "m_hapticEffect": {"m_type": 0},
                "m_length": 0.022,
                "m_priority": 0,
                "m_startingPoint": t
            })
            last_time = t

    return transients
