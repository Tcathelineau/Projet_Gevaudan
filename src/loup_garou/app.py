"""Point d'entrée : assemble la page, la barre latérale et l'écran de la phase courante."""

import os

import streamlit as st

from loup_garou.config import MUSIQUE_FILE
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
from loup_garou.ui.illustrations import ASSETS
from loup_garou.ui.sons import jouer, son_courant
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
        zone_son = st.container(key="zone_son")
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

    with zone_son:
        if st.session_state.get("sons_on", True):
            jouer(son_courant(s, bool(st.session_state.get(f"resultat_{s['jour']}"))))

    with st.sidebar:
        st.checkbox("🔔 Bruitages", value=True, key="sons_on")
        if os.path.exists(MUSIQUE_FILE):
            if st.checkbox("🎵 Musique de fond", value=True, key="musique_on"):
                st.audio(MUSIQUE_FILE, format="audio/mp3", loop=True, autoplay=True)

        # Le menu flotte au-dessus du bouton (position absolue) : il recouvre le reste sans le déplacer.
        with st.container(key="options"):
            if st.session_state.get("options_ouvert"):
                with st.container(key="menu_option"):
                    panneau_rechargement(s)
                    libelle = "🏠 Retour au menu" if s["phase"] == "fin" else "🚪 Abandonner la partie"
                    if st.button(libelle, key="abandon"):
                        clear_save()
                        st.session_state.clear()
                        st.rerun()
            ouvert = st.session_state.get("options_ouvert", False)
            st.button(
                "⚙️ Option " + ("▾" if ouvert else "▴"), key="bouton_option",
                on_click=lambda: st.session_state.update(options_ouvert=not ouvert),
            )

    save_game(s)
