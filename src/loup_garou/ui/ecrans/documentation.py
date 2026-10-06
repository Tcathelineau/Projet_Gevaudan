"""Documentation des rôles : une dalle par rôle, avec son résumé et ses notes d'équilibre."""

import html

import streamlit as st

from loup_garou.equilibre import NOTES
from loup_garou.roles import ROLES
from loup_garou.ui.composants import scene_ciel
from loup_garou.ui.ecrans.accueil import aller_a
from loup_garou.ui.regles import afficher_regles
from loup_garou.ui.styles import CSS_DOCUMENTATION, CSS_SANS_SIDEBAR

FORCE_MAX = 7  # force absolue la plus élevée du barème : sert d'échelle à la barre


def _camp(role):
    if role.solitaire:
        return "solo", "Solitaire"
    if role.camp_secret:
        return "choix", "Camp au choix"
    if role.camp == "loups":
        return "loups", "Loups"
    return "village", "Village"


def _pastilles(valeur):
    return "".join(f'<i class="{"on" if i < valeur else ""}"></i>' for i in range(5))


def _dalle(role):
    notes = NOTES[role.key]
    classe_camp, libelle_camp = _camp(role)
    if role.lot > 1:
        libelle_camp += f" · {role.lot} cartes (notes par carte)"
    if notes.force == 0:
        remplissage, signe = "", "0"
    else:
        cote = "village" if notes.force > 0 else "loups"
        largeur = min(abs(notes.force) / FORCE_MAX, 1) * 50
        remplissage = f'<span class="doc-barre-{cote}" style="width: {largeur:.1f}%;"></span>'
        signe = f"+{notes.force}" if notes.force > 0 else str(notes.force)
    return (
        f'<div class="doc-dalle doc-{classe_camp}">'
        f'<div class="doc-tete"><div class="icone-role" style="background: {role.degrade};">{role.emoji}</div>'
        f'<div><div class="doc-nom">{html.escape(role.nom)}</div>'
        f'<div class="doc-camp">{libelle_camp}</div></div></div>'
        f'<div class="doc-resume">{html.escape(role.description)}</div>'
        '<div class="doc-notes">'
        f'<div class="doc-note"><span>⚖️ Force</span><div class="doc-force">{remplissage}</div><b>{signe}</b></div>'
        f'<div class="doc-note"><span>🔮 Information</span><div class="doc-pastilles">{_pastilles(notes.info)}</div>'
        f'<b>{notes.info}/5</b></div>'
        f'<div class="doc-note"><span>🌀 Chaos</span><div class="doc-pastilles">{_pastilles(notes.chaos)}</div>'
        f'<b>{notes.chaos}/5</b></div>'
        '</div></div>'
    )


def ecran_documentation():
    st.markdown(CSS_SANS_SIDEBAR + CSS_DOCUMENTATION, unsafe_allow_html=True)
    if st.button("← Menu", key="retour_menu_documentation"):
        aller_a("accueil")
    scene_ciel("jour", "Documentation", "Comment jouer, et les rôles du village avec leur poids dans l'équilibre")
    onglet_regles, onglet_roles = st.tabs(["📖 Comment jouer", "🃏 Les rôles"])
    with onglet_regles:
        afficher_regles()
    with onglet_roles:
        st.caption(
            "Force : de -6 (très favorable aux loups) à +7 (très favorable au village). "
            "Information : renseignements que le rôle apporte à son camp. "
            "Chaos : imprévisibilité qu'il ajoute à la partie. Valeurs estimées, détail dans docs/equilibre-roles.md. "
            "La Voyante et le Loup Blanc sont comptés ici à une action par nuit : la cadence choisie à la composition les ajuste."
        )
        st.markdown(
            f'<div class="doc-grille">{"".join(_dalle(r) for r in ROLES.values())}</div>', unsafe_allow_html=True,
        )
