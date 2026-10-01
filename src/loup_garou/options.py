"""Options de partie réglables dans le menu de composition, et leurs valeurs par défaut."""


OPTIONS_DEFAUT = {
    "potions_sorciere": 1,     # potions de soin de la sorcière
    "potions_mort": 0,         # potions de mort de la sorcière
    "couple_hasard": False,    # couple tiré au sort au départ, sans Cupidon
    "trouple": False,          # l'amour lie trois joueurs au lieu de deux
    "cadence_voyante": 2,      # la voyante sonde une nuit sur N (à partir de la nuit 1)
    "cadence_loup_blanc": 2,   # le Loup Blanc festoie une nuit sur N (à partir de la nuit 1)
    "maire_depart": True,      # à égalité loups/village, la partie continue sauf si le maire est un loup
}


def opt(s, cle):
    """Option de partie (les anciennes sauvegardes n'en ont pas : valeur par défaut)."""
    return s.get("options", {}).get(cle, OPTIONS_DEFAUT[cle])


def taille_couple(s):
    return 3 if opt(s, "trouple") else 2


def nuit_active(s, cadence):
    """Nuit 1 puis une nuit sur `cadence`."""
    return s["jour"] > 0 and (s["jour"] - 1) % cadence == 0


def prochaine_nuit(s, cadence):
    return s["jour"] + cadence - (s["jour"] - 1) % cadence


CADENCES = {1: "Chaque nuit", 2: "Une nuit sur 2", 3: "Une nuit sur 3"}
