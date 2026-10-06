"""Écran de la nuit : passage de l'appareil de joueur en joueur."""

import streamlit as st

from loup_garou.moteur.journal import prendre_instantane
from loup_garou.moteur.partie import resoudre_nuit, vivants
from loup_garou.options import opt
from loup_garou.roles import ROLES
from loup_garou.ui.composants import badge_amour, bouton_fin, bouton_validation, carte_dos, carte_role, plaquette
from loup_garou.ui.nuit_roles import NUIT_ROLES


def ecran_nuit(s):
    if not s["ordre_nuit"]:
        prendre_instantane(s, "nuit")
        s["servante_nuit"] = None
        # Voleur puis Chien-Loup jouent en premier (cf. priorite_nuit) : leur choix de
        # rôle ou de camp doit être fait avant que les autres ne découvrent la meute.
        s["ordre_nuit"] = sorted(vivants(s), key=lambda n: ROLES[s["joueurs"][n]["role"]].priorite_nuit)
        s["tour"] = 0
        s["devoile"] = False
        s["transfert"] = False

    if s["tour"] >= len(s["ordre_nuit"]):
        resoudre_nuit(s)
        st.rerun()

    nom = s["ordre_nuit"][s["tour"]]
    donnees = s["joueurs"][nom]
    role = donnees["role"]

    st.caption(f"Nuit {s['jour']} — joueur {s['tour'] + 1} sur {len(s['ordre_nuit'])}")

    if not s["transfert"]:
        with st.container(key="scene_passage"):
            if s["tour"] == 0:
                st.header("🌙 La nuit tombe")
                sous_titre = "Première nuit" if s["jour"] == 0 else f"Nuit {s['jour']}"
                st.markdown(f'<div class="passage-sous">{sous_titre}</div>', unsafe_allow_html=True)
            else:
                st.header("🔄 Changement de joueur")
            carte_dos()
            if bouton_validation(f"Je vais chercher {nom}", f"transfert_{s['jour']}_{s['tour']}"):
                s["transfert"] = True
                st.rerun()
        return

    if not s["devoile"]:
        with st.container(key="scene_passage"):
            st.header(f"C'est ton tour, {nom}")
            carte_dos()
            plaquette("Confirme que c'est bien toi avant de voir ton rôle.", icone="🗝️")
            if bouton_validation(f"Oui, je suis {nom}", f"pret_{s['jour']}_{s['tour']}"):
                s["devoile"] = True
                st.rerun()
        return

    st.header("🃏 Ta carte")
    carte_role(nom, role)
    cle = f"{s['jour']}_{s['tour']}"

    with st.container(height=400, border=False):
        if (s.get("servante_nuit") or {}).get("servante") == nom:
            plaquette(
                f"Tu as repris le rôle de {s['servante_nuit']['mort']} : voici ta nouvelle carte. "
                "Tu la joueras dès la nuit prochaine ; le village apprendra demain que la servante est intervenue.",
                icone="🧹", ton="succes",
            )
            bouton_fin(s, cle)
        else:
            gerer_nuit = NUIT_ROLES.get(role, NUIT_ROLES["villageois"])
            gerer_nuit(s, nom, cle)

    if donnees["amoureux"] and (s["jour"] > 0 or opt(s, "couple_hasard")):
        autres = [n for n in s["amoureux"] if n != nom]
        with st.sidebar:
            badge_amour(autres)
