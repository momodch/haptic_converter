# __main__.py
import sys
from .wav_to_haps import wav_to_haps

if __name__ == "__main__":
    print("Hello Wav to Haps 🖐️")
    if len(sys.argv) != 3:
        print("Usage : python -m haptic_converter <input.wav> <output.haps>")
    else:
        print("📁 Looking for " + sys.argv[1])
        print("⌛")
        wav_to_haps(sys.argv[1], sys.argv[2])

# TO DOs 
# pour les basses il faut faire un traitement pour éviter un buzz continue
# Pour les drums il faut cut à 0 plus haut ~1.3 peut-être (à testé)
## Il faut également vérifier qu'un transient est plus haut que la melody sinon ça se soustrait ? Peut-être que c'est juste dans le rendu graphique (qui sait)

## Faire un test FX pas lié au son mais au visuel (aucune idée d'automatisation de ça)