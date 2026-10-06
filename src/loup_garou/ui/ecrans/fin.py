"""Écran de fin de partie et journal détaillé."""

import html
import json

import streamlit as st

from loup_garou.moteur.bilan import CAUSES, bilan_partie
from loup_garou.moteur.partie import nouvelle_partie
from loup_garou.moteur.persistance import clear_save
from loup_garou.roles import ROLES
from loup_garou.ui.composants import scene_victoire
from loup_garou.ui.styles import CSS_BILAN


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


def afficher_bilan(s):
    """Chiffres clés, distinctions et frise des disparitions."""
    bilan = bilan_partie(s)
    tuiles = "".join(
        f'<div class="bil-tuile"><span class="bil-emoji">{emoji}</span><b>{valeur}</b><span>{libelle}</span></div>'
        for emoji, libelle, valeur in bilan["chiffres"]
    )
    st.markdown(f'<div class="bil-tuiles">{tuiles}</div>', unsafe_allow_html=True)

    if bilan["distinctions"]:
        st.subheader("Les distinctions")
        st.markdown("".join(
            f'<div class="bil-dist"><span class="bil-dist-emoji">{emoji}</span><div>'
            f'<div class="bil-dist-titre">{html.escape(titre)}</div><div>{html.escape(texte)}</div></div></div>'
            for emoji, titre, texte in bilan["distinctions"]
        ), unsafe_allow_html=True)

    if bilan["frise"]:
        st.subheader("Les disparitions")
        for titre, morts in bilan["frise"]:
            classe = "jrn-nuit" if titre.startswith("🌙") else "jrn-jour"
            lignes = "".join(
                f'<div class="jrn-ligne"><span>{CAUSES[m["genre"]][0]}</span><span>'
                f'<b>{html.escape(m["nom"])}</b> ({ROLES[m["role"]].emoji} {ROLES[m["role"]].nom}), '
                f'{CAUSES[m["genre"]][1]}</span></div>'
                for m in morts
            )
            st.markdown(
                f'<div class="jrn-bloc {classe}"><div class="jrn-tete">{titre}</div>{lignes}</div>',
                unsafe_allow_html=True,
            )


def _quitter():
    clear_save()
    st.session_state.clear()


def ecran_fin(s):
    st.markdown(CSS_BILAN, unsafe_allow_html=True)
    message = s["message_fin"]
    if message.startswith("Le village a gagné"):
        scene_victoire("village", "Le village a gagné !", "Fin de la partie")
    elif message.startswith("Les loups ont gagné"):
        scene_victoire("loups", "Les loups ont gagné !", "Fin de la partie")
    else:
        st.title("🏁 Fin de la partie")
    st.header(message)
    afficher_bilan(s)
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

    col_rejouer, col_menu = st.columns(2)
    if col_rejouer.button(
        "🔁 Rejouer avec les mêmes joueurs", type="primary", key="fin_rejouer",
        disabled="composition" not in s, use_container_width=True,
    ):
        nouvelle = nouvelle_partie(list(s["joueurs"]), s["composition"], s.get("options"))
        _quitter()
        st.session_state.partie = nouvelle
        st.rerun()
    if col_menu.button("🏠 Retour au menu", key="fin_menu", use_container_width=True):
        _quitter()
        st.rerun()


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
