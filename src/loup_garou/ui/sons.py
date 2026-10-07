"""Musiques (CC0, outils/importer_musiques.py) et bruitages synthétisés (outils/generer_sons.py) de assets/sons.

Deux lecteurs invisibles, créés à position fixe dans la barre latérale : la musique de la phase en cours
et un bruitage ponctuel. Streamlit ne remonte un lecteur (donc ne relance le son) que si son contenu change,
la musique ne repart donc pas à chaque clic d'une même phase.
"""

import os
from functools import lru_cache

import streamlit as st

from loup_garou.config import MUSIQUE_FILE
from loup_garou.moteur.partie import camp
from loup_garou.moteur.persistance import load_preferences, maj_preferences
from loup_garou.roles import ROLES
from loup_garou.ui.illustrations import ASSETS


@lru_cache(maxsize=None)
def _octets(fichier):
    return (ASSETS / "sons" / fichier).read_bytes()


def musique_courante(s):
    """Nom de la musique de l'écran affiché, ou None : nuit inquiétante, jour sobre, conseil tendu.
    La tension du conseil commence dès le réveil quand la nuit a fait des morts."""
    phase = s["phase"]
    if phase == "reveil":
        return "musique_conseil" if s.get("morts_nuit") else "musique_jour"
    return {
        "nuit": "musique_nuit",
        "election_maire": "musique_conseil",
        "conseil": "musique_conseil",
        "tir_chasseur": "musique_conseil",
    }.get(phase)


def _un_gentil_meurt(s, morts):
    return any(camp(s, n) != "loups" for n in morts)


def effet_courant(s, morts_du_vote=()):
    """Bruitage de l'écran affiché : coup de gong quand un innocent meurt (réveil ou verdict du village),
    hurlement quand un loup découvre sa carte, cri de victoire à la fin."""
    if s["phase"] == "fin":
        message = s.get("message_fin", "")
        gagnant_village = message.startswith(("Le village a gagné", "Les amoureux"))
        return "victoire_village" if gagnant_village else "victoire_loups"
    if s["phase"] == "reveil" and _un_gentil_meurt(s, s.get("morts_nuit", [])):
        return "mort_gentil"
    if s["phase"] == "conseil" and morts_du_vote and _un_gentil_meurt(s, morts_du_vote):
        return "mort_gentil"
    if s["phase"] == "nuit" and s.get("devoile") and s["tour"] < len(s.get("ordre_nuit", [])):
        # Une seule fois par joueur : la première fois qu'il découvre qu'il est loup (la clé garde le son
        # affiché pendant tout son tour, sinon il disparaîtrait au premier clic).
        d = s["joueurs"][s["ordre_nuit"][s["tour"]]]
        if ROLES[d["role"]].camp == "loups" and d.get("cri_loup") in (None, f"{s['jour']}_{s['tour']}"):
            return "hurlement"
    return None


def marquer_cri(s):
    """Note que le joueur en cours a entendu son hurlement (à appeler quand il est réellement joué)."""
    s["joueurs"][s["ordre_nuit"][s["tour"]]]["cri_loup"] = f"{s['jour']}_{s['tour']}"


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
    "sons_on": "🔔 Bruitages (morts, victoire du village)",
    "cri_on": "🐺 Hurlement d'un loup à la révélation de sa carte",
}


def actif(cle):
    return bool(st.session_state.get(cle, False))


def _memoriser(cle):
    st.session_state[cle] = st.session_state[f"case_{cle}"]
    maj_preferences(son={c: actif(c) for c in REGLAGES})


def charger_preferences_son():
    """Reprend les réglages du son de la dernière session (désactivés tant qu'on ne les a pas activés une fois)."""
    if "prefs_son_chargees" in st.session_state:
        return
    st.session_state["prefs_son_chargees"] = True
    for cle, valeur in load_preferences().get("son", {}).items():
        if cle in REGLAGES and cle not in st.session_state:
            st.session_state[cle] = bool(valeur)


def cases_a_cocher():
    """Les cases du menu Option. Le réglage vit sous sa propre clé : une case non affichée (menu fermé) perdrait le sien."""
    for cle, libelle in REGLAGES.items():
        st.checkbox(libelle, value=actif(cle), key=f"case_{cle}", on_change=_memoriser, args=(cle,))


def vider_session():
    """Efface la partie de la session en gardant les réglages du son."""
    reglages = {cle: st.session_state[cle] for cle in (*REGLAGES, "prefs_son_chargees") if cle in st.session_state}
    st.session_state.clear()
    st.session_state.update(reglages)


def effet_autorise(effet):
    """Les hurlements se règlent à part (ils trahissent le camp) ; la victoire des loups sonne aussi si l'un des deux est activé."""
    if effet == "hurlement":
        return actif("cri_on")
    if effet == "victoire_loups":
        return actif("sons_on") or actif("cri_on")
    return actif("sons_on")
