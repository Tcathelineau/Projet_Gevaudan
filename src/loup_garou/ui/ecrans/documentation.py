"""Documentation des rôles : une dalle par rôle, avec son résumé et ses notes d'équilibre."""

import html

import streamlit as st

from loup_garou.equilibre import ROLES_NOTES
from loup_garou.roles import ROLES
from loup_garou.ui.composants import scene_ciel
from loup_garou.ui.ecrans.accueil import aller_a
from loup_garou.ui.illustrations import ASSETS, svg_role
from loup_garou.ui.regles import afficher_regles
from loup_garou.ui.styles import CSS_DOCUMENTATION, CSS_SANS_SIDEBAR

IMPACT_MAX = 40  # impact absolu qui remplit la demi-barre (le Louveteau, le plus extrême, vaut -38)


def _camp(role):
    if role.solitaire:
        return "solo", "Solitaire"
    if role.camp_secret:
        return "choix", "Camp au choix"
    if role.camp == "loups":
        return "loups", "Loups"
    return "village", "Village"


def _pourcentage(valeur):
    return f'<div class="doc-pct"><span style="width: {valeur}%;"></span></div>'


def _dalle(role):
    notes = ROLES_NOTES[role.key]
    classe_camp, libelle_camp = _camp(role)
    impact = notes["impact_pts"]
    if role.lot > 1:
        libelle_camp += f" · {role.lot} cartes : impact par carte, {impact * role.lot:+.0f} pts ensemble"
    if abs(impact) < .5:
        remplissage, signe = "", "0"
    else:
        cote = "village" if impact > 0 else "loups"
        largeur = min(abs(impact) / IMPACT_MAX, 1) * 50
        remplissage = f'<span class="doc-barre-{cote}" style="width: {largeur:.1f}%;"></span>'
        signe = f"+{impact:.0f}" if impact > 0 else f"{impact:.0f}"
    return (
        f'<div class="doc-dalle doc-{classe_camp}">'
        f'<div class="doc-tete"><div class="icone-role" style="background: {role.degrade};">{svg_role(role.key, "icone-art", role.emoji)}</div>'
        f'<div><div class="doc-nom">{html.escape(role.nom)}</div>'
        f'<div class="doc-camp">{libelle_camp}</div></div></div>'
        f'<div class="doc-resume">{html.escape(role.description)}</div>'
        '<div class="doc-notes">'
        f'<div class="doc-note"><span>⚖️ Impact</span><div class="doc-force">{remplissage}</div><b>{signe} pts</b></div>'
        f'<div class="doc-note"><span>🔮 Information</span>{_pourcentage(notes["info"])}<b>{notes["info"]} %</b></div>'
        f'<div class="doc-note"><span>🌀 Chaos</span>{_pourcentage(notes["chaos"])}<b>{notes["chaos"]} %</b></div>'
        '</div></div>'
    )


def _credits():
    fichier = ASSETS / "CREDITS.md"
    return fichier.read_text(encoding="utf-8") if fichier.exists() else ""


def ecran_documentation():
    st.markdown(CSS_SANS_SIDEBAR + CSS_DOCUMENTATION, unsafe_allow_html=True)
    if st.button("← Menu", key="retour_menu_documentation"):
        aller_a("accueil")
    scene_ciel("jour", "Documentation", "Comment jouer, et les rôles du village avec leur poids dans l'équilibre")
    onglet_roles, onglet_regles = st.tabs(["🃏 Les rôles", "📖 Comment jouer"])
    with onglet_regles:
        afficher_regles()
    with onglet_roles:
        st.caption(
            "Impact : points de chance de victoire du village que le rôle ajoute (+) ou retire (-) à une table équilibrée. "
            "Information : part de l'information utile au village que le rôle apporte, de 0 à 100 % (100 = le meilleur). "
            "Chaos : événements imprévus qu'il provoque (morts hors loups et vote, changements de camp...), de 0 à 100 %. "
            "Mesures par simulation de parties automatiques, donc des ordres de grandeur : méthode dans docs/equilibre-roles.md."
        )
        st.markdown(
            f'<div class="doc-grille">{"".join(_dalle(r) for r in ROLES.values())}</div>', unsafe_allow_html=True,
        )
    with st.expander("🎨 Crédits"):
        st.markdown(_credits())
