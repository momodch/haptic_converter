import numpy as np
import scipy.io.wavfile as wav
import json
import sys
from scipy.fft import *
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
from matplotlib import pyplot as plt

def lowpass_filter(signal, sample_rate, cutoff=150.0, order=4):
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)

def generate_bass_vibration_note(data, sample_rate, step_duration=0.05):
    # Filtrer uniquement les basses fréquences
    bass_signal = lowpass_filter(data, sample_rate, cutoff=150.0)

    # Calculer l'enveloppe du signal basse fréquence
    envelope = compute_envelope(bass_signal, sample_rate, win_duration=step_duration)

    # Générer une note vibratoire longue comme pour la modulation complète
    return generate_single_long_modulated_note(envelope, sample_rate, step_duration)

def create_modulated_melody(data, sample_rate, duration=1.0, step_interval=2.5):
    melody = []
    total_time = len(data) / sample_rate
    t = 0.0
    while t + duration < total_time:
        start_index = int(t * sample_rate)
        end_index = int((t + duration) * sample_rate)
        segment = data[start_index:end_index]
        rms = np.sqrt(np.mean(segment ** 2))
        if rms > 0.05:
            note = create_modulated_note(t, duration, amp=float(np.clip(rms, 0.0, 1.0)))
            melody.append(note)
        t += step_interval
    return melody

def compute_envelope(signal, sample_rate, win_duration=0.01):
    win_size = int(win_duration * sample_rate)
    envelope = np.abs(signal)
    smoothed = np.convolve(envelope, np.ones(win_size)/win_size, mode='same')
    return smoothed

def generate_modulated_melody_from_envelope(envelope, sample_rate, duration=1.0, hop_duration=0.2):
    melody = []
    note_len = int(duration * sample_rate)
    hop_len = int(hop_duration * sample_rate)
    total_samples = len(envelope)

    for start in range(0, total_samples - note_len, hop_len):
        segment = envelope[start:start + note_len]
        if np.max(segment) < 0.05:  # skip silent regions
            continue
        
        time_start = start / sample_rate
        amp_keyframes = []
        freq_keyframes = []
        n_keyframes = 5  # for example
        step = len(segment) // n_keyframes

        for i in range(n_keyframes):
            idx = i * step
            t = (idx / sample_rate)
            amp_val = float(np.clip(segment[idx], 0.0, 1.0))
            freq_val = 65 + amp_val * 235  # freq: 65 Hz (low) to 300 Hz (high)

            amp_keyframes.append({
                "m_inSlope": 0.0, "m_outSlope": 0.0,
                "m_time": t,
                "m_value": amp_val
            })
            freq_keyframes.append({
                "m_inSlope": 0.0, "m_outSlope": 0.0,
                "m_time": t,
                "m_value": freq_val
            })

        note = {
            "m_gain": 1.0,
            "m_hapticEffect": {
                "m_amplitudeModulation": {
                    "m_extrapolationStrategy": 0,
                    "m_keyframes": amp_keyframes
                },
                "m_frequencyModulation": {
                    "m_extrapolationStrategy": 0,
                    "m_keyframes": freq_keyframes
                }
            },
            "m_length": duration,
            "m_priority": 1,
            "m_startingPoint": time_start
        }

        melody.append(note)

    return melody

def generate_single_long_modulated_note(envelope, sample_rate, step_duration=0.05): #0.01 très précis sinon lisse la courbe
    step_size = int(step_duration * sample_rate)
    amp_keyframes = []
    freq_keyframes = []
    total_samples = len(envelope)
    total_time = total_samples / sample_rate

    for i in range(0, total_samples, step_size):
        #idx = i
        time = i / sample_rate
        amp = float(np.clip(envelope[i], 0.0, 1.0))
        freq = 65.0 + amp * 235.0  # Range: 65Hz - 300Hz

        amp_keyframes.append({
            "m_inSlope": 0.0,
            "m_outSlope": 0.0,
            "m_time": time,
            "m_value": amp
        })

        freq_keyframes.append({
            "m_inSlope": 0.0,
            "m_outSlope": 0.0,
            "m_time": time,
            "m_value": freq
        })

    note = {
        "m_gain": 1.0,
        "m_hapticEffect": {
            "m_amplitudeModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": amp_keyframes
            },
            "m_frequencyModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": freq_keyframes
            }
        },
        "m_length": total_time,
        "m_priority": 1,
        "m_startingPoint": 0.0
    }

    return [note]


# 🎧


def wav_to_haps(wav_path, haps_path, threshold=0.1, note_duration=0.022):
    # Lecture du fichier WAV
    sample_rate, data = wav.read(wav_path)
    
    # Normalisation (entre -1.0 et 1.0)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128) / 128.0

    # Mono si stéréo
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Création des notes
    notes = []
    step = int(sample_rate * note_duration)
    for i in range(0, len(data), step):
        chunk = data[i:i+step]
        rms = np.sqrt(np.mean(chunk**2))
        if rms > threshold:
            time = i / sample_rate
            gain = float(np.clip(rms, 0.0, 1.0))
            note = {
                "m_gain": gain,
                "m_hapticEffect": {"m_type": 0},
                "m_length": note_duration,
                "m_priority": 0,
                "m_startingPoint": time
            }
            notes.append(note)

    # Structure HAPS
    haps = {
        "m_HDFlag": 0,
        "m_description": "",
        "m_gain": 1.0,
        "m_length_unit": 7,
        "m_stiffness": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_texture": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_time_unit": 0,
        "m_version": "5",
        "m_vibration": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [
                {
                    "m_gain": 1.0,
                    "m_mute": 0,
                    "m_notes": notes
                }
            ]
        }
    }

    # Calcul de l’enveloppe
    #envelope = compute_envelope(data, sample_rate)

    # Génération de la mélodie qui suit l’enveloppe
    #modulated_melody = generate_modulated_melody_from_envelope(envelope, sample_rate)

    # Ajout de la deuxième mélodie
    #haps["m_vibration"]["m_melodies"].append({
    #    "m_gain": 1.0,
    #    "m_mute": 0,
    #    "m_notes": modulated_melody
    #})

    envelope = compute_envelope(data, sample_rate)
    long_modulated_note = generate_single_long_modulated_note(envelope, sample_rate)

    haps["m_vibration"]["m_melodies"].append({
        "m_gain": 1.0,
        "m_mute": 0,
        "m_notes": long_modulated_note
    })




    # Sauvegarde au format .haps (JSON)
    with open(haps_path, 'w') as f:
        json.dump(haps, f, indent=4)

    print(f"Conversion réussie : {haps_path}")

def wav_to_haps_subwoofer(wav_path, haps_path, threshold=0.1, note_duration=0.022):
    # Lecture du fichier WAV
    sample_rate, data = wav.read(wav_path)
    
    # Normalisation (entre -1.0 et 1.0)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128) / 128.0

    # Mono si stéréo
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Création des notes
    notes = []
    step = int(sample_rate * note_duration)
    for i in range(0, len(data), step):
        chunk = data[i:i+step]
        rms = np.sqrt(np.mean(chunk**2))
        if rms > threshold:
            time = i / sample_rate
            gain = float(np.clip(rms, 0.0, 1.0))
            note = {
                "m_gain": gain,
                "m_hapticEffect": {"m_type": 0},
                "m_length": note_duration,
                "m_priority": 0,
                "m_startingPoint": time
            }
            notes.append(note)

    # Structure HAPS
    haps = {
        "m_HDFlag": 0,
        "m_description": "",
        "m_gain": 1.0,
        "m_length_unit": 7,
        "m_stiffness": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_texture": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_time_unit": 0,
        "m_version": "5",
        "m_vibration": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [
                {
                    "m_gain": 1.0,
                    "m_mute": 0,
                    "m_notes": notes
                }
            ]
        }
    }

    # Calcul de l’enveloppe
    #envelope = compute_envelope(data, sample_rate)

    # Génération de la mélodie qui suit l’enveloppe
    #modulated_melody = generate_modulated_melody_from_envelope(envelope, sample_rate)

    # Ajout de la deuxième mélodie
    #haps["m_vibration"]["m_melodies"].append({
    #    "m_gain": 1.0,
    #    "m_mute": 0,
    #    "m_notes": modulated_melody
    #})

    envelope = compute_envelope(data, sample_rate)
    long_modulated_note = generate_single_long_modulated_note(envelope, sample_rate)

    haps["m_vibration"]["m_melodies"].append({
        "m_gain": 1.0,
        "m_mute": 0,
        "m_notes": long_modulated_note
    })


    bass_note = generate_bass_vibration_note(data, sample_rate)

    haps["m_vibration"]["m_melodies"].append({
        "m_gain": 1.0,
        "m_mute": 0,
        "m_notes": bass_note
    })

    # Sauvegarde au format .haps (JSON)
    with open(haps_path, 'w') as f:
        json.dump(haps, f, indent=4)

    print(f"Conversion réussie : {haps_path}")

def create_modulated_note(start_time, duration, amp=1.0):
    return {
        "m_gain": 1.0,
        "m_hapticEffect": {
            "m_amplitudeModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": [
                    {"m_inSlope": 0.0, "m_outSlope": 0.0, "m_time": 0.0, "m_value": amp},
                    {"m_inSlope": 0.0, "m_outSlope": 0.0, "m_time": duration * 0.8, "m_value": amp * 0.5},
                    {"m_inSlope": 0.0, "m_outSlope": 0.0, "m_time": duration, "m_value": 0.0}
                ]
            },
            "m_frequencyModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": [
                    {"m_inSlope": 0.0, "m_outSlope": 0.0, "m_time": 0.0, "m_value": 300.0},
                    {"m_time": duration * 0.8, "m_value": 140.0},
                    {"m_inSlope": 0.0, "m_outSlope": 0.0, "m_time": duration, "m_value": 65.0}
                ]
            }
        },
        "m_length": duration,
        "m_priority": 1,
        "m_startingPoint": start_time
    }

## Version qui englobe toutes ces approches ensemble. 

def detect_transients(signal, sample_rate, threshold=0.1, min_gap=0.2):
    step = int(sample_rate * 0.01)
    envelope = compute_envelope(signal, sample_rate, win_duration=0.01)
    transients = []
    last_time = -min_gap

    for i in range(0, len(envelope), step):
        t = i / sample_rate
        if envelope[i] > threshold and (t - last_time) >= min_gap:
            note = {
                "m_gain": float(np.clip(envelope[i], 0.0, 1.0)),
                "m_hapticEffect": {"m_type": 0},
                "m_length": 0.022,
                "m_priority": 0,
                "m_startingPoint": t
            }
            transients.append(note)
            last_time = t

    return transients

def wav_to_haps_Global_Approach(wav_path, haps_path):
    sample_rate, data = wav.read(wav_path)

    # Normalisation
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128) / 128.0

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # 1. Transients principaux
    #transients = detect_transients(data, sample_rate, threshold=0.1, min_gap=0.3)
    #Testes
    #transients = detect_transients(data, sample_rate, threshold=0.35, min_gap=0.25)
    transients = detect_transients_from_Frequency(data, sample_rate, threshold=0.35, min_gap=0.25)

    ##To do si le transients correspond à un enveloppe[i] de fréquence faible alors j'augmente l'amplitude sinon je diminue l'amplitude.

    # 2. Enveloppe full band
    full_envelope = compute_envelope(data, sample_rate)
    #modulated_note = generate_single_long_modulated_note(full_envelope, sample_rate)
    modulated_note = generate_single_long_modulated_note_with_fft(data,sample_rate)

    # 3. Subwoofer (basses)
    #bass_signal = lowpass_filter(data, sample_rate, cutoff=150.0)
    #bass_envelope = compute_envelope(bass_signal, sample_rate)
    #bass_note = generate_single_long_modulated_note(bass_envelope, sample_rate)

    # Structure HAPS
    haps = {
        "m_HDFlag": 0,
        "m_description": "Generated from WAV",
        "m_gain": 1.0,
        "m_length_unit": 7,
        "m_stiffness": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_texture": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [],
            "m_signalEvaluationMethod": 3
        },
        "m_time_unit": 0,
        "m_version": "5",
        "m_vibration": {
            "m_gain": 1.0,
            "m_loop": 0,
            "m_maximum": 1.0,
            "m_melodies": [
                {
                    "m_gain": 1.0,
                    "m_mute": 0,
                    "m_notes": transients
                },
                {
                    "m_gain": 1.0,
                    "m_mute": 0,
                    "m_notes": modulated_note
                },
#                {
#                    "m_gain": 1.0,
#                    "m_mute": 0,
#                    "m_notes": bass_note
#                }
            ]
        }
    }

    with open(haps_path, 'w') as f:
        json.dump(haps, f, indent=4)

    print(f"[OK ✅] Fichier HAPS généré : {haps_path}")


def freq(file, start_step, end_step,sample_rate):

    # Open the file and convert to mono
    #sample_rate, data = wavfile.read(file)
    #if data.ndim > 1:
    #    data = data[:, 0]
    #else:
    #    pass

    # Return a slice of the data from start_time to end_time
    dataToRead = file[start_step : end_step + 1]

    # Fourier Transform
    N = len(dataToRead)
    yf = rfft(dataToRead)
    xf = rfftfreq(N, 1 / sample_rate)

    # Uncomment these to see the frequency spectrum as a plot
    #plt.plot(xf, np.abs(yf))
    #plt.show()

    # Get the most dominant frequency and return it
    idx = np.argmax(np.abs(yf))
    freq = xf[idx]
    return freq

def detect_transients_from_Frequency(signal, sample_rate, threshold=0.1, min_gap=0.2):
    step = int(sample_rate * 0.01)
    envelope = compute_envelope(signal, sample_rate, win_duration=0.01)
    transients = []
    last_time = -min_gap

    for i in range(0, len(envelope), step):
        t = i / sample_rate
        if envelope[i] > threshold and (t - last_time) >= min_gap:
            if freq(signal, i-5, i,sample_rate) > 350:
                note = {
                    "m_gain": float(np.clip(envelope[i]*0.5, 0.0, 1.0)),
                    "m_hapticEffect": {"m_type": 0},
                    "m_length": 0.022,
                    "m_priority": 0,
                    "m_startingPoint": t
                }
            if freq(signal, i-5, i,sample_rate) < 100: # En HZ normalement
                note = {
                    "m_gain": float(np.clip(envelope[i]*2, 0.0, 1.0)),
                    "m_hapticEffect": {"m_type": 0},
                    "m_length": 0.022,
                    "m_priority": 0,
                    "m_startingPoint": t
                }
            else :
                note = {
                    "m_gain": float(np.clip(envelope[i]*1.25, 0.0, 1.0)),
                    "m_hapticEffect": {"m_type": 0},
                    "m_length": 0.022,
                    "m_priority": 0,
                    "m_startingPoint": t
                }
            transients.append(note)
            last_time = t

    return transients

def get_dominant_freq(signal, sample_rate):
    N = len(signal)
    if N < 2:
        return 0.0
    yf = rfft(signal)
    xf = rfftfreq(N, 1 / sample_rate)
    idx = np.argmax(np.abs(yf))
    return xf[idx]

def generate_single_long_modulated_note_with_fft(signal, sample_rate, step_duration=0.05):
    step_size = int(step_duration * sample_rate)
    total_samples = len(signal)
    total_time = total_samples / sample_rate
    amp_keyframes = []
    freq_keyframes = []

    for i in range(0, total_samples - step_size, step_size):
        segment = signal[i:i + step_size]
        t = i / sample_rate
        amp = float(np.clip(np.sqrt(np.mean(segment**2)), 0.0, 1.0))  # ou enveloppe directe

        # Mesure de fréquence dominante
        dom_freq = get_dominant_freq(segment, sample_rate)

        # Mapping : fréquence dominante → fréquence vibratoire haptique
        # Ici, on mappe les graves entre 65 et 300 Hz
        if dom_freq < 100:
            vibr_freq = 65.0 + amp * 35.0    # accentue basses
            amp *= 2.0
        elif dom_freq > 350:
            vibr_freq = 200.0 + amp * 100.0  # fréquences plus aigües
            amp *= 0.5
        else:
            vibr_freq = 100.0 + amp * 200.0

        amp_keyframes.append({
            "m_inSlope": 0.0,
            "m_outSlope": 0.0,
            "m_time": t,
            "m_value": float(np.clip(amp, 0.0, 1.0))
        })

        freq_keyframes.append({
            "m_inSlope": 0.0,
            "m_outSlope": 0.0,
            "m_time": t,
            "m_value": float(np.clip(vibr_freq, 20.0, 300.0))
        })

    return [{
        "m_gain": 1.0,
        "m_hapticEffect": {
            "m_amplitudeModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": amp_keyframes
            },
            "m_frequencyModulation": {
                "m_extrapolationStrategy": 0,
                "m_keyframes": freq_keyframes
            }
        },
        "m_length": total_time,
        "m_priority": 1,
        "m_startingPoint": 0.0
    }]

# Exemple d'utilisation
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Utilisation : python wav_to_haps.py input.wav output.haps")
    else:
        #print("🎵 Generate melody from envelope :\r\n")
        #wav_to_haps(sys.argv[1], sys.argv[2])
        #print("Generate Subwoofer version 🎧:\r\n")
        #wav_to_haps_subwoofer(sys.argv[1], "subwoofer_"+sys.argv[2])
        print("🎵 Generate melody from envelope:\r\n")
        wav_to_haps_Global_Approach(sys.argv[1],sys.argv[2])
        #print("Get main frequency:")
        #print(freq(sys.argv[1], 0, 1000))
        print("☑️  End program")
