"""Rappel des règles : texte commun au tutoriel (page Documentation) et au rappel en cours de partie."""

import streamlit as st

from loup_garou.roles import ROLES

# (titre, texte en markdown). Le texte reprend les règles décidées du README.
SECTIONS = [
    ("🎯 Le principe", """
Un village est hanté par des **loups-garous**. Chaque nuit ils dévorent un villageois ; chaque jour le village vote pour éliminer un suspect.
L'application joue le **meneur du jeu** : elle distribue les rôles en secret, mène les nuits, compte les morts et annonce le vainqueur.
"""),
    ("🔄 Le déroulement", """
1. **La nuit** : l'appareil passe de joueur en joueur. Chacun découvre sa carte et agit en secret (dévorer, sonder, protéger, soigner...).
2. **Le réveil** : le panneau d'affichage annonce les morts et le camp qu'ils avaient.
3. **Le conseil** : on débat à voix haute, puis le village élimine un joueur. L'app révèle si c'était un loup.
4. Retour à la nuit, jusqu'à la victoire d'un camp.

La **première nuit** n'a pas de mort : les loups se découvrent, Cupidon lie un couple, qui ne l'apprend qu'à la nuit suivante. Il n'y a pas de vote le premier jour.
"""),
    ("🏆 Comment gagner", """
- **Le village** gagne quand tous les loups sont morts.
- **Les loups** gagnent quand ils sont plus nombreux que les autres (ou aussi nombreux, si l'un d'eux est maire).
- **Les amoureux** gagnent s'ils sont les derniers survivants. Un couple loup + villageois forme un camp à part : tant qu'il vit, ni le village ni la meute ne peut gagner.
- **Les solitaires** (Loup Blanc) gagnent seuls, en éliminant tout le monde.
"""),
    ("👑 Le maire", """
Il est élu au premier jour. S'il meurt, il désigne lui-même son successeur. Quand loups et villageois sont à égalité, la partie continue sauf si le maire est un loup (cette règle se règle dans les options avancées).
"""),
    ("🤫 Passer l'appareil sans tricher", """
À chaque tour de nuit, deux écrans se succèdent : **« Je vais chercher X »**, puis **« Oui, je suis X »**. Ne cliquez sur le second qu'une fois l'appareil dans les bonnes mains : il dévoile la carte.
Si les loups ne s'accordent pas sur une victime, personne n'est dévoré. Les loups peuvent aussi désigner l'un des leurs (sacrifice, bluff).
"""),
    ("🕰️ Le rythme et les esprits", """
Le jeu se vit sur plusieurs heures ou plusieurs jours : **les joueurs décident ensemble** quand ouvrir un conseil. Les morts deviennent des **esprits frappeurs** : ils discutent et glanent des informations, mais ne votent pas et ne parlent pas au conseil. Les esprits ne vont jamais vers les vivants : ce sont les vivants qui viennent les interroger.
"""),
    ("🛟 En cas d'erreur", """
Le menu **Option** de la barre latérale permet de **revenir au début d'une nuit ou à l'annonce d'un jour** (clic malheureux, plantage). La partie est sauvegardée à chaque étape : fermer le navigateur n'efface rien.
"""),
]


# En cours de partie, le rappel se limite aux règles de victoire (le déroulement se lit dans la documentation).
SECTIONS_RAPPEL = [section for section in SECTIONS if section[0] == "🏆 Comment gagner"]

# Réglages de l'étape « Options » : (thème, [(clés de OPTIONS_DEFAUT, intitulé, explication)]).
# Un test vérifie que chaque option y figure.
OPTIONS_DOC = [
    ("🧪 La sorcière", [
        (("potions_sorciere", "potions_mort"), "Potions de soin et de mort",
         "Nombre de potions de chaque sorte, de 0 à 5 (1 potion de soin et aucune de mort par défaut). "
         "Une potion de soin sauve la victime des loups, une potion de mort élimine un joueur (le poison échappe au soin et à la protection)."),
        (("sorciere_sait_sauve",), "Elle apprend qui elle a sauvé",
         "Désactivé par défaut. La nuit suivant l'usage de sa potion de soin, la sorcière découvre l'identité de la personne sauvée."),
    ]),
    ("🔮 La voyante et 🌕 le Loup Blanc", [
        (("cadence_voyante",), "Fréquence des visions",
         "La voyante sonde chaque nuit, une nuit sur 2 (défaut) ou une nuit sur 3, à partir de la nuit 1."),
        (("cadence_loup_blanc",), "Fréquence des festins",
         "Le Loup Blanc dévore l'un de ses frères loups chaque nuit, une nuit sur 2 (défaut) ou une nuit sur 3, à partir de la nuit 1."),
    ]),
    ("💘 L'amour", [
        (("couple_hasard",), "Couple tiré au sort, sans Cupidon",
         "Désactivé par défaut. Le couple est désigné au hasard dès le départ et Cupidon est remplacé par un villageois. "
         "Les amoureux l'apprennent à la nuit 1."),
        (("voyante_couple",), "BONUS : la voyante peut découvrir le couple",
         "Activé par défaut, seulement avec un couple tiré au sort. À chaque vision, la voyante choisit entre sonder un rôle "
         "et apprendre qui forme le couple (une seule fois)."),
        (("trouple",), "Mode fun : un trouple",
         "Désactivé par défaut. L'amour lie trois joueurs au lieu de deux (choisis par Cupidon ou tirés au sort) : si l'un meurt, les deux autres le suivent."),
    ]),
    ("👑 Le village", [
        (("maire_depart",), "Le maire départage les égalités",
         "Activé par défaut : à égalité loups / village, la partie continue sauf si le maire est un loup. "
         "Désactivé : les loups gagnent dès qu'ils sont aussi nombreux que les autres."),
        (("revelation_mort",), "Ce que révèle une mort",
         "Le camp (défaut : « était loup-garou » ou non), le rôle complet, ou rien. Avec « Rien », le menu de gauche ne donne plus les effectifs par camp, "
         "et le gong grave, la couleur des avis du village ne trahissent plus le camp du mort."),
        (("composition_secrete",), "Composition secrète",
         "Désactivé par défaut. Le rappel des règles ne liste plus les rôles du paquet ; les effectifs par camp restent visibles à gauche."),
    ]),
    ("⏰ Le temps", [
        (("echeance_active", "echeance_min", "echeance_max"), "Échéance aléatoire du conseil",
         "Désactivé par défaut. Chaque jour, au réveil, une durée est tirée au hasard entre deux bornes (de 15 min à 24 h) : "
         "un bandeau affiche l'heure limite et le temps restant. Elle est indicative, rien ne force le vote. Pas d'échéance le premier jour."),
    ]),
]


def afficher_options():
    """Description de tous les réglages de la partie, thème par thème."""
    for theme, reglages in OPTIONS_DOC:
        st.markdown(f"**{theme}**")
        for _, nom, texte in reglages:
            st.markdown(f"- **{nom}** : {texte}")


def afficher_regles(sections=None):
    for titre, texte in SECTIONS if sections is None else sections:
        st.markdown(f"**{titre}**")
        st.markdown(texte.strip())


def afficher_roles_de_la_partie(s):
    """Rôles du paquet avec leur résumé (sans dire qui les joue)."""
    for cle, n in s.get("composition", {}).items():
        role = ROLES[cle]
        quantite = f" ×{n}" if n > 1 else ""
        st.markdown(f"{role.emoji} **{role.nom}**{quantite} : {role.description or 'Pas de pouvoir particulier.'}")
