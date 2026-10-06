"""Synthétise les bruitages du jeu (aucun échantillon tiers) dans src/loup_garou/assets/sons/.

Usage : uv run --python 3.12 --with numpy python outils/generer_sons.py
"""

import wave
from pathlib import Path

import numpy as np

SR = 16000
DOSSIER = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets" / "sons"
rng = np.random.default_rng(7)


def temps(duree):
    return np.arange(int(SR * duree)) / SR


def ecrire(nom, signal, crete=0.6, fondu=0.4):
    """`fondu` : durée (s) du fondu de sortie ; 0 pour un son destiné à boucler."""
    signal = signal / (np.max(np.abs(signal)) or 1) * crete
    if fondu:
        n = int(SR * fondu)
        signal[-n:] *= np.linspace(1, 0, n)
    DOSSIER.mkdir(parents=True, exist_ok=True)
    with wave.open(str(DOSSIER / f"{nom}.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((signal * 32767).astype("<i2").tobytes())


def bruit_filtre(duree, bas, haut):
    """Bruit passe-bande construit par FFT : périodique, donc bouclable sans raccord."""
    n = int(SR * duree)
    spectre = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spectre[(f < bas) | (f > haut)] = 0
    return np.fft.irfft(spectre, n)


def cloche(t, f0, duree, force=1.0):
    """Cloche : partiels inharmoniques à décroissance exponentielle."""
    signal = np.zeros_like(t)
    for rang, (rapport, gain, tau) in enumerate(((1, 1, 1.4), (2.0, .6, 1.0), (2.76, .5, .8), (5.4, .25, .45), (8.93, .12, .3))):
        signal += gain * np.sin(2 * np.pi * f0 * rapport * t) * np.exp(-t / (tau * duree / 2))
    attaque = np.minimum(t / 0.004, 1)
    return force * signal * attaque


def decale(signal, debut, total):
    sortie = np.zeros(int(SR * total))
    i = int(SR * debut)
    morceau = signal[: len(sortie) - i]
    sortie[i:i + len(morceau)] += morceau
    return sortie


def nuit():
    d = 8.0
    t = temps(d)
    bourdon = (np.sin(2 * np.pi * 55 * t) + .6 * np.sin(2 * np.pi * 82.5 * t) + .3 * np.sin(2 * np.pi * 110 * t)) * (1 + .25 * np.sin(2 * np.pi * t / d))
    vent = bruit_filtre(d, 150, 900) * (.55 + .45 * np.sin(2 * np.pi * 2 * t / d + 1))
    vent /= np.max(np.abs(vent))
    grillons = np.sin(2 * np.pi * 4200 * t) * (np.sin(2 * np.pi * 6 * t) > .2) * (np.sin(2 * np.pi * 0.5 * t) > .1)
    ecrire("nuit", .5 * bourdon / 1.9 + .55 * vent + .05 * grillons, crete=.5, fondu=0)


def jour():
    d = 4.5
    t = temps(d)
    signal = np.zeros_like(t)
    for debut, f0, force in ((0.0, 523.25, 1), (0.25, 659.25, .9), (0.5, 783.99, .8)):
        signal += decale(cloche(temps(d - debut), f0, 2.2, force), debut, d)
    for debut in (1.4, 1.9, 2.15, 2.9, 3.2, 3.45):
        tt = temps(.14)
        base = rng.uniform(2300, 2900)
        chant = np.sin(2 * np.pi * (base * tt + 6500 * tt ** 2)) * np.sin(np.pi * tt / .14)
        signal += .22 * decale(chant, debut, d)
    ecrire("jour", signal, crete=.55)


def mort():
    d = 3.8
    t = temps(d)
    signal = cloche(t, 174.6, 3.0) + .8 * decale(cloche(temps(d - 1.7), 174.6, 3.0), 1.7, d)
    signal += .8 * np.sin(2 * np.pi * 58 * t) * np.exp(-t / .35)
    ecrire("mort", signal, crete=.6)


def victoire_village():
    d = 4.2
    signal = np.zeros(int(SR * d))
    for i, f in enumerate((392, 523.25, 659.25, 783.99, 1046.5)):
        tt = temps(d - i * .16)
        note = sum(g * np.sin(2 * np.pi * f * k * tt) for k, g in ((1, 1), (2, .4), (3, .15))) * np.exp(-tt / .9)
        signal += decale(note, i * .16, d)
    accord = sum(np.sin(2 * np.pi * f * temps(d - .8)) for f in (523.25, 659.25, 783.99)) * np.exp(-temps(d - .8) / 1.2) * np.minimum(temps(d - .8) / .1, 1)
    signal += .5 * decale(accord, .8, d)
    ecrire("victoire_village", signal, crete=.55)


def victoire_loups():
    d = 6.0
    t = temps(d)
    progression = np.interp(t, [0, 1.6, 3.2, 5.2], [260, 640, 600, 380])
    vibrato = 14 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 1) / 1.5, 0, 1)
    phase = 2 * np.pi * np.cumsum(progression + vibrato) / SR
    hurlement = np.sin(phase) + .45 * np.sin(2 * phase) + .2 * np.sin(3 * phase)
    enveloppe = np.interp(t, [0, .5, 1.6, 4.4, 5.4, 6], [0, .7, 1, .8, .25, 0])
    fond = (np.sin(2 * np.pi * 110 * t) + .8 * np.sin(2 * np.pi * 130.8 * t)) * .25 + .5 * bruit_filtre(d, 150, 700) / 4
    ecrire("victoire_loups", hurlement * enveloppe + fond * np.minimum(t / .8, 1) * np.minimum((d - t) / .8, 1), crete=.55)


if __name__ == "__main__":
    for fabrique in (nuit, jour, mort, victoire_village, victoire_loups):
        fabrique()
    print("sons écrits dans", DOSSIER)
