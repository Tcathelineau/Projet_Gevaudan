"""Synthétise les bruitages du jeu (hurlement, victoires ; aucun échantillon tiers) dans src/loup_garou/assets/sons/.

Usage : uv run --python 3.12 --with numpy python outils/generer_sons.py
Les musiques, elles, viennent de morceaux libres de droits : voir outils/importer_musiques.py.
"""

import wave
from pathlib import Path

import numpy as np

SR = 22050
DOSSIER = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets" / "sons"
rng = np.random.default_rng(2026)


# --- outils de synthèse -----------------------------------------------------------------------

def hz(midi):
    return 440.0 * 2 ** ((np.asarray(midi, dtype=float) - 69) / 12)


def temps(duree):
    return np.arange(int(SR * duree)) / SR


def enveloppe(n, attaque, relache, decroissance=None):
    t = np.arange(n) / SR
    e = np.minimum(t / max(attaque, 1e-4), 1.0)
    e = e * np.minimum((n / SR - t) / max(relache, 1e-4), 1.0)
    if decroissance:
        e = e * np.exp(-t / decroissance)
    return np.clip(e, 0, 1)


def harmoniques(f, t, partiels):
    """Somme de partiels (rapport, gain), coupée sous Nyquist."""
    s = np.zeros_like(t)
    for rapport, gain in partiels:
        if f * rapport < SR / 2 - 200:
            s += gain * np.sin(2 * np.pi * f * rapport * t)
    return s


SCIE = tuple((k, 1 / k) for k in range(1, 9))
CARRE = tuple((k, 1 / k) for k in range(1, 12, 2))
CLOCHE = ((1, 1), (2.756, .35), (5.404, .15), (8.93, .06))
FLUTE = ((1, 1), (2, .25), (3, .08))


def note(f, duree, partiels, attaque=.01, relache=.05, decroissance=None, desaccord=0.0):
    t = temps(duree)
    s = harmoniques(f, t, partiels)
    if desaccord:
        s = .5 * s + .5 * harmoniques(f * (1 + desaccord), t, partiels)
    return s * enveloppe(len(t), attaque, relache, decroissance)


def poser(piste, signal, debut, gain=1.0):
    i = int(debut * SR)
    if i >= len(piste):
        return
    morceau = signal[: len(piste) - i]
    piste[i:i + len(morceau)] += gain * morceau


def bruit_filtre(duree, bas, haut):
    n = int(SR * duree)
    spectre = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spectre[(f < bas) | (f > haut)] = 0
    s = np.fft.irfft(spectre, n)
    return s / (np.max(np.abs(s)) or 1)


def reverb(x, queue=1.8, mix=.25):
    t = temps(queue)
    ir = rng.standard_normal(len(t)) * np.exp(-t / (queue / 4))
    n = len(x) + len(ir)
    taille = 1 << (n - 1).bit_length()
    humide = np.fft.irfft(np.fft.rfft(x, taille) * np.fft.rfft(ir, taille), taille)[: len(x)]
    humide *= np.max(np.abs(x)) / (np.max(np.abs(humide)) or 1)
    return (1 - mix) * x + mix * humide


def echo(x, delai=.45, retour=.4, repetitions=4):
    sortie = x.copy()
    for k in range(1, repetitions + 1):
        poser(sortie, x, k * delai, retour ** k)
    return sortie


def grosse_caisse(force=1.0, duree=.35):
    t = temps(duree)
    return force * np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t / .03)) / SR) * np.exp(-t / .12)


def impact_bruit(duree, bas, haut, decroissance):
    return bruit_filtre(duree, bas, haut) * np.exp(-temps(duree) / decroissance)


def ecrire(nom, signal, crete=.6, fondu=.4):
    signal = np.nan_to_num(signal)
    signal = signal / (np.max(np.abs(signal)) or 1) * crete
    if fondu:
        n = int(SR * fondu)
        signal[-n:] *= np.linspace(1, 0, n)
        signal[:n // 4] *= np.linspace(0, 1, n // 4)
    pcm = (signal * 32767).astype("<i2")
    DOSSIER.mkdir(parents=True, exist_ok=True)
    with wave.open(str(DOSSIER / f"{nom}.wav"), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes(pcm.tobytes())


# --- bruitages -----------------------------------------------------------------------------------

def hurlement_seul(duree, grave, aigu, vibrato=14):
    t = temps(duree)
    hauteur = np.interp(t, [0, duree * .3, duree * .55, duree], [grave, aigu, aigu * .96, grave * 1.3])
    vib = vibrato * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - duree * .25) / (duree * .2), 0, 1)
    phase = 2 * np.pi * np.cumsum(hauteur + vib) / SR
    voix = np.sin(phase) + .5 * np.sin(2 * phase) + .22 * np.sin(3 * phase)
    souffle = .12 * bruit_filtre(duree, 600, 3000)
    env = np.interp(t, [0, duree * .12, duree * .5, duree * .85, duree], [0, .8, 1, .55, 0])
    return (voix + souffle) * env


def hurlement():
    return reverb(hurlement_seul(3.8, 300, 640), 1.6, .3)


def victoire_loups():
    d = 7.0
    sortie = np.zeros(int(SR * d))
    for debut, grave, aigu in ((0, 260, 560), (.7, 330, 700), (1.4, 220, 480)):
        poser(sortie, hurlement_seul(5.0, grave, aigu), debut, .6)
    t = temps(d)
    sortie += .12 * (np.sin(2 * np.pi * 110 * t) + .8 * np.sin(2 * np.pi * 130.8 * t))
    sortie += .08 * bruit_filtre(d, 150, 700)
    return reverb(sortie, 2.0, .3)


def victoire_village():
    d = 6.0
    sortie = np.zeros(int(SR * d))
    for i, m in enumerate((67, 72, 76, 79, 84)):
        poser(sortie, note(hz(m), 1.4, SCIE, attaque=.01, relache=.4, decroissance=.5), i * .17, .35)
    for m in (72, 76, 79):
        poser(sortie, note(hz(m), 3.0, SCIE, attaque=.02, relache=1.2), .9, .22)
        poser(sortie, note(hz(m + 12), 2.4, CLOCHE, attaque=.003, relache=.8, decroissance=.9), .9, .3)
    applaudissements = np.zeros_like(sortie)
    for _ in range(420):
        debut = float(np.clip(rng.normal(3.0, 1.1), .6, 5.6))
        poser(applaudissements, impact_bruit(.035, 1200, 7000, .01), debut, rng.uniform(.2, .7))
    sortie += .7 * applaudissements
    return reverb(sortie, 1.4, .2)


if __name__ == "__main__":
    ecrire("hurlement", hurlement(), crete=.7, fondu=.5)
    ecrire("victoire_village", victoire_village(), crete=.7, fondu=.8)
    ecrire("victoire_loups", victoire_loups(), crete=.7, fondu=1.0)
    print("sons écrits dans", DOSSIER)
