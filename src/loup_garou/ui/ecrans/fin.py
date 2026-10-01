"""Écran de fin de partie et journal détaillé."""

import html
import json

import streamlit as st

from loup_garou.roles import ROLES
from loup_garou.ui.composants import scene_victoire


def afficher_roles(joueurs):
    for nom, d in joueurs.items():
        etat = "en vie" if d["vivant"] else "mort"
        coeur = " 💘" if d["amoureux"] else ""
        ancien = " (ex-enfant sauvage)" if d.get("enfant_sauvage") else ""
        ancien += " (ex-voleur)" if d.get("voleur") else ""
        ancien += " (ex-renard)" if d.get("renard") else ""
        if d.get("camp_choisi"):
            ancien += " (loup-garou)" if d["camp_choisi"] == "loups" else " (villageois)"
        st.write(f"{ROLES[d['role']].emoji} **{nom}** — {ROLES[d['role']].nom}{ancien} ({etat}){coeur}")


def ecran_fin(s):
    message = s["message_fin"]
    if message.startswith("Le village a gagné"):
        scene_victoire("village", "Le village a gagné !", "Fin de la partie")
    elif message.startswith("Les loups ont gagné"):
        scene_victoire("loups", "Les loups ont gagné !", "Fin de la partie")
    else:
        st.title("🏁 Fin de la partie")
    st.header(message)
    st.subheader("Les rôles")
    afficher_roles(s["joueurs"])

    with st.expander("📜 Afficher le log de la partie"):
        afficher_historique(s)
    st.download_button(
        "Télécharger l'historique (JSON)",
        data=json.dumps(
            {"issue": s["message_fin"], "joueurs": s["joueurs"], "journal": s["journal"]},
            indent=2, ensure_ascii=False,
        ),
        file_name="historique_partie.json",
        mime="application/json",
    )
    if s.get("archive"):
        st.caption(f"Archive enregistrée dans {s['archive']}")


# Premier motif trouvé dans le texte gagne : les morts passent avant les rôles.
ICONES_EVENEMENTS = [
    ("meurt de chagrin", "💔"),
    ("abattu par le chasseur", "🔫"),
    ("renonce à tirer", "🕊️"),
    ("éliminé par le village", "⚖️"),
    ("dévoré par le Loup Blanc", "💀"),
    ("dévoré par les loups", "💀"),
    ("Personne ne meurt", "🌅"),
    ("ne s'accordent pas", "🤷"),
    ("sauvé par", "💚"),
    ("devient loup-garou", "🐺"),
    ("est élu maire", "👑"),
    ("comme successeur", "👑"),
    ("Loup Blanc", "🌕"),
    ("Chien-Loup", "🐕"),
    ("renard", "🦊"),
    ("Renard", "🦊"),
    ("voyante", "🔮"),
    ("sorcière", "🧪"),
    ("Cupidon", "💘"),
    ("salvateur", "🛡️"),
    ("mentor", "🐾"),
    ("Voleur", "🃏"),
    ("désigne", "🍖"),
]


def icone_evenement(texte):
    return next((icone for motif, icone in ICONES_EVENEMENTS if motif in texte), "▪️")


def afficher_historique(s):
    """Journal en cases : une case par nuit, par jour et pour l'issue, dans l'ordre chronologique."""
    blocs = []
    for e in s["journal"]:
        if e["moment"] == "debut":
            continue
        if e["moment"] == "fin":
            cle, classe, titre = ("fin", None), "jrn-fin", "🏁 Issue de la partie"
        elif e["moment"] == "nuit":
            suite = " <small>· première nuit</small>" if e["jour"] == 0 else ""
            cle, classe, titre = ("nuit", e["jour"]), "jrn-nuit", f"🌙 Nuit {e['jour']}{suite}"
        else:
            cle, classe, titre = ("jour", e["jour"]), "jrn-jour", f"☀️ Jour {e['jour']}"
        if not blocs or blocs[-1][0] != cle:
            blocs.append((cle, classe, titre, []))
        icone = "🏆" if e["moment"] == "fin" else icone_evenement(e["texte"])
        blocs[-1][3].append(f'<div class="jrn-ligne"><span>{icone}</span><span>{html.escape(e["texte"])}</span></div>')
    for _, classe, titre, lignes in blocs:
        st.markdown(
            f'<div class="jrn-bloc {classe}"><div class="jrn-tete">{titre}</div>{"".join(lignes)}</div>',
            unsafe_allow_html=True,
        )
