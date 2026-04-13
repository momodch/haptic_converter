# presets/haps_template.py
def get_base_haps_structure():
    return {
        "m_HDFlag": 0,
        "m_description": "Generated from WAV",
        "m_gain": 1.0,
        "m_length_unit": 7,
        "m_stiffness": {
            "m_gain": 1.0, "m_loop": 0, "m_maximum": 1.0,
            "m_melodies": [], "m_signalEvaluationMethod": 3
        },
        "m_texture": {
            "m_gain": 1.0, "m_loop": 0, "m_maximum": 1.0,
            "m_melodies": [], "m_signalEvaluationMethod": 3
        },
        "m_time_unit": 0,
        "m_version": "5",
        "m_vibration": {
            "m_gain": 1.0, "m_loop": 0, "m_maximum": 1.0,
            "m_melodies": []
        }
    }
