"""Page de statistiques : ce que disent les parties archivées."""

import streamlit as st

from loup_garou.moteur.statistiques import statistiques
from loup_garou.roles import ROLES
from loup_garou.ui.styles import CSS_BILAN

PEU_DE_DONNEES = 5  # sous ce nombre de parties, un pourcentage ne veut presque rien dire


def _barre(libelle, pct, detail="", faible=False):
    classe = " stat-faible" if faible else ""
    return (
        f'<div class="stat-ligne{classe}"><span class="stat-nom">{libelle}</span>'
        f'<div class="jauge-piste jauge-piste-simple"><div class="jauge-rempli" style="width: {pct:.0f}%;"></div></div>'
        f'<span class="stat-val">{pct:.0f} %</span><span class="stat-detail">{detail}</span></div>'
    )


def afficher_statistiques(parties):
    st.markdown(CSS_BILAN, unsafe_allow_html=True)
    if not parties:
        st.info("Aucune partie terminée pour l'instant : les statistiques apparaîtront ici.")
        return
    stats = statistiques(parties)
    total = stats["total"]
    victoires = stats["victoires"]
    tuiles = (
        ("🎲", "Parties", total),
        ("👥", "Joueurs en tout", stats["joueurs"]),
        ("🏡", "Victoires du village", f"{100 * victoires.get('village', 0) / total:.0f} %"),
        ("🐺", "Victoires des loups", f"{100 * victoires.get('loups', 0) / total:.0f} %"),
        ("💘", "Autres issues", victoires.get("couple", 0) + victoires.get("loupblanc", 0) + victoires.get("autre", 0)),
    )
    st.markdown(
        '<div class="bil-tuiles">' + "".join(
            f'<div class="bil-tuile"><span class="bil-emoji">{e}</span><b>{v}</b><span>{lib}</span></div>'
            for e, lib, v in tuiles
        ) + "</div>",
        unsafe_allow_html=True,
    )
    if total < PEU_DE_DONNEES:
        st.caption(f"Seulement {total} partie(s) : ces pourcentages bougeront beaucoup avec les suivantes.")

    st.subheader("Victoire du village selon la taille de la table")
    st.markdown("".join(
        _barre(libelle, 100 * taux, f"{n} partie{'s' if n > 1 else ''}", n < PEU_DE_DONNEES)
        for libelle, n, taux in stats["tailles"] if n
    ) or "_Pas encore de données._", unsafe_allow_html=True)

    st.subheader("Les rôles")
    st.caption("Taux de victoire : part des joueurs de ce rôle dont le camp a gagné. Les lignes grisées reposent sur moins de "
               f"{PEU_DE_DONNEES} apparitions.")
    lignes = "".join(
        _barre(f"{ROLES[cle].emoji} {ROLES[cle].nom}", 100 * taux_v, f"{n} fois · {100 * taux_s:.0f} % en vie à la fin", n < PEU_DE_DONNEES)
        for cle, n, taux_v, taux_s in stats["roles"]
    )
    st.markdown(lignes, unsafe_allow_html=True)
