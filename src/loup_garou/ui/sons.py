"""Bruitages synthétisés (assets/sons, cf. outils/generer_sons.py) : un son par moment de la partie."""

from functools import lru_cache

import streamlit as st

from loup_garou.ui.illustrations import ASSETS


@lru_cache(maxsize=None)
def _octets(nom):
    return (ASSETS / "sons" / f"{nom}.wav").read_bytes()


def son_courant(s, resultat_vote=False):
    """(nom du son, en boucle ?) pour l'écran affiché, ou None. Les sons ponctuels ne se rejouent pas
    tant que l'écran reste le même : Streamlit ne remonte l'élément audio que si le son change."""
    phase = s["phase"]
    if phase == "nuit":
        return "nuit", True
    if phase == "reveil":
        return ("mort" if s["morts_nuit"] else "jour"), False
    if phase == "conseil" and resultat_vote:
        return "mort", False
    if phase == "fin":
        message = s.get("message_fin", "")
        if message.startswith("Le village a gagné"):
            return "victoire_village", False
        return "victoire_loups", False
    return None


def jouer(choix):
    """Insère un lecteur audio invisible qui démarre tout seul (le joueur a déjà cliqué dans la page)."""
    if choix is None:
        return
    nom, boucle = choix
    st.audio(_octets(nom), format="audio/wav", loop=boucle, autoplay=True)
