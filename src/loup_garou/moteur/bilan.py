"""Bilan d'une partie terminée : chiffres clés, distinctions et frise des disparitions (sans Streamlit)."""

from loup_garou.roles import ROLES

# Genre de mort (cf. `tuer`) -> (emoji, libellé de la cause)
CAUSES = {
    "loups": ("🐺", "dévoré par les loups"),
    "loup_blanc": ("🌕", "dévoré par le Loup Blanc"),
    "poison": ("☠️", "empoisonné"),
    "village": ("⚖️", "éliminé par le village"),
    "tir": ("🔫", "abattu par le chasseur"),
    "chagrin": ("💔", "mort de chagrin"),
    "autre": ("💀", "mort"),
}


def _nom_role(mort):
    return f"{mort['nom']} ({ROLES[mort['role']].nom})"


def bilan_partie(s):
    """Dictionnaire {chiffres, distinctions, frise} ; vide de morts si la partie n'en a pas enregistré."""
    morts = s.get("morts", [])
    condamnes = [m for m in morts if m["genre"] == "village"]
    loups_demasques = [m for m in condamnes if m["camp"] == "loups"]
    innocents = [m for m in condamnes if m["camp"] != "loups"]
    survivants = [n for n, d in s["joueurs"].items() if d["vivant"]]

    chiffres = [
        ("🌙", "Nuits", s["jour"] + 1),
        ("💀", "Morts", len(morts)),
        ("🐺", "Dévorés par les loups", sum(m["genre"] in ("loups", "loup_blanc") for m in morts)),
        ("🎯", "Loups démasqués", len(loups_demasques)),
        ("🙈", "Innocents condamnés", len(innocents)),
        ("🕯️", "Survivants", len(survivants)),
    ]

    distinctions = []
    if morts:
        premier = morts[0]
        distinctions.append(("🥀", "Première victime", f"{_nom_role(premier)}, {CAUSES[premier['genre']][1]}."))
    if innocents:
        e = innocents[0]
        distinctions.append(("🙈", "Erreur judiciaire", f"{_nom_role(e)} a été condamné à tort au jour {e['jour']}."))
    if loups_demasques:
        noms = ", ".join(_nom_role(m) for m in loups_demasques)
        distinctions.append(("🎯", "Bon flair", f"Le village a démasqué {len(loups_demasques)} loup(s) : {noms}."))
    for m in morts:
        if m["genre"] == "tir":
            distinctions.append(("🔫", "Dernière balle", f"{_nom_role(m)} a été emporté par un tir du chasseur."))
            break
    for m in morts:
        if m["genre"] == "chagrin":
            distinctions.append(("💔", "Amour fatal", f"{_nom_role(m)} n'a pas survécu à la perte de son amoureux."))
            break
    loups = [n for n in s["joueurs"] if _est_loup(s, n)]
    discret = _loup_le_plus_discret(s, loups, morts)
    if discret:
        distinctions.append(discret)

    return {"chiffres": chiffres, "distinctions": distinctions, "frise": _frise(morts), "survivants": survivants}


def _est_loup(s, nom):
    d = s["joueurs"][nom]
    return (d.get("camp_choisi") or ROLES[d["role"]].camp) == "loups"


def _loup_le_plus_discret(s, loups, morts):
    """Le loup resté en vie le plus longtemps (un survivant l'emporte sur un loup tombé tard)."""
    if not loups:
        return None
    mort_le = {m["nom"]: m["jour"] for m in morts}
    vivants = [n for n in loups if s["joueurs"][n]["vivant"]]
    if vivants:
        return ("🕶️", "Loup le plus discret", f"{', '.join(vivants)} {'a' if len(vivants) == 1 else 'ont'} survécu jusqu'au bout.")
    tard = max(loups, key=lambda n: mort_le.get(n, -1))
    return ("🕶️", "Loup le plus discret", f"{tard} est resté caché jusqu'au jour {mort_le.get(tard, 0)}.")


def _frise(morts):
    """Disparitions regroupées par nuit ou par jour, dans l'ordre : [(titre, [mort, ...]), ...]."""
    groupes = []
    for m in morts:
        cle = (m["moment"], m["jour"])
        if not groupes or groupes[-1][0] != cle:
            groupes.append((cle, []))
        groupes[-1][1].append(m)
    return [
        (f"🌙 Nuit {j}" if moment == "nuit" else f"☀️ Jour {j}", liste)
        for (moment, j), liste in groupes
    ]


# --- coulisses : les événements de rôle, rangés par thème --------------------------------------------

# (emoji, titre, motifs du journal). Un événement va dans le premier thème dont un motif apparaît dans son texte.
THEMES = (
    ("💘", "Les amoureux", (" lie ", "Le hasard lie", "meurt de chagrin", "découvre le couple")),
    ("🧪", "Les potions", ("potion de soin", "empoisonne", "empoisonné par la sorcière", "sorcière")),
    ("🛡️", "Les protections", ("protège", "sauvé par le salvateur")),
    ("🔮", "Les visions", ("sonde", "flaire")),
    ("🌕", "Le Loup Blanc", ("Le Loup Blanc", "dévoré par le Loup Blanc")),
    ("🐶", "Le Louveteau", ("Louveteau est mort",)),
    ("🐾", "L'enfant sauvage et son mentor", ("mentor",)),
    ("🔫", "Les tirs du chasseur", ("abattu par le chasseur", "renonce à tirer")),
    ("🃏", "Changements de rôle et de camp", ("Chien-Loup", "(Voleur)", "prend le rôle", "devient simple Villageois")),
    ("⚖️", "Le juge bègue", ("juge bègue",)),
    ("👑", "Le maire", ("élu maire", "successeur")),
)


def coulisses(joueurs, journal):
    """Événements de rôle d'une partie, par thème : [(emoji, titre, [ligne, ...]), ...] (thèmes vides omis).

    Fonctionne sur le journal seul, donc aussi sur les parties archivées avant l'existence de cette fonction."""
    par_theme = {titre: [] for _, titre, _ in THEMES}
    for e in journal:
        if e["moment"] in ("debut", "fin"):
            continue
        for _, titre, motifs in THEMES:
            if any(m in e["texte"] for m in motifs):
                quand = f"Nuit {e['jour']}" if e["moment"] == "nuit" else f"Jour {e['jour']}"
                par_theme[titre].append(f"{quand} : {e['texte']}")
                break
    resultat = []
    for emoji, titre, _ in THEMES:
        lignes = par_theme[titre]
        if titre == "Les amoureux":
            amoureux = [n for n, d in joueurs.items() if d.get("amoureux")]
            if amoureux:
                roles = ", ".join(f"{n} ({ROLES[joueurs[n]['role']].nom})" for n in amoureux if joueurs[n]["role"] in ROLES)
                camps = {(joueurs[n].get("camp_choisi") or ROLES[joueurs[n]["role"]].camp) for n in amoureux if joueurs[n]["role"] in ROLES}
                mixte = " : couple mixte, un camp à part" if len(camps) > 1 else ""
                lignes = [f"Le couple : {roles}{mixte}."] + lignes
        if lignes:
            resultat.append((emoji, titre, lignes))
    return resultat
