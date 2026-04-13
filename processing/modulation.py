# processing/modulation.py
from .audio_utils import compute_envelope, lowpass_filter, get_dominant_freq
import numpy as np

def generate_modulated_note(signal, sample_rate, step_duration=0.05):
    step_size = int(step_duration * sample_rate)
    total_samples = len(signal)
    total_time = total_samples / sample_rate
    amp_keys, freq_keys = [], []

    for i in range(0, total_samples - step_size, step_size):
        segment = signal[i:i + step_size]
        t = i / sample_rate
        amp = float(np.clip(np.sqrt(np.mean(segment**2)), 0.0, 1.0))
        dom_freq = get_dominant_freq(segment, sample_rate)

        if dom_freq < 100:
            vibr_freq = 30.0 + amp * 70.0
            amp *= 2.0
        elif dom_freq > 300:
            vibr_freq = 200.0 + amp * 100.0
            #vibr_freq = 65.0 + amp * 35.0

            amp *= 1.0
        else:
            vibr_freq = 100.0 + amp * 200.0 # À tester
            amp *= 1.5
            

        amp_keys.append({
            "m_inSlope": 0.0, "m_outSlope": 0.0,
            "m_time": t, "m_value": float(0.0 if amp< 0.09 else np.clip(amp, 0.0, 1.0))
        })
        freq_keys.append({
            "m_inSlope": 0.0, "m_outSlope": 0.0,
            "m_time": t, "m_value": float(np.clip(vibr_freq, 20.0, 300.0))
        })

    amp_keys = clean_keyframes(amp_keys)

    return [{
        "m_gain": 1.0,
        "m_hapticEffect": {
            "m_amplitudeModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": amp_keys
            },
            "m_frequencyModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": freq_keys
            }
        },
        "m_length": total_time,
        "m_priority": 1,
        "m_startingPoint": 0.0
    }]

def generate_modulated_note_highFreq(signal, sample_rate, step_duration=0.05):
    step_size = int(step_duration * sample_rate)
    total_samples = len(signal)
    total_time = total_samples / sample_rate
    amp_keys, freq_keys = [], []

    for i in range(0, total_samples - step_size, step_size):
        segment = signal[i:i + step_size]
        t = i / sample_rate
        amp = float(np.clip(np.sqrt(np.mean(segment**2)), 0.0, 1.0))
        dom_freq = get_dominant_freq(segment, sample_rate)

        if dom_freq < 100:
            vibr_freq = 65.0 + amp * 35.0
            amp *= 2
        elif dom_freq > 350:
            vibr_freq = 350 + amp * 1000.0
        else:
            vibr_freq = 100.0 + amp * 200.0
            amp *= 1.5

        amp_keys.append({
            "m_inSlope": 0.0, "m_outSlope": 0.0,
            "m_time": t, "m_value": float(0.0 if amp< 0.08 else np.clip(amp, 0.0, 1.0))
        })
        freq_keys.append({
            "m_inSlope": 0.0, "m_outSlope": 0.0,
            "m_time": t, "m_value": float(np.clip(vibr_freq, 20.0, 1000.0))
        })

    amp_keys = clean_keyframes(amp_keys)

    return [{
        "m_gain": 1.0,
        "m_hapticEffect": {
            "m_amplitudeModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": amp_keys
            },
            "m_frequencyModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": freq_keys
            }
        },
        "m_length": total_time,
        "m_priority": 1,
        "m_startingPoint": 0.0
    }]

def generate_bass_note(signal, sample_rate):
    bass = lowpass_filter(signal, sample_rate)
    return generate_modulated_note(bass, sample_rate)

def clean_keyframes(keyframes): # Possibilité de faire de la récursivité (on verra plus tard).
    if not keyframes:
        return []

    cleaned = []
    buffer = []

    for i, kf in enumerate(keyframes):
        value = kf.get("m_value", 0.0)

        if value == 0.0:
            buffer.append(kf)
        else:
            if buffer:
                # Garde la première et la dernière de la série
                cleaned.append(buffer[0])
                if len(buffer) > 1:
                    cleaned.append(buffer[-1])
                buffer.clear()
            cleaned.append(kf)

    # Cas : la série de zéros est à la fin
    if buffer:
        cleaned.append(buffer[0])
        if len(buffer) > 1:
            cleaned.append(buffer[-1])

    return cleaned

