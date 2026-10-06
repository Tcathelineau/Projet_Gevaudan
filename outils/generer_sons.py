"""Synthétise les musiques et bruitages du jeu (aucun échantillon tiers) dans src/loup_garou/assets/sons/.

Usage : uv run --python 3.12 --with numpy --with lameenc python outils/generer_sons.py
Les trois musiques durent ~96 s, sans motif court qui se répète : l'oreille ne repère pas la boucle.
"""

import wave
from pathlib import Path

import lameenc
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


def ecrire(nom, signal, crete=.6, fondu=.4, mp3=False):
    signal = np.nan_to_num(signal)
    signal = signal / (np.max(np.abs(signal)) or 1) * crete
    if fondu:
        n = int(SR * fondu)
        signal[-n:] *= np.linspace(1, 0, n)
        signal[:n // 4] *= np.linspace(0, 1, n // 4)
    pcm = (signal * 32767).astype("<i2")
    DOSSIER.mkdir(parents=True, exist_ok=True)
    if mp3:
        enc = lameenc.Encoder()
        enc.set_bit_rate(64)
        enc.set_in_sample_rate(SR)
        enc.set_channels(1)
        enc.set_quality(2)
        (DOSSIER / f"{nom}.mp3").write_bytes(enc.encode(pcm.tobytes()) + enc.flush())
    else:
        with wave.open(str(DOSSIER / f"{nom}.wav"), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes(pcm.tobytes())


# --- musiques ------------------------------------------------------------------------------------

DUREE = 96.0


def musique_nuit():
    """Ré mineur, sans pulsation : nappes lentes, drone, boîte à musique clairsemée, vent, battements sourds."""
    n = int(SR * DUREE)
    pad, drone, boite, vent, coeur = (np.zeros(n) for _ in range(5))
    accords = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52, 58)]
    for i in range(12):
        accord = list(accords[i % 4])
        if i % 4 == 0 and i >= 4:
            accord.append(63)  # mi bémol : la seconde mineure qui dérange
        for m in accord:
            poser(pad, note(hz(m), 11.5, SCIE, attaque=2.8, relache=3.0, desaccord=.004), i * 8, .22)
    t = temps(DUREE)
    drone += (np.sin(2 * np.pi * hz(38) * t) + .6 * np.sin(2 * np.pi * hz(45) * t)) * (.75 + .25 * np.sin(2 * np.pi * .07 * t))
    gamme = [74, 75, 77, 79, 81, 82, 84, 86]
    poids = np.array([4, 3, 2, 2, 2, 1.5, 1, 1], dtype=float)
    instant = 2.0
    while instant < DUREE - 6:
        m = int(rng.choice(gamme, p=poids / poids.sum()))
        motif = [m] if rng.random() < .6 else [m, m - int(rng.choice([1, 2])), m - int(rng.choice([3, 4]))]
        for k, mm in enumerate(motif):
            poser(boite, note(hz(mm), 2.2, CLOCHE, attaque=.004, relache=.2, decroissance=.8), instant + k * .42)
        instant += float(rng.uniform(2.4, 5.5))
    boite = echo(boite, .55, .45, 4)
    vent = bruit_filtre(DUREE, 250, 1400) * (.55 + .3 * np.sin(2 * np.pi * .06 * t) + .15 * np.sin(2 * np.pi * .11 * t + 1))
    instant = 4.0
    while instant < DUREE - 3:
        for decalage, force in ((0, 1.0), (.33, .65)):
            poser(coeur, grosse_caisse(force, .5), instant + decalage)
        instant += float(rng.uniform(7, 12))
    for debut in (38, 78):
        for m in (64, 65):
            poser(pad, note(hz(m), 9, SCIE, attaque=4, relache=4), debut, .12)
    mix = .9 * pad / 3 + .22 * drone + .5 * boite + .13 * vent + .35 * coeur
    return reverb(mix, 2.2, .3)


def musique_jour():
    """Do majeur, 116 bpm : basse sautillante, accords sur les contretemps, mélodie pentatonique, grelots."""
    n = int(SR * DUREE)
    basse, accords_p, melodie, grelots, perc = (np.zeros(n) for _ in range(5))
    battement = 60 / 116
    mesure = 4 * battement
    progression = [(36, (60, 64, 67)), (43, (59, 62, 67)), (45, (60, 64, 69)), (41, (60, 65, 69)),
                   (36, (60, 64, 67)), (43, (59, 62, 67)), (41, (60, 65, 69)), (43, (62, 65, 67))]
    pentatonique = [72, 74, 76, 79, 81, 84]
    motifs = [[1, 0, 1, 1, 0, 1, 1, 0], [1, 1, 0, 1, 1, 0, 1, 0], [1, 0, 0, 1, 1, 0, 1, 1], [1, 0, 1, 0, 1, 1, 0, 1]]
    degre = 2
    for b in range(int(DUREE / mesure)):
        racine, accord = progression[b % 8]
        debut = b * mesure
        poser(basse, note(hz(racine), .5, CARRE, attaque=.005, relache=.1, decroissance=.18), debut, .9)
        poser(basse, note(hz(racine + 7), .5, CARRE, attaque=.005, relache=.1, decroissance=.18), debut + 2 * battement, .7)
        for tps in (1, 3):
            for m in accord:
                poser(accords_p, note(hz(m), .4, SCIE, attaque=.004, relache=.08, decroissance=.12), debut + tps * battement + battement / 2, .16)
        for k, actif in enumerate(motifs[(b // 2) % 4] if b % 2 == 0 else motifs[(b // 2 + 1) % 4]):
            if not actif:
                continue
            degre = int(np.clip(degre + rng.choice([-1, 0, 1, 1, -2, 2]), 0, len(pentatonique) - 1))
            poser(melodie, note(hz(pentatonique[degre]), .45, FLUTE, attaque=.01, relache=.12, decroissance=.3), debut + k * battement / 2, .5)
        if b % 2 == 0:
            poser(grelots, note(hz(accord[1] + 24), 1.6, CLOCHE, attaque=.003, relache=.3, decroissance=.5), debut + 2 * battement, .5)
        for tps in (0, 2):
            poser(perc, grosse_caisse(.8, .3), debut + tps * battement)
        for demi in range(8):
            poser(perc, impact_bruit(.06, 5000, 9000, .02), debut + demi * battement / 2, .12 if demi % 2 else .2)
        for tps in (1, 3):
            poser(perc, impact_bruit(.14, 1500, 4500, .05), debut + tps * battement, .18)
    mix = .5 * basse + .55 * accords_p + .6 * melodie + .35 * grelots + .55 * perc
    return reverb(mix, 1.1, .16)


def musique_conseil():
    """La mineur, 132 bpm : ostinato nerveux, battements de cœur, cordes en trémolo, tic-tac, montées de tension."""
    n = int(SR * DUREE)
    ostinato, coeur, cordes, tic, effets = (np.zeros(n) for _ in range(5))
    battement = 60 / 132
    mesure = 4 * battement
    racines = [45, 41, 38, 40]  # la, fa, ré, mi
    accords = [(57, 60, 64), (53, 57, 60), (50, 53, 57), (52, 56, 59)]
    accent = [1, .45, .7, .45, 1, .5, .75, .6]
    for b in range(int(DUREE / mesure)):
        groupe = (b // 4) % 4
        section = (b // 16) % 3
        debut = b * mesure
        intensite = .55 + .15 * ((b % 16) / 16) + .1 * section
        for k in range(8):
            poser(ostinato, note(hz(racines[groupe] + (12 if k in (3, 7) and b % 8 > 4 else 0)), .24, CARRE, attaque=.004, relache=.05, decroissance=.1),
                  debut + k * battement / 2, accent[k] * intensite)
        poser(coeur, grosse_caisse(1.0, .4), debut)
        poser(coeur, grosse_caisse(.7, .4), debut + 2.5 * battement)
        if (b // 8) % 2 == 1:
            for k in range(4):
                poser(tic, note(2400 if k % 2 == 0 else 1800, .03, ((1, 1),), attaque=.001, relache=.02, decroissance=.01), debut + k * battement, .12)
        if b % 4 == 2:
            for m in (57, 58):
                poser(effets, note(hz(m), .3, CARRE, attaque=.003, relache=.1, decroissance=.1), debut + battement * 3, .25)
    for g in range(int(DUREE / (mesure * 2))):
        accord = accords[(g // 2) % 4]
        for m in accord:
            tr = 1 + .4 * np.sin(2 * np.pi * 9 * temps(2 * mesure + 1.5))
            poser(cordes, note(hz(m), 2 * mesure + 1.5, SCIE, attaque=1.2, relache=1.5, desaccord=.006) * tr, g * 2 * mesure, .16)
    for section in range(int(DUREE / (16 * mesure)) + 1):
        fin = (section + 1) * 16 * mesure
        monte = bruit_filtre(2 * mesure, 200, 6000) * np.linspace(0, 1, int(SR * 2 * mesure)) ** 2
        poser(effets, monte, fin - 2 * mesure, .5)
        poser(effets, impact_bruit(1.6, 40, 400, .5) * 2, fin, .9)
    mix = .55 * ostinato + .7 * coeur + .8 * cordes + 1.0 * tic + .6 * effets
    return reverb(mix, 1.0, .14)


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
    ecrire("musique_nuit", musique_nuit(), crete=.7, fondu=2.5, mp3=True)
    ecrire("musique_jour", musique_jour(), crete=.7, fondu=2.5, mp3=True)
    ecrire("musique_conseil", musique_conseil(), crete=.7, fondu=2.5, mp3=True)
    ecrire("hurlement", hurlement(), crete=.7, fondu=.5)
    ecrire("victoire_village", victoire_village(), crete=.7, fondu=.8)
    ecrire("victoire_loups", victoire_loups(), crete=.7, fondu=1.0)
    print("sons écrits dans", DOSSIER)
