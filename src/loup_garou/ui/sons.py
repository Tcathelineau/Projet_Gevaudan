"""Musiques (CC0, outils/importer_musiques.py) et bruitages synthétisés (outils/generer_sons.py) de assets/sons.

Deux lecteurs invisibles, créés à position fixe dans la barre latérale : la musique de la phase en cours
et un bruitage ponctuel. Streamlit ne remonte un lecteur (donc ne relance le son) que si son contenu change,
la musique ne repart donc pas à chaque clic d'une même phase.
"""

import os
from functools import lru_cache

import streamlit as st

from loup_garou.config import MUSIQUE_FILE
from loup_garou.roles import ROLES
from loup_garou.ui.illustrations import ASSETS


@lru_cache(maxsize=None)
def _octets(fichier):
    return (ASSETS / "sons" / fichier).read_bytes()


def musique_courante(s):
    """Nom de la musique de l'écran affiché (nuit inquiétante, jour joyeux, conseil tendu), ou None."""
    return {
        "nuit": "musique_nuit",
        "reveil": "musique_jour",
        "election_maire": "musique_jour",
        "conseil": "musique_conseil",
        "tir_chasseur": "musique_conseil",
    }.get(s["phase"])


def effet_courant(s):
    """Bruitage de l'écran affiché : hurlement quand un loup découvre sa carte, cri de victoire à la fin."""
    if s["phase"] == "fin":
        message = s.get("message_fin", "")
        gagnant_village = message.startswith(("Le village a gagné", "Les amoureux"))
        return "victoire_village" if gagnant_village else "victoire_loups"
    if s["phase"] == "nuit" and s.get("devoile") and s["tour"] < len(s.get("ordre_nuit", [])):
        # Une seule fois par joueur : la première fois qu'il découvre qu'il est loup (la clé garde le son
        # affiché pendant tout son tour, sinon il disparaîtrait au premier clic).
        d = s["joueurs"][s["ordre_nuit"][s["tour"]]]
        tour = f"{s['jour']}_{s['tour']}"
        if ROLES[d["role"]].camp == "loups" and d.get("cri_loup") in (None, tour):
            d["cri_loup"] = tour
            return "hurlement"
    return None


def jouer_musique(nom):
    """Musique de la phase en boucle ; un fichier `musique.mp3` posé par l'utilisateur la remplace."""
    if os.path.exists(MUSIQUE_FILE):
        st.audio(MUSIQUE_FILE, format="audio/mpeg", loop=True, autoplay=True)
    elif nom:
        st.audio(_octets(f"{nom}.mp3"), format="audio/mpeg", loop=True, autoplay=True)


def jouer_effet(nom):
    if nom:
        st.audio(_octets(f"{nom}.wav"), format="audio/wav", autoplay=True)


# Réglages du son : désactivé par défaut (rien ne doit jouer à l'arrivée sur la page), activé depuis le menu Option.
REGLAGES = {
    "musique_on": "🎵 Musique",
    "sons_on": "🔔 Bruitages (victoire)",
    "cri_on": "🐺 Hurlement d'un loup à la révélation de sa carte",
}


def actif(cle):
    return bool(st.session_state.get(cle, False))


def _memoriser(cle):
    st.session_state[cle] = st.session_state[f"case_{cle}"]


def cases_a_cocher():
    """Les cases du menu Option. Le réglage vit sous sa propre clé : une case non affichée (menu fermé) perdrait le sien."""
    for cle, libelle in REGLAGES.items():
        st.checkbox(libelle, value=actif(cle), key=f"case_{cle}", on_change=_memoriser, args=(cle,))


def vider_session():
    """Efface la partie de la session en gardant les réglages du son."""
    reglages = {cle: st.session_state[cle] for cle in REGLAGES if cle in st.session_state}
    st.session_state.clear()
    st.session_state.update(reglages)
