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

def voyelle(f, formants):
    """Enveloppe spectrale d'une voyelle : somme de bosses (centre, largeur, gain) autour des formants."""
    f = np.asarray(f, dtype=float)
    return .02 + sum(g * np.exp(-((f - c) / w) ** 2) for c, w, g in formants)


OU = ((430, 190, 1.0), (880, 260, .55), (2200, 600, .12))      # « ouou » du hurlement
A = ((730, 200, 1.0), (1220, 260, .7), (2600, 500, .2))         # « a » d'une acclamation


def bruit_lisse(n, frequence):
    """Variation lente aléatoire (autour de 0, amplitude ~1), pour les micro-variations de hauteur."""
    pas = max(int(SR / frequence), 1)
    points = rng.standard_normal(n // pas + 2)
    return np.interp(np.arange(n), np.arange(len(points)) * pas, points)


def voix(f0, formants, harmoniques_max=28, pente=.7):
    """Voix chantée : harmoniques de la hauteur `f0` (une valeur par échantillon) pondérées par la voyelle."""
    phase = 2 * np.pi * np.cumsum(f0) / SR
    signal = np.zeros_like(f0)
    for k in range(1, harmoniques_max + 1):
        fk = k * f0
        poids = voyelle(fk, formants) / k ** pente * (fk < SR / 2 - 400)
        signal += poids * np.sin(k * phase)
    return signal


def hurlement_seul(duree, grave, aigu, souffle=.1):
    """Un loup qui hurle : montée lente vers la note haute, vibrato tardif, hauteur vivante, retombée plaintive."""
    n = int(SR * duree)
    t = np.arange(n) / SR
    d = duree
    contour = np.interp(t, [0, .05 * d, .3 * d, .55 * d, .75 * d, .92 * d, d],
                        [grave * .78, grave, aigu, aigu * .98, aigu * .9, grave * 1.12, grave * .8])
    vibrato = 1 + .018 * np.sin(2 * np.pi * 5.3 * t + rng.uniform(0, 6)) * np.clip((t - .3 * d) / (.25 * d), 0, 1)
    hauteur = contour * vibrato * (1 + .006 * bruit_lisse(n, 9) + .01 * bruit_lisse(n, 2.5))
    chant = voix(hauteur, OU)
    enveloppe = np.interp(t, [0, .06 * d, .22 * d, .7 * d, .93 * d, d], [0, .45, 1, .85, .25, 0])
    enveloppe *= 1 + .06 * bruit_lisse(n, 6)
    air = bruit_filtre(duree, 500, 3800) * (.4 + .6 * np.clip((t - .25 * d) / (.2 * d), 0, 1)) * souffle
    return (chant / (np.max(np.abs(chant)) or 1) + air) * enveloppe


def hurlement():
    """Révélation d'un loup : un seul hurlement, dans le lointain."""
    d = 4.6
    sortie = np.zeros(int(SR * d))
    poser(sortie, hurlement_seul(4.2, 320, 620), .15)
    return reverb(sortie, 2.2, .32)


def victoire_loups():
    """Victoire des loups : la meute entière, quatre voix décalées, sous un vent froid."""
    d = 8.0
    sortie = np.zeros(int(SR * d))
    for debut, grave, aigu, gain in ((0, 300, 600, 1.0), (.55, 380, 760, .8), (1.15, 250, 500, .9), (1.8, 340, 680, .7)):
        poser(sortie, hurlement_seul(5.6, grave, aigu), debut, gain)
    t = temps(d)
    sortie += .09 * bruit_filtre(d, 120, 900) * (.6 + .4 * np.sin(2 * np.pi * t / d * 2))
    return reverb(sortie, 2.8, .38)


def mort_gentil():
    """Un innocent meurt : coup de gong grave, un second plus sourd, et un battement sourd dessous."""
    d = 6.0
    t = temps(d)
    sortie = np.zeros(len(t))
    for debut, f0, gain in ((0, 82, 1.0), (1.6, 73, .6)):
        gong = sum(g * np.sin(2 * np.pi * f0 * r * temps(d - debut)) * np.exp(-temps(d - debut) / tau)
                   for r, g, tau in ((1, .55, 2.6), (1.5, .5, 2.0), (2.0, 1.0, 1.9), (2.76, .9, 1.5), (5.4, .5, .9), (8.9, .22, .5)))
        gong *= np.minimum(temps(d - debut) / .006, 1)
        poser(sortie, gong, debut, gain)
    for debut in (0, 1.6):
        poser(sortie, np.sin(2 * np.pi * np.cumsum(np.interp(temps(.8), [0, .8], [75, 38])) / SR) * np.exp(-temps(.8) / .22), debut, .45)
        poser(sortie, bruit_filtre(.25, 60, 400) * np.exp(-temps(.25) / .05), debut, .5)
    return reverb(sortie, 2.0, .22)


def acclamation(duree, hauteur, graine_voyelle=A):
    """« Ouais ! » : une voix qui monte, ouverte sur un « a »."""
    n = int(SR * duree)
    t = np.arange(n) / SR
    f0 = np.interp(t, [0, .25 * duree, duree], [hauteur * .85, hauteur * 1.15, hauteur * 1.05]) * (1 + .01 * bruit_lisse(n, 8))
    v = voix(f0, graine_voyelle, 18, .8)
    return v / (np.max(np.abs(v)) or 1) * np.minimum(t / .03, 1) * np.exp(-t / (duree * .6))


def victoire_village():
    """Victoire du village : fanfare de cuivres, cloches, acclamations et applaudissements."""
    d = 7.0
    sortie = np.zeros(int(SR * d))
    cuivres = tuple((k, 1 / k ** .6) for k in range(1, 10))
    for i, m in enumerate((67, 72, 76, 79)):
        poser(sortie, note(hz(m), .5, cuivres, attaque=.03, relache=.1), i * .22, .4)
    for m in (72, 76, 79, 84):
        poser(sortie, note(hz(m), 2.6, cuivres, attaque=.05, relache=1.2, desaccord=.003), 1.0, .22)
    for i, m in enumerate((88, 91, 95, 100, 96, 103)):
        poser(sortie, note(hz(m), 1.6, CLOCHE, attaque=.003, relache=.4, decroissance=.5), 1.0 + i * .13, .22)
    for debut, hauteur in ((1.1, 230), (1.35, 300), (1.5, 260), (1.8, 340), (2.1, 280)):
        poser(sortie, acclamation(.9, hauteur), debut, .22)
    applaudissements = np.zeros_like(sortie)
    for _ in range(520):
        debut = float(np.clip(rng.normal(3.6, 1.3), 1.2, 6.4))
        poser(applaudissements, impact_bruit(.04, 1000, 7500, .012), debut, rng.uniform(.2, .8))
    sortie += .65 * applaudissements
    return reverb(sortie, 1.6, .2)


if __name__ == "__main__":
    ecrire("hurlement", hurlement(), crete=.7, fondu=.6)
    ecrire("victoire_loups", victoire_loups(), crete=.7, fondu=1.2)
    ecrire("mort_gentil", mort_gentil(), crete=.75, fondu=.8)
    ecrire("victoire_village", victoire_village(), crete=.7, fondu=1.0)
    print("sons écrits dans", DOSSIER)
