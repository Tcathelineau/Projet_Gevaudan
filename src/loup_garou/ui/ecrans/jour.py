"""Écrans du jour : réveil, élection du maire, conseil du village, tir du chasseur."""

import html

import streamlit as st

from loup_garou.moteur.journal import log
from loup_garou.moteur.partie import camp, servante_prend_role, terminer_partie, tuer, vainqueur, vivants
from loup_garou.roles import ROLES
from loup_garou.ui.composants import (
    annonce,
    bouton_validation,
    grille_dalles,
    panneau_avis,
    plaquette,
    scene_ciel,
    selection_dalles,
)


def _camp_txt(s, nom):
    role = ROLES[s["joueurs"][nom]["role"]]
    if s["joueurs"][nom].get("role_pris_par"):
        return "avait un rôle désormais repris par la servante dévouée : son camp reste secret"
    if role.camp_secret:
        return f"était le {role.nom.upper()} : son camp reste secret jusqu'à la fin"
    return "était LOUP-GAROU" if camp(s, nom) == "loups" else "n'était pas loup-garou"


def panneau_morts(s):
    """Annonce des morts de la nuit, façon panneau d'affichage du village."""
    papiers = []
    for mort in s["morts_nuit"]:
        papiers.append(
            f'<div class="avis-papier"><div class="avis-nom">💀 {html.escape(mort)}</div>'
            f'<div class="avis-detail">Il {_camp_txt(s, mort)}.</div></div>'
        )
    if s["morts_nuit"] and s["amoureux"] and set(s["amoureux"]) <= set(s["morts_nuit"]):
        papiers.append(
            '<div class="avis-papier"><div class="avis-detail">💔 Les amoureux sont morts ensemble.</div></div>'
        )
    if not papiers:
        papiers.append(
            '<div class="avis-papier avis-papier-calme"><div class="avis-nom">🕊️ Nul n\'a péri</div>'
            '<div class="avis-detail">Le village a passé une nuit paisible.</div></div>'
        )
    panneau_avis("Avis à la population", "Premier jour" if s["jour"] == 0 else f"Jour {s['jour']}", papiers)


def panneau_vote(s, morts, sous=None):
    """Verdict du vote du village : vert si un loup tombe, rouge sinon, ambre si son camp reste secret."""
    papiers = []
    for i, mort in enumerate(morts):
        if ROLES[s["joueurs"][mort]["role"]].camp_secret or s["joueurs"][mort].get("role_pris_par"):
            classe = " avis-papier-secret"
        elif camp(s, mort) == "loups":
            classe = " avis-papier-loup"
        else:
            classe = ""
        entete = "⚖️" if i == 0 else "💔"
        detail = f"Il {_camp_txt(s, mort)}."
        if i > 0:
            detail = f"Mort de chagrin (amoureux). {detail}"
        papiers.append(
            f'<div class="avis-papier{classe}"><div class="avis-nom">{entete} {html.escape(mort)}</div>'
            f'<div class="avis-detail">{detail}</div></div>'
        )
    panneau_avis("Sentence du village", sous or f"Jour {s['jour']}", papiers)


def annonce_tirs(s):
    for mort in s.get("morts_tir", []):
        annonce(f"{mort} a été abattu par le chasseur. Il {_camp_txt(s, mort)}.", "!", "danger")


def bouton_tir(s, retour):
    """Bouton menant à l'écran de tir s'il reste un chasseur à faire tirer."""
    chasseur = s["tirs_en_attente"][0]
    annonce(f"{chasseur} était le chasseur : il peut tirer sa dernière balle.", "!")
    if st.button("🔫 Le chasseur décide", type="primary", key=f"bouton_tir_{retour}"):
        s["retour_tir"] = retour
        s["phase"] = "tir_chasseur"
        st.rerun()


def ecran_reveil(s):
    scene_ciel("jour", "Le village se réveille", "Premier jour" if s["jour"] == 0 else f"Jour {s['jour']}")
    panneau_morts(s)
    annonce_tirs(s)

    if s.get("tirs_en_attente"):
        bouton_tir(s, "reveil")
        return

    gagnant = vainqueur(s)
    if gagnant:
        if st.button("Voir le résultat", type="primary"):
            terminer_partie(s, gagnant)
            st.rerun()
        return

    texte = "Passer au premier conseil" if s["jour"] == 0 else "Ouvrir le conseil du village"
    if st.button(texte, type="primary"):
        s["morts_tir"] = []
        if s["jour"] > 0 and s.get("maire") is None:
            s["phase"] = "election_maire"
        else:
            s["phase"] = "conseil"
        st.rerun()


def ecran_election_maire(s):
    ancien = s.get("dernier_maire")
    st.title("👑 Succession du maire" if ancien else "👑 Élection du maire")

    if ancien:
        annonce(f"{ancien} était le maire et il est mort : il désigne lui-même son successeur.", "!")
        st.caption(f"{ancien} choisit son successeur, puis saisis ici son choix.")
        st.markdown(f"**{ancien} désigne comme maire**")
    else:
        st.caption("Débattez et votez à voix haute comme d'habitude, puis saisis ici le nom élu.")
        st.markdown("**Le village élit comme maire**")

    choix = selection_dalles("maire", s["jour"], vivants(s), 1)
    elu = choix[0] if choix else None
    if bouton_validation(
        f"Valider : {elu} est maire" if elu else ("Valider le choix" if ancien else "Valider l'élection"),
        "valider_maire", disabled=elu is None,
    ):
        s["maire"] = elu
        log(s, f"{ancien} désigne {elu} comme successeur." if ancien else f"{elu} est élu maire.")
        s["dernier_maire"] = None
        st.session_state.pop(f"sel_maire_{s['jour']}", None)
        gagnant = vainqueur(s)
        if gagnant:
            terminer_partie(s, gagnant)
        else:
            s["phase"] = "conseil"
        st.rerun()


def _servante_vivante(s, exclure):
    return any(s["joueurs"][n]["role"] == "servante" for n in vivants(s) if n != exclure)


def _condamner(s, condamne, cle_resultat):
    """Rend le verdict : le joueur meurt et son camp est révélé."""
    s["vote_en_attente"] = None
    for cle in (f"servante_oui_{cle_resultat}", f"servante_erreur_{cle_resultat}"):
        st.session_state.pop(cle, None)
    st.session_state[cle_resultat] = tuer(s, condamne, "est éliminé par le village")
    st.rerun()


def _intervention_servante(s, cle_resultat):
    """Entre la désignation du condamné et la révélation de son camp, la servante dévouée peut se manifester."""
    condamne = s["vote_en_attente"]
    annonce(
        f"Le village a désigné {condamne}. Avant que son camp soit révélé, "
        "la servante dévouée peut se manifester pour reprendre son rôle.", "?", "mystere",
    )
    cle_oui = f"servante_oui_{cle_resultat}"
    erreur = st.session_state.get(f"servante_erreur_{cle_resultat}")
    if erreur:
        plaquette(f"{erreur} n'est pas la servante dévouée.", icone="🧹")
    if not st.session_state.get(cle_oui):
        if st.button("Personne ne se manifeste", type="primary", key=f"servante_non_{cle_resultat}"):
            _condamner(s, condamne, cle_resultat)
        if st.button("🧹 Je suis la servante dévouée", key=f"servante_moi_{cle_resultat}"):
            st.session_state[cle_oui] = True
            st.rerun()
        return

    st.markdown("**Qui es-tu ?**")
    qui = grille_dalles("serv", cle_resultat, [n for n in vivants(s) if n != condamne])
    if st.button("Annuler", key=f"servante_annule_{cle_resultat}"):
        st.session_state.pop(cle_oui, None)
        st.rerun()
    if qui:
        if s["joueurs"][qui]["role"] == "servante":
            servante_prend_role(s, qui, condamne)
            _condamner(s, condamne, cle_resultat)
        st.session_state[f"servante_erreur_{cle_resultat}"] = qui
        st.session_state.pop(cle_oui, None)
        st.rerun()


def _saisie_vote(s, rang):
    """Vote du village : `rang` 1 pour le premier, 2 pour le second exigé par le juge bègue."""
    cle_sel = s["jour"] if rang == 1 else f"{s['jour']}b"
    cle_resultat = f"resultat_{s['jour']}" if rang == 1 else f"resultat2_{s['jour']}"
    if s.get("vote_en_attente"):
        _intervention_servante(s, cle_resultat)
        return

    if rang == 1:
        st.caption("Débattez à voix haute, puis le capitaine saisit le résultat du vote.")
    else:
        annonce("Le juge bègue exige un second vote : le village se prononce à nouveau.", "!")
    st.markdown("**Le village élimine**")
    choix = selection_dalles("vote", cle_sel, vivants(s), 1)
    condamne = choix[0] if choix else None
    if bouton_validation(
        f"Valider : éliminer {condamne}" if condamne else "Valider le vote",
        "valider_vote" if rang == 1 else "valider_vote2", disabled=condamne is None,
    ):
        st.session_state.pop(f"sel_vote_{cle_sel}", None)
        if _servante_vivante(s, condamne):
            s["vote_en_attente"] = condamne
            st.rerun()
        _condamner(s, condamne, cle_resultat)


def ecran_conseil(s):
    resultat = None if s["jour"] == 0 else st.session_state.get(f"resultat_{s['jour']}")
    resultat2 = None if s["jour"] == 0 else st.session_state.get(f"resultat2_{s['jour']}")
    if resultat:
        scene_ciel("jour", "Le village a tranché", f"Jour {s['jour']}")
    else:
        st.title("🗳️ Conseil du village")

    if s["jour"] == 0:
        annonce("Première nuit passée : pas de vote aujourd'hui.", "?", "mystere")
        if st.button("La nuit retombe", type="primary"):
            s["jour"] += 1
            s["phase"] = "nuit"
            st.rerun()
        return

    if not resultat:
        _saisie_vote(s, 1)
        return

    panneau_vote(s, resultat)
    if resultat2:
        panneau_vote(s, resultat2, "Second vote")
    annonce_tirs(s)

    gagnant = vainqueur(s)
    if s.get("tirs_en_attente"):
        bouton_tir(s, "conseil")
    elif gagnant:
        if st.button("Voir le résultat", type="primary"):
            terminer_partie(s, gagnant)
            st.rerun()
    elif s.get("second_vote") == s["jour"] and not resultat2:
        _saisie_vote(s, 2)
    elif st.button("La nuit tombe", type="primary"):
        s["jour"] += 1
        s["phase"] = "nuit"
        st.rerun()


def ecran_tir_chasseur(s):
    chasseur = s["tirs_en_attente"][0]
    st.title("🔫 Dernière balle")
    annonce(
        f"{chasseur} était le chasseur et vient de mourir. "
        "Il peut désigner quelqu'un qui mourra sur-le-champ, ou renoncer à tirer.", "!",
    )

    cibles = vivants(s)
    cle_cible = f"tir_cible_{s['jour']}_{chasseur}"
    clic = grille_dalles("tir", s["jour"], cibles)
    if clic:
        st.session_state[cle_cible] = clic
        st.rerun()

    choix = st.session_state.get(cle_cible)
    if choix not in cibles:
        choix = None
    if choix:
        plaquette(f"Cible choisie : {choix}", icone="🎯")

    tirer = bouton_validation(
        f"🔫 Tirer sur {choix}" if choix else "🔫 Tirer", "tir_confirmer", disabled=choix is None,
    )
    with st.container(key="validation_tir_renoncer"):
        renoncer = st.button("Renoncer à tirer", key="tir_renoncer")

    if tirer or renoncer:
        s["tirs_en_attente"].pop(0)
        if tirer:
            s["morts_tir"] += tuer(s, choix, f"est abattu par le chasseur {chasseur}")
        else:
            log(s, f"Le chasseur {chasseur} renonce à tirer.")
        st.session_state.pop(cle_cible, None)
        if not s["tirs_en_attente"]:
            s["phase"] = s["retour_tir"]
        st.rerun()
