"""Menu d'accueil et liste des parties archivées."""

import html
import random
from collections import Counter

import streamlit as st

from loup_garou.moteur.persistance import clear_save, date_partie, gagnant_partie, lister_historique, resume_sauvegarde
from loup_garou.roles import ROLES
from loup_garou.ui.composants import scene_ciel, silhouettes_vent
from loup_garou.ui.illustrations import svg_role
from loup_garou.ui.ecrans.statistiques import afficher_statistiques
from loup_garou.ui.ecrans.fin import afficher_coulisses, afficher_historique, afficher_roles
from loup_garou.ui.styles import CSS_SANS_SIDEBAR


def _fond_accueil():
    """Quatre décors qui se fondent en boucle : jour, nuit, lune de sang, victoire du village."""
    rnd = random.Random(5)
    couleurs = ("#ff5a5a", "#ffd23f", "#4cc9f0", "#7bd88f", "#f78fd0", "#ffffff")
    confettis = "".join(
        f'<span class="ciel-confetti" style="left:{rnd.uniform(1, 99):.1f}%;background:{rnd.choice(couleurs)};'
        f'animation-duration:{rnd.uniform(3.2, 5.6):.1f}s;animation-delay:-{rnd.uniform(0, 5):.1f}s"></span>'
        for _ in range(40)
    )
    chauves = silhouettes_vent()
    return (
        '<div class="acc-fond">'
        '<div class="acc-couche acc-jour"><div class="ciel-astre ciel-soleil"></div></div>'
        '<div class="acc-couche acc-nuit"><div class="ciel-astre ciel-lune"></div></div>'
        '<div class="acc-couche acc-loups"><div class="ciel-astre ciel-lune-sang"></div>' + chauves +
        '<div class="ciel-colline"></div></div>'
        '<div class="acc-couche acc-victoire"><div class="ciel-rayons"></div>'
        '<div class="ciel-astre ciel-soleil-haut"></div>' + confettis + '</div>'
        '</div>'
    )


def aller_a(ecran):
    st.session_state.ecran = ecran
    st.rerun()


def ecran_accueil():
    st.markdown(CSS_SANS_SIDEBAR, unsafe_allow_html=True)
    with st.container(key="scene_accueil"):
        st.markdown(_fond_accueil(), unsafe_allow_html=True)
        st.markdown(
            f'<div class="acc-titre-bloc"><div class="acc-surtitre">{svg_role("logo", "acc-logo", "🐺")}</div>'
            '<div class="acc-titre">Projet Gévaudan</div></div>',
            unsafe_allow_html=True,
        )
        sauvegarde = resume_sauvegarde()
        with st.container(key="accueil_boutons"):
            if sauvegarde:
                _bloc_reprise(sauvegarde)
            elif st.button("🐺 Nouvelle partie", key="accueil_btn_nouvelle", type="primary"):
                aller_a("installation")
            if st.button("📜 Historique", key="accueil_btn_historique"):
                aller_a("historique")
            if st.button("📖 Documentation", key="accueil_btn_documentation"):
                aller_a("documentation")


def _reprendre(partie):
    st.session_state.partie = partie


def _bloc_reprise(sauvegarde):
    """Une partie est sauvegardée : on la propose, et on demande confirmation avant de la remplacer."""
    partie, texte, date = sauvegarde
    st.markdown(
        f'<div class="reprise"><div class="reprise-titre">Partie en cours</div><div>{html.escape(texte)}</div>'
        f'<small>Sauvegardée le {date}</small></div>',
        unsafe_allow_html=True,
    )
    st.button("▶ Reprendre la partie", key="accueil_btn_reprendre", type="primary", on_click=_reprendre, args=(partie,))
    if st.session_state.get("remplacer_demande"):
        st.warning("La partie sauvegardée sera perdue.")
        if st.button("Oui, nouvelle partie", key="accueil_btn_remplacer"):
            clear_save()
            st.session_state.remplacer_demande = False
            aller_a("installation")
        if st.button("Non, la garder", key="accueil_btn_garder"):
            st.session_state.remplacer_demande = False
            st.rerun()
    elif st.button("🐺 Nouvelle partie", key="accueil_btn_nouvelle"):
        st.session_state.remplacer_demande = True
        st.rerun()


def _carte_partie(p):
    _, emoji, mot = gagnant_partie(p["issue"])
    joueurs = p["joueurs"]
    noms = "".join(f'<span class="hc-puce">{html.escape(n)}</span>' for n in joueurs)
    comptes = Counter(d["role"] for d in joueurs.values())
    roles = "".join(
        f'<span class="hc-puce">{ROLES[r].emoji} {html.escape(ROLES[r].nom)}{f" ×{n}" if n > 1 else ""}</span>'
        for r, n in comptes.items() if r in ROLES
    )
    return (
        f'<div class="hc-tete"><span class="hc-gagnant">{emoji} {mot}</span>'
        f'<span class="hc-date">📅 {date_partie(p)}</span></div>'
        f'<div class="hc-ligne"><span class="hc-label">Joueurs</span>{noms}</div>'
        f'<div class="hc-ligne"><span class="hc-label">Rôles</span>{roles}</div>'
    )


def ecran_historique():
    st.markdown(CSS_SANS_SIDEBAR, unsafe_allow_html=True)
    if st.button("← Menu", key="retour_menu_historique"):
        aller_a("accueil")
    scene_ciel("nuit", "Historique des parties", "Les parties terminées, de la plus récente à la plus ancienne")

    parties = lister_historique()
    onglet_parties, onglet_stats = st.tabs(["📜 Parties", "📊 Statistiques"])
    with onglet_stats:
        afficher_statistiques(parties)
    with onglet_parties:
        _liste_parties(parties)


def _liste_parties(parties):
    if not parties:
        st.info("Aucune partie terminée pour l'instant. Les parties abandonnées ne sont pas conservées.")
        return

    victoires = Counter(gagnant_partie(p["issue"])[0] for p in parties)
    bilan = [f"{len(parties)} parties"]
    for cle, emoji, mot in (("village", "🏡", "Village"), ("loups", "🐺", "Loups"),
                            ("couple", "💘", "Couple"), ("loupblanc", "🌕", "Loup Blanc")):
        if victoires[cle]:
            bilan.append(f"{emoji} {mot} {victoires[cle]}")
    st.caption(" · ".join(bilan))
    for i, p in enumerate(parties):
        with st.container(key=f"histo_{gagnant_partie(p['issue'])[0]}_{i}", border=True):
            st.markdown(_carte_partie(p), unsafe_allow_html=True)
            with st.expander("Détails"):
                st.markdown(f"**{len(p['joueurs'])} joueurs**")
                afficher_roles(p["joueurs"])
                st.markdown("**🎭 Les coulisses**")
                afficher_coulisses(p["joueurs"], p["journal"])
                st.markdown("**📜 Journal**")
                afficher_historique(p)
