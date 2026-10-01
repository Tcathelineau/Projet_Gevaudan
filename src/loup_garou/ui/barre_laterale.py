"""Éléments de la barre latérale : rechargement d'étape et maintien de son ouverture."""

import copy

import streamlit.components.v1 as components
import streamlit as st


def recharger_etape(s, cle):
    """Revient à l'étape `cle` : tout ce qui a suivi est oublié."""
    instantanes = s["instantanes"]
    i = next(i for i, inst in enumerate(instantanes) if inst["id"] == cle)
    nouvel = copy.deepcopy(instantanes[i]["etat"])
    nouvel["instantanes"] = instantanes[: i + 1]
    # Les saisies en cours d'écran (sélections, résultats de vision...) vivent dans session_state.
    for k in list(st.session_state.keys()):
        if k != "musique_on":
            del st.session_state[k]
    st.session_state.partie = nouvel
    st.rerun()


def panneau_rechargement(s):
    instantanes = s.get("instantanes", [])
    if not instantanes:
        return
    libelles = {inst["id"]: inst["libelle"] for inst in instantanes}
    st.markdown("**⏪ Recharger une étape**")
    st.caption("Revient au début de la nuit ou à l'annonce du jour choisi. Ce qui a suivi est oublié.")
    cle = st.selectbox(
        "Étape", list(reversed(libelles)), index=None, placeholder="Choisir une étape…",
        format_func=libelles.get, label_visibility="collapsed", key="reload_choix",
    )
    if st.button("Recharger cette étape", disabled=cle is None, key="reload_ok"):
        recharger_etape(s, cle)


def garder_sidebar_ouverte():
    """Streamlit mémorise dans le navigateur qu'on a replié la barre latérale, et la replie d'office
    sur petit écran. Comme on masque son bouton de réouverture, on la rouvre par script."""
    script = """<script>
        const doc = window.parent.document;
        setInterval(() => {
            const bouton = doc.querySelector('[data-testid="stExpandSidebarButton"] button, [data-testid="stExpandSidebarButton"]');
            if (bouton) bouton.click();
        }, 400);
        </script>"""
    # st.components.v1.html est déprécié au profit de st.iframe (absent des versions plus anciennes).
    if hasattr(st, "iframe"):
        st.iframe(script, height=1)
    else:
        components.html(script, height=0)
