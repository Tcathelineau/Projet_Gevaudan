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

La **première nuit** n'a pas de mort : les loups se découvrent, Cupidon lie un couple. Il n'y a pas de vote le premier jour.
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
