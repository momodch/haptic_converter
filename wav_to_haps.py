# wav_to_haps.py
from .processing.audio_utils import read_wav
from .processing.transients import detect_transients
from .processing.modulation import generate_modulated_note, generate_bass_note,generate_modulated_note_highFreq
from .presets.haps_template import get_base_haps_structure
import json

def wav_to_haps(wav_path, haps_path):
    sample_rate, data = read_wav(wav_path)

    haps = get_base_haps_structure()

    # 1. Transients adaptatifs
    print("Generating transients 📊")
    transients = detect_transients(data, sample_rate)
    print("Transients done 👍")
    # 2. Mélodie modulée (full band avec FFT)
    print("Generating Melody 🎵")
    #modulated_note = generate_modulated_note(data, sample_rate,step_duration=0.2)
    modulated_note = generate_modulated_note_highFreq(data, sample_rate,step_duration=0.05)
    print("Melody done 👍")
    # 3. Subwoofer
    #bass_note = generate_bass_note(data, sample_rate)

    haps["m_vibration"]["m_melodies"].extend([
        {"m_gain": 1.0, "m_mute": 0, "m_notes": transients},
        {"m_gain": 1.0, "m_mute": 0, "m_notes": modulated_note},
        #{"m_gain": 1.0, "m_mute": 0, "m_notes": bass_note}
    ])

    with open(haps_path, 'w') as f:
        json.dump(haps, f, indent=4)

    print(f"✅ Fichier HAPS généré : {haps_path}")


## TO DO: méthode qui permet d'assembler plusieurs haps ensemble pour n'a voir qu'une seule piste haptique lorsque qu'on veut associer plusieurs court effets ensemble sur une longue track. 
