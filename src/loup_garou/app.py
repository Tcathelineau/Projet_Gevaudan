"""Point d'entrée : assemble la page, la barre latérale et l'écran de la phase courante."""

import streamlit as st

from loup_garou.moteur.partie import camp, vivants
from loup_garou.moteur.persistance import clear_save, load_game, save_game
from loup_garou.roles import ROLES
from loup_garou.ui.barre_laterale import garder_sidebar_ouverte, panneau_rechargement
from loup_garou.ui.composants import chronologie_html
from loup_garou.ui.ecrans.accueil import ecran_accueil, ecran_historique
from loup_garou.ui.ecrans.documentation import ecran_documentation
from loup_garou.ui.ecrans.fin import ecran_fin
from loup_garou.ui.ecrans.installation import ecran_installation
from loup_garou.ui.ecrans.jour import ecran_conseil, ecran_election_maire, ecran_reveil, ecran_tir_chasseur
from loup_garou.ui.ecrans.nuit import ecran_nuit
from loup_garou.ui.regles import SECTIONS, afficher_regles, afficher_roles_de_la_partie
from loup_garou.ui.illustrations import ASSETS
from loup_garou.ui.sons import (
    actif, cases_a_cocher, effet_courant, jouer_effet, jouer_musique, musique_courante, vider_session,
)
from loup_garou.ui.styles import CSS_ACCUEIL, css_cartes, CSS_HISTORIQUE, CSS_PASSAGE, CSS_SCENES


def main():
    st.set_page_config(
        page_title="Projet Gévaudan", page_icon=str(ASSETS / "favicon.png"), layout="wide",
        initial_sidebar_state="expanded",
    )
    css_cartes()
    st.markdown(CSS_SCENES, unsafe_allow_html=True)
    st.markdown(CSS_PASSAGE, unsafe_allow_html=True)
    st.markdown(CSS_ACCUEIL + CSS_HISTORIQUE, unsafe_allow_html=True)
    garder_sidebar_ouverte()

    if "partie" not in st.session_state:
        sauvegarde = load_game()
        if sauvegarde:
            st.session_state.partie = sauvegarde
        else:
            ecran = st.session_state.get("ecran", "accueil")
            if ecran == "installation":
                ecran_installation()
            elif ecran == "historique":
                ecran_historique()
            elif ecran == "documentation":
                ecran_documentation()
            else:
                ecran_accueil()
            return

    s = st.session_state.partie

    with st.sidebar:
        # Réservé en premier : sa position ne bouge pas, donc le son en cours n'est pas relancé à chaque clic.
        zone_musique = st.container(key="zone_musique")
        zone_effet = st.container(key="zone_effet")
        secrets = [n for n in vivants(s) if ROLES[s["joueurs"][n]["role"]].camp_secret]
        loups_vivants = sum(
            1 for n in vivants(s) if n not in secrets and camp(s, n) == "loups"
        )
        village_vivants = len(vivants(s)) - loups_vivants - len(secrets)
        ligne_secret = (
            f'<div class="panneau-ligne"><span>❓ Camp secret</span><span>{len(secrets)}</span></div>'
            if secrets else ""
        )
        maire_txt = s.get("maire") or "— (pas encore élu)"
        if s["phase"] == "fin":
            titre_phase = "🏁 Fin de partie"
        elif s["phase"] == "nuit":
            titre_phase = f"🌙 Nuit {s['jour']}"
        else:
            titre_phase = f"☀️ Jour {s['jour']}"

        st.markdown(
            f"""
            <div class="panneau">
                <div class="panneau-titre">{titre_phase}</div>
                <div class="panneau-ligne"><span>👥 Vivants</span><span>{len(vivants(s))} / {s['nb_joueurs']}</span></div>
                <div class="panneau-ligne"><span>🐺 Loups</span><span>{loups_vivants}</span></div>
                <div class="panneau-ligne"><span>🧑‍🌾 Village</span><span>{village_vivants}</span></div>
                {ligne_secret}
            </div>
            <div class="panneau">
                <div class="panneau-ligne"><span>👑 Maire</span><span class="maire-nom">{maire_txt}</span></div>
            </div>
            <div class="panneau">
                <div class="panneau-titre">🕰️ Chronologie</div>
                {chronologie_html(s)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("📖 Rappel des règles"):
            afficher_regles(SECTIONS[1:3])
            st.markdown("**🃏 Les rôles de la partie**")
            afficher_roles_de_la_partie(s)

    # Les écrans de phase (ex. le badge "en couple avec" pendant la nuit)
    # peuvent encore ajouter du contenu à la sidebar : on les appelle avant
    # la musique et le bouton d'abandon pour qu'ils restent en haut, au-dessus
    # du bouton ancré en bas.
    if s["phase"] == "nuit":
        ecran_nuit(s)
    elif s["phase"] == "reveil":
        ecran_reveil(s)
    elif s["phase"] == "election_maire":
        ecran_election_maire(s)
    elif s["phase"] == "conseil":
        ecran_conseil(s)
    elif s["phase"] == "tir_chasseur":
        ecran_tir_chasseur(s)
    else:
        ecran_fin(s)

    with zone_musique:
        if actif("musique_on"):
            jouer_musique(musique_courante(s))
    with zone_effet:
        effet = effet_courant(s)
        if effet and actif("sons_on") and (effet != "hurlement" or actif("cri_on")):
            jouer_effet(effet)

    with st.sidebar:
        # Le menu flotte au-dessus du bouton (position absolue) : il recouvre le reste sans le déplacer.
        with st.container(key="options"):
            if st.session_state.get("options_ouvert"):
                with st.container(key="menu_option"):
                    st.markdown("**🔊 Son** (désactivé par défaut)")
                    cases_a_cocher()
                    panneau_rechargement(s)
                    if s["phase"] == "fin":
                        sortir = st.button("🏠 Retour au menu", key="abandon")
                    elif st.session_state.get("abandon_demande"):
                        st.warning("La partie en cours sera perdue (elle ne sera pas archivée).")
                        sortir = st.button("Oui, abandonner la partie", key="abandon")
                        if st.button("Non, continuer", key="continuer_partie"):
                            st.session_state.abandon_demande = False
                            st.rerun()
                    else:
                        if st.button("🚪 Abandonner la partie", key="abandon_demande_bouton"):
                            st.session_state.abandon_demande = True
                            st.rerun()
                        sortir = False
                    if sortir:
                        clear_save()
                        vider_session()
                        st.rerun()
            ouvert = st.session_state.get("options_ouvert", False)
            st.button(
                "⚙️ Option " + ("▾" if ouvert else "▴"), key="bouton_option",
                on_click=lambda: st.session_state.update(options_ouvert=not ouvert),
            )

    save_game(s)
