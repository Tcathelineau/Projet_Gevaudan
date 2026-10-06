"""Télécharge les trois musiques du jeu (domaine public, CC0) et les prépare pour l'app.

Source : FreePD (https://freepd.com, musique en domaine public CC0), via le miroir GitHub 0lhi/FreePD.
Chaque piste est convertie en mono 22 kHz, ramenée à un volume commun, fondue en entrée et en sortie,
puis encodée en MP3 64 kbit/s dans src/loup_garou/assets/sons/.

Usage : uv run --python 3.12 --with numpy --with lameenc python outils/importer_musiques.py
Nécessite `afconvert` (macOS) ou `ffmpeg` pour décoder les MP3 d'origine.
"""

import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import lameenc
import numpy as np

SR = 22050
URL = "https://raw.githubusercontent.com/0lhi/FreePD/HEAD/{chemin}"
DOSSIER = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets" / "sons"

# fichier de sortie -> (chemin dans FreePD, titre)
PISTES = {
    "musique_nuit": ("Horror/Creepy Hallow.mp3", "Creepy Hallow"),
    "musique_jour": ("Upbeat/Happy Whistling Ukulele.mp3", "Happy Whistling Ukulele"),
    "musique_conseil": ("Scoring/Find Them.mp3", "Find Them"),
}
VOLUME_CIBLE = 0.12  # niveau efficace commun
FONDU = 1.5


def decoder(source, cible):
    if shutil.which("afconvert"):
        cmd = ["afconvert", str(source), str(cible), "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1"]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-ac", "1", "-ar", str(SR), str(cible)]
    subprocess.run(cmd, check=True)


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for nom, (chemin, titre) in PISTES.items():
            mp3, wav = Path(tmp) / "src.mp3", Path(tmp) / "src.wav"
            urllib.request.urlretrieve(URL.format(chemin=urllib.parse.quote(chemin)), mp3)
            decoder(mp3, wav)
            with wave.open(str(wav)) as f:
                x = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(float) / 32768
            x *= VOLUME_CIBLE / np.sqrt((x ** 2).mean())
            x = np.clip(x, -0.95, 0.95)
            n = int(SR * FONDU)
            x[:n] *= np.linspace(0, 1, n)
            x[-n:] *= np.linspace(1, 0, n)
            enc = lameenc.Encoder()
            enc.set_bit_rate(64)
            enc.set_in_sample_rate(SR)
            enc.set_channels(1)
            enc.set_quality(2)
            (DOSSIER / f"{nom}.mp3").write_bytes(enc.encode((x * 32767).astype("<i2").tobytes()) + enc.flush())
            print(f"{nom}: « {titre} » ({len(x) / SR:.0f} s)")


if __name__ == "__main__":
    main()
