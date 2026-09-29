"""
Loup-Garou — version Streamlit (jeu en hotseat : on se passe l'écran).

Lancement :  streamlit run loup_garou_app.py
"""

import json
import os
import random
from collections import Counter
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, Optional

import streamlit as st

SAVE_FILE = "save.json"
HISTORIQUE_DIR = "parties"
MUSIQUE_FILE = "musique.mp3"

PHASE_EMOJI = {
    "nuit": "🌙",
    "reveil": "🌅",
    "election_maire": "👑",
    "conseil": "🗳️",
    "tir_chasseur": "🔫",
    "fin": "🏁",
}

PHASE_LABEL = {
    "nuit": "Nuit",
    "reveil": "Réveil",
    "election_maire": "Élection du maire",
    "conseil": "Conseil",
    "tir_chasseur": "Dernière balle",
    "fin": "Fin",
}


def css_cartes():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=EB+Garamond:ital@0;1&display=swap');

        .block-container {
            padding-top: 2rem;
            padding-bottom: 1rem;
        }
        #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0;
        }

        .carte {
            width: min(230px, 60vw);
            aspect-ratio: 5 / 7;
            margin: 0.8rem auto 1rem auto;
            border-radius: 14px;
            border: 3px solid #c9a44c;
            box-shadow: 0 0 0 1px rgba(201,164,76,.35) inset, 0 16px 34px rgba(0,0,0,.55);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0.8rem 0.9rem 0.8rem;
            position: relative;
            font-family: 'EB Garamond', serif;
            color: #f2e9d8;
        }
        .carte::before, .carte::after,
        .carte .coin-bd, .carte .coin-bg {
            content: "✦";
            position: absolute;
            color: #c9a44c;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        .carte::before { top: 10px; left: 12px; }
        .carte::after { top: 10px; right: 12px; }
        .carte .coin-bd { bottom: 10px; right: 12px; }
        .carte .coin-bg { bottom: 10px; left: 12px; }

        .carte-titre {
            font-family: 'Cinzel', serif;
            font-variant: small-caps;
            letter-spacing: 0.12em;
            font-size: 1.15rem;
            font-weight: 700;
            text-align: center;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(201,164,76,.5);
            width: 80%;
        }
        .carte-medaillon {
            width: 78px;
            height: 78px;
            border-radius: 50%;
            border: 2px solid #c9a44c;
            background: rgba(0,0,0,.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.1rem;
            box-shadow: 0 0 22px rgba(201,164,76,.25) inset;
        }
        .carte-nom {
            font-family: 'Cinzel', serif;
            font-size: 1.3rem;
            font-weight: 600;
            text-align: center;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(201,164,76,.5);
            width: 80%;
        }
        .carte-dos {
            width: min(230px, 60vw);
            aspect-ratio: 5 / 7;
            margin: 0.8rem auto 1rem auto;
            border-radius: 14px;
            border: 3px solid #c9a44c;
            background:
                repeating-linear-gradient(45deg, rgba(201,164,76,.08) 0 2px, transparent 2px 14px),
                radial-gradient(circle at 50% 50%, #1c1c2e, #0a0a12 80%);
            box-shadow: 0 0 0 1px rgba(201,164,76,.35) inset, 0 16px 34px rgba(0,0,0,.55);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.4rem;
        }
        .badge-amour {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1rem 0;
            padding: 0.8rem 1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(216,74,110,.22), rgba(201,164,76,.10));
            border: 1.5px solid #d84a6e;
            box-shadow: 0 0 16px rgba(216,74,110,.35);
        }
        .badge-icone { font-size: 1.8rem; line-height: 1; }
        .badge-label {
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #e3b8c4;
            opacity: 0.85;
        }
        .badge-nom {
            font-family: 'Cinzel', serif;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #ffd7e0;
        }
        .badge-sous {
            font-size: 0.78rem;
            color: #e3b8c4;
            opacity: 0.9;
        }
        .badge-meute {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 0.6rem 0 1rem 0;
            padding: 0.8rem 1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(140,30,34,.28), rgba(201,164,76,.08));
            border: 1.5px solid #a3383c;
            box-shadow: 0 0 16px rgba(163,56,60,.35);
        }
        .badge-meute-label {
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #e3a3a5;
            opacity: 0.85;
        }
        .badge-meute-noms {
            font-family: 'Cinzel', serif;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: #ffd0d0;
        }
        .plaquette {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 0.7rem 0;
            padding: 0.8rem 1.1rem;
            border-radius: 8px;
            background: rgba(20,16,10,.5);
            border: 1px solid rgba(201,164,76,.4);
            border-left: 3px solid rgba(201,164,76,.7);
        }
        .plaquette-icone { font-size: 1.4rem; flex-shrink: 0; }
        .plaquette-texte {
            font-family: 'EB Garamond', serif;
            font-style: italic;
            font-size: 1.05rem;
            color: #ece3d2;
        }
        .plaquette-succes { border-left-color: rgba(122,168,116,.85); }
        .plaquette-danger { border-left-color: rgba(190,80,80,.85); }

        div[class*="st-key-pret_"] button {
            background-color: #3f7d4f;
            border-color: #2f5f3b;
            color: #f2e9d8;
        }
        div[class*="st-key-pret_"] button:hover {
            background-color: #4a9059;
            border-color: #3f7d4f;
            color: #ffffff;
        }
        div[class*="st-key-pret_"] button:active {
            background-color: #356745;
        }
        .panneau {
            border-radius: 10px;
            border: 1px solid rgba(201,164,76,.4);
            background: rgba(20,16,10,.4);
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }
        .panneau-titre {
            font-family: 'Cinzel', serif;
            font-size: 1.05rem;
            font-weight: 600;
            color: #f2e9d8;
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(201,164,76,.35);
        }
        .panneau-ligne {
            display: flex;
            justify-content: space-between;
            font-family: 'EB Garamond', serif;
            font-size: 0.98rem;
            color: #ece3d2;
            padding: 0.15rem 0;
        }
        .panneau-dense { padding: 0.6rem 0.9rem; margin-bottom: 0.6rem; }
        .panneau-dense .panneau-titre {
            font-size: 0.95rem;
            padding-bottom: 0.3rem;
            margin-bottom: 0.35rem;
        }
        .panneau-dense .panneau-ligne { font-size: 0.92rem; padding: 0.05rem 0; }
        .panneau-grille {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            column-gap: 1.4rem;
        }
        .panneau-total {
            border-top: 1px solid rgba(201,164,76,.35);
            margin-top: 0.35rem;
            padding-top: 0.3rem;
        }
        .pictogramme {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.35rem;
            margin: 0.4rem 0 0.7rem 0;
        }
        .icone-role {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 2px solid #c9a44c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            box-shadow: 0 0 12px rgba(201,164,76,.25) inset;
        }
        [data-testid="stSidebarUserContent"] {
            display: flex;
            flex-direction: column;
            min-height: 92vh;
        }
        [data-testid="stSidebarUserContent"] > div {
            display: contents;
        }
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
            flex: 1;
        }
        div[class*="st-key-abandon"] {
            margin-top: auto;
            margin-bottom: -1.5rem;
            display: flex;
            justify-content: flex-start;
        }
        div[class*="st-key-abandon"] button {
            background-color: transparent;
            border: 1.5px solid #b34848;
            color: #d98080;
        }
        div[class*="st-key-abandon"] button:hover {
            background-color: rgba(179,72,72,.12);
            border-color: #d98080;
            color: #f0a0a0;
        }
        div[class*="st-key-setup_roles"] [data-testid="stVerticalBlock"] { gap: 0.55rem; }
        div[class*="st-key-setup_roles"] [data-testid="stHorizontalBlock"] { gap: 0.6rem; }
        div[class*="st-key-dalles_"] {
            max-width: min(760px, 95%);
            margin: 0 auto;
        }
        div[class*="st-key-dalles_"],
        div[class*="st-key-dalles_"] [data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
        div[class*="st-key-dalles_"] button {
            position: relative;
            background: rgba(28,43,92,.35);
            border: 2px solid rgba(201,164,76,.45);
            border-radius: 10px;
            color: #ece3d2;
            font-family: 'Cinzel', serif;
            font-size: 0.85rem;
            padding: 0.55rem 0.3rem;
            transition: all .18s ease;
        }
        div[class*="st-key-dalles_"] button:hover {
            background: rgba(28,43,92,.8);
            border-color: #c9a44c;
            color: #ffffff;
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(201,164,76,.4);
        }
        div[class*="st-key-dalles_"] button::after {
            content: "👁";
            position: absolute;
            top: 2px;
            right: 5px;
            opacity: 0;
            font-size: 0.8rem;
            transition: opacity .18s ease;
        }
        div[class*="st-key-dalles_"] button:hover::after {
            opacity: 1;
        }
        div[class*="st-key-dalles_loup_"] button,
        div[class*="st-key-dalles_tir_"] button {
            background: rgba(120,20,28,.4);
            border-color: rgba(200,60,60,.55);
        }
        div[class*="st-key-dalles_loup_"] button:hover,
        div[class*="st-key-dalles_tir_"] button:hover {
            background: rgba(160,28,36,.75);
            border-color: #e05555;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(224,85,85,.45);
        }
        div[class*="st-key-dalles_loup_"] button::after { content: "🍖"; }
        div[class*="st-key-dalles_tir_"] button::after { content: "🎯"; }
        div[class*="st-key-dalles_salv_"] button {
            background: rgba(20,90,84,.4);
            border-color: rgba(80,190,175,.55);
        }
        div[class*="st-key-dalles_salv_"] button:hover {
            background: rgba(28,120,110,.75);
            border-color: #55d0bf;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(85,208,191,.45);
        }
        div[class*="st-key-dalles_salv_"] button::after { content: "🛡️"; }
        div[class*="st-key-dalles_mentor_"] button::after { content: "🐾"; }
        div[class*="st-key-dalles_vol_"] button::after { content: "🃏"; }
        div[class*="st-key-dalles_lb_"] button {
            background: rgba(190,190,205,.14);
            border-color: rgba(220,220,235,.55);
        }
        div[class*="st-key-dalles_lb_"] button:hover {
            background: rgba(210,210,225,.3);
            border-color: #e6e6f2;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(230,230,242,.4);
        }
        div[class*="st-key-dalles_lb_"] button::after { content: "🦴"; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def carte_role(nom, role):
    r = ROLES[role]
    st.markdown(
        f"""
        <div class="carte" style="background: {r.degrade};">
            <span class="coin-bd"></span><span class="coin-bg"></span>
            <div class="carte-titre">{r.nom}</div>
            <div class="carte-medaillon">{r.emoji}</div>
            <div class="carte-nom">{nom}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def carte_dos():
    st.markdown('<div class="carte-dos">🐺</div>', unsafe_allow_html=True)


def badge_amour(autre):
    st.markdown(
        f"""
        <div class="badge-amour">
            <span class="badge-icone">💘</span>
            <div>
                <div class="badge-label">En couple avec</div>
                <div class="badge-nom">{autre}</div>
                <div class="badge-sous">Si l'un meurt, l'autre le suit.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_meute(nom, complices):
    if complices:
        noms = " & ".join([nom] + complices)
        sous = "Vous chassez ensemble, en secret."
    else:
        noms = nom
        sous = "Tu es le dernier loup, tu chasses seul."
    st.markdown(
        f"""
        <div class="badge-meute">
            <span class="badge-icone">🐺</span>
            <div>
                <div class="badge-meute-label">La meute</div>
                <div class="badge-meute-noms">{noms}</div>
                <div class="badge-sous">{sous}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plaquette(texte, icone="🌙", ton="neutre"):
    classe = "plaquette" if ton == "neutre" else f"plaquette plaquette-{ton}"
    st.markdown(
        f'<div class="{classe}"><span class="plaquette-icone">{icone}</span><span class="plaquette-texte">{texte}</span></div>',
        unsafe_allow_html=True,
    )


def grille_dalles(theme, cle, choix):
    """Dalles cliquables sur 2 colonnes (style selon `theme`, cf. CSS). Renvoie le nom cliqué ou None."""
    # Plus il y a de choix, plus on élargit la grille : elle reste sur peu de lignes.
    n_col = 2 if len(choix) <= 4 else 3 if len(choix) <= 9 else 4 if len(choix) <= 14 else 5
    clic = None
    with st.container(key=f"dalles_{theme}_{cle}"):
        cols = st.columns(n_col)
        for i, nom in enumerate(choix):
            with cols[i % n_col]:
                if st.button(nom, key=f"pick_{theme}_{cle}_{nom}", use_container_width=True):
                    clic = nom
    return clic


def bouton_fin(s, cle):
    if st.button("Terminer mon tour", type="primary", key=f"fin_{cle}"):
        fin_de_tour(s)
        st.rerun()


# --------------------------------------------------------------------------
# Rôles
#
# Chaque rôle est décrit une seule fois ci-dessous : son affichage (nom,
# emoji, dégradé de carte), son camp (qui détermine les conditions de
# victoire) et sa nuit (une fonction qui affiche l'action du joueur et met
# à jour l'état de partie ; laisser à None pour un rôle qui dort simplement).
#
# Pour ajouter un rôle : lui écrire une fonction `_nuit_xxx(s, nom, cle)` si
# besoin, puis ajouter une entrée dans ROLES. La composition de partie,
# l'écran de nuit, l'affichage des cartes et les conditions de victoire
# s'adaptent automatiquement — aucun autre écran à modifier.
# --------------------------------------------------------------------------

def _afficher_meute(s, nom):
    if s["joueurs"][nom].get("enfant_sauvage"):
        plaquette("Ton mentor est mort : tu as rejoint la meute.", icone="🐾")
    complices = [l for l in s["loups"] if l != nom and s["joueurs"][l]["vivant"]]
    badge_meute(nom, complices)


def _cibles_loups(s):
    return [n for n in vivants(s) if camp(s, n) != "loups"]


def _vote_loups(s, nom, cle, cibles):
    """Grille de vote de la meute. Renvoie True quand la victime vient d'être désignée."""
    st.markdown("**Qui dévorez-vous ?**")
    cible = grille_dalles("loup", cle, cibles)
    if cible:
        s["votes_loups"].append(cible)
        log(s, f"{nom} ({ROLES[s['joueurs'][nom]['role']].nom}) désigne {cible}.")
    return bool(cible)


def _nuit_loup(s, nom, cle):
    _afficher_meute(s, nom)
    cibles = _cibles_loups(s)
    if s["jour"] == 0:
        plaquette("Première nuit : vous vous découvrez, personne ne meurt encore.", icone="🐾")
        bouton_fin(s, cle)
    elif not cibles:
        plaquette("Il ne reste que des loups : personne à dévorer.", icone="🐾")
        bouton_fin(s, cle)
    elif _vote_loups(s, nom, cle, cibles):
        fin_de_tour(s)
        st.rerun()


def _nuit_loup_blanc(s, nom, cle):
    """Vote avec la meute, puis une nuit sur deux (nuits impaires) il peut dévorer l'un des siens."""
    _afficher_meute(s, nom)
    if s["jour"] == 0:
        plaquette("Première nuit : vous vous découvrez, personne ne meurt encore.", icone="🐾")
        bouton_fin(s, cle)
        return

    cibles = _cibles_loups(s)
    if cibles and s.get("vote_loup_blanc") != cle:
        if _vote_loups(s, nom, cle, cibles):
            s["vote_loup_blanc"] = cle
            st.rerun()
        return

    freres = [n for n in vivants(s) if n != nom and camp(s, n) == "loups"]
    if not freres:
        plaquette("Tu es le dernier loup : plus aucun frère à dévorer.", icone="🌕")
        bouton_fin(s, cle)
    elif s["jour"] % 2 == 0:
        plaquette(f"Pas de festin cette nuit. Prochain festin : nuit {s['jour'] + 1}.", icone="🌕")
        bouton_fin(s, cle)
    else:
        st.markdown("**Un de tes frères est-il de trop ?**")
        st.caption("Tu gagnes seul : élimine le village, puis la meute. Tu peux aussi les épargner cette nuit.")
        cible = grille_dalles("lb", cle, freres)
        epargne = st.button("Épargner la meute", key=f"lb_epargne_{cle}")
        if cible:
            s["cible_loup_blanc"] = cible
            log(s, f"Le Loup Blanc {nom} dévore {cible}.")
        elif epargne:
            log(s, f"Le Loup Blanc {nom} épargne la meute.")
        if cible or epargne:
            fin_de_tour(s)
            st.rerun()


def _nuit_chien_loup(s, nom, cle):
    """Première nuit : choix définitif du camp ; ensuite il agit comme un loup ou comme un villageois."""
    choix = s["joueurs"][nom].get("camp_choisi")
    if choix is None:
        st.markdown("**Que choisis-tu d'être ?**")
        st.caption("Choix définitif : tu gagnes avec ce camp. Les autres ne le sauront qu'à la fin de la partie.")
        col1, col2 = st.columns(2)
        villageois = col1.button("🧑‍🌾 Simple Villageois", use_container_width=True, key=f"chien_vil_{cle}")
        loup = col2.button("🐺 Loup-Garou", use_container_width=True, key=f"chien_loup_{cle}")
        if villageois or loup:
            s["joueurs"][nom]["camp_choisi"] = "loups" if loup else "village"
            log(s, f"Le Chien-Loup {nom} choisit d'être {'Loup-Garou' if loup else 'simple Villageois'}.")
            if loup:
                s["loups"].append(nom)
            st.rerun()
    elif choix == "loups":
        _nuit_loup(s, nom, cle)
    else:
        plaquette("Tu as choisi d'être simple Villageois. Dors.", icone="🐕")
        bouton_fin(s, cle)


def _nuit_renard(s, nom, cle):
    """Chaque nuit où il a encore du flair : il flaire 3 personnes et apprend si un loup s'y trouve."""
    resultat = s.get("resultat_renard")
    if resultat and resultat["cle"] == cle:
        if resultat["loup"]:
            plaquette("Un Loup-Garou se cache dans ce groupe. Tu gardes ton flair : à la nuit prochaine.",
                      icone="🦊", ton="succes")
        else:
            plaquette("Aucun Loup-Garou dans ce groupe. Tu perds ton flair et deviens simple Villageois.",
                      icone="🦊")
        st.caption("Groupe flairé : " + ", ".join(resultat["groupe"]))
        if st.button("Terminer mon tour", type="primary", key=f"fin_{cle}"):
            if not resultat["loup"]:
                s["joueurs"][nom]["role"] = "villageois"
                s["joueurs"][nom]["renard"] = True
                log(s, f"{nom} (Renard) devient simple Villageois.")
            fin_de_tour(s)
            st.rerun()
        return

    candidats = [n for n in vivants(s) if n != nom]
    k = min(3, len(candidats))
    st.markdown(f"**Flaire {k} personnes**")
    groupe = st.multiselect(
        "Groupe à flairer", candidats, max_selections=k, key=f"flair_{cle}",
        placeholder="Choisir…", label_visibility="collapsed",
    )
    if st.button("Flairer", type="primary", disabled=len(groupe) != k, key=f"flairer_{cle}"):
        loup = any(camp(s, n) == "loups" for n in groupe)
        log(s, f"Le renard {nom} flaire {', '.join(groupe)} : "
               + ("un loup-garou s'y trouve." if loup else "aucun loup-garou, il perd son flair."))
        s["resultat_renard"] = {"cle": cle, "groupe": groupe, "loup": loup}
        st.rerun()


def _nuit_voyante(s, nom, cle):
    """La voyante a une vision une nuit sur deux (nuits impaires) : pas de stock à épuiser."""
    deja_vu = st.session_state.get(f"vu_{cle}")
    peut_voir = s["jour"] > 0 and s["jour"] % 2 == 1

    if deja_vu:
        role_vu = s["joueurs"][deja_vu]["role"]
        plaquette(f"{deja_vu} est {ROLES[role_vu].nom.upper()}.", icone="🔮", ton="succes")
        bouton_fin(s, cle)
    elif not peut_voir:
        plaquette(f"Pas de vision cette nuit. Prochaine vision : nuit {s['jour'] + 1}.", icone="🌙")
        bouton_fin(s, cle)
    else:
        candidats = [n for n in vivants(s) if n != nom]
        vu = grille_dalles("voy", cle, candidats)
        if vu:
            log(s, f"La voyante {nom} sonde {vu} : {ROLES[s['joueurs'][vu]['role']].nom}.")
            st.session_state[f"vu_{cle}"] = vu
            st.rerun()


def _nuit_sorciere(s, nom, cle):
    if s["jour"] == 0 or s["potions_sorciere"] == 0:
        plaquette("Rien à faire cette nuit.", icone="🌙")
        bouton_fin(s, cle)
    else:
        st.write(f"Potions de soin restantes : {s['potions_sorciere']}")
        st.caption("Tu ne sais pas encore qui les loups ont désigné.")
        col1, col2 = st.columns(2)
        if col1.button("Utiliser une potion", type="primary", key=f"soin_{cle}"):
            s["soin_sorciere"] = True
            s["potions_sorciere"] -= 1
            log(s, f"La sorcière {nom} utilise une potion de soin.")
            fin_de_tour(s)
            st.rerun()
        if col2.button("Ne rien faire", key=f"rien_{cle}"):
            fin_de_tour(s)
            st.rerun()


def _nuit_cupidon(s, nom, cle):
    if s["jour"] > 0:
        plaquette("Ton travail est fait. Dors.", icone="🏹")
        bouton_fin(s, cle)
    else:
        tous = list(s["joueurs"].keys())
        premier = st.selectbox("Premier amoureux", tous, index=None, placeholder="Choisir…", key=f"cup1_{cle}")
        second_options = [n for n in tous if n != premier] if premier else tous
        second = st.selectbox("Deuxième amoureux", second_options, index=None, placeholder="Choisir…", key=f"cup2_{cle}")
        couple = [premier, second] if premier and second else []
        if st.button("Décocher la flèche", type="primary", key=f"ok_cup_{cle}"):
            if len(couple) != 2:
                st.error("Il en faut exactement deux.")
            else:
                s["amoureux"] = couple
                log(s, f"Cupidon {nom} lie {couple[0]} et {couple[1]}.")
                for n in couple:
                    s["joueurs"][n]["amoureux"] = True
                fin_de_tour(s)
                st.rerun()


def _nuit_salvateur(s, nom, cle):
    if s["jour"] == 0:
        plaquette("Première nuit : personne ne meurt, rien à protéger.", icone="🛡️")
        bouton_fin(s, cle)
        return

    precedent = s.get("protege_precedent")
    st.markdown("**Qui protèges-tu cette nuit ?**")
    if precedent and s["joueurs"][precedent]["vivant"]:
        st.caption(f"Tu ne peux pas protéger {precedent} deux nuits de suite.")
    protege = grille_dalles("salv", cle, [n for n in vivants(s) if n != precedent])
    if protege:
        log(s, f"Le salvateur {nom} protège {protege}.")
        s["protege_nuit"] = protege
        fin_de_tour(s)
        st.rerun()


def _nuit_enfant_sauvage(s, nom, cle):
    mentor = s.get("mentor_enfant")
    if mentor is None:
        st.markdown("**Choisis ton mentor**")
        st.caption("Il ignorera son rôle. S'il meurt, tu deviens loup-garou.")
        choix = grille_dalles("mentor", cle, [n for n in vivants(s) if n != nom])
        if choix:
            log(s, f"{nom} (Enfant sauvage) choisit {choix} comme mentor.")
            s["mentor_enfant"] = choix
            st.rerun()
    else:
        plaquette(f"Ton mentor est {mentor}. S'il meurt, tu deviens loup-garou.", icone="🐾")
        bouton_fin(s, cle)


def _nuit_voleur(s, nom, cle):
    """Première nuit : le voleur prend l'un des deux rôles du milieu, ou reste simple villageois."""
    milieu = s["cartes_milieu"]
    st.markdown("**Deux cartes sont restées au milieu**")
    st.caption("Choisis-en une pour en prendre le rôle, ou garde ton sort : tu seras alors simple Villageois.")

    nouveau_role = None
    garde = False
    with st.container(key=f"dalles_vol_{cle}"):
        cols = st.columns(2)
        for i, role in enumerate(milieu):
            with cols[i % 2]:
                if st.button(
                    f"{ROLES[role].emoji} {ROLES[role].nom}",
                    key=f"pick_vol_{cle}_{i}", use_container_width=True,
                ):
                    nouveau_role = role
    if st.button("Garder mon rôle (Villageois)", key=f"vol_garde_{cle}"):
        nouveau_role = "villageois"
        garde = True

    if nouveau_role:
        if garde:
            log(s, f"{nom} (Voleur) garde son sort et devient simple Villageois.")
        else:
            log(s, f"{nom} (Voleur) prend la carte {ROLES[nouveau_role].nom}.")
        s["joueurs"][nom]["role"] = nouveau_role
        s["joueurs"][nom]["voleur"] = True
        if ROLES[nouveau_role].camp == "loups":
            s["loups"].append(nom)
        s["cartes_milieu"] = []
        st.rerun()


def _nuit_chasseur(s, nom, cle):
    plaquette("Tu es le chasseur : si tu meurs, tu pourras tirer une dernière balle. Dors.", icone="🔫")
    bouton_fin(s, cle)


def _nuit_villageois(s, nom, cle):
    plaquette("Tu dors paisiblement.", icone="🌙")
    bouton_fin(s, cle)


@dataclass(frozen=True)
class Role:
    key: str
    nom: str
    emoji: str
    degrade: str  # dégradé CSS de fond pour la carte de rôle
    camp: str = "village"  # "village" ou "loups" : détermine les conditions de victoire
    unique: bool = True  # au plus un exemplaire proposé par défaut à la composition
    etat_initial: dict = field(default_factory=dict)  # clés d'état de partie propres à ce rôle
    nuit: Optional[Callable[[dict, str, str], None]] = None  # rendu du tour de nuit ; None = dort
    cartes_en_plus: int = 0  # cartes ajoutées au paquet et laissées au milieu de la table
    recommande: bool = True  # coché par défaut dans la composition suggérée
    tir_a_la_mort: bool = False  # à sa mort, ce rôle peut emporter un autre joueur avec lui
    solitaire: bool = False  # gagne seul, en éliminant tout le monde (village et loups compris)
    camp_secret: bool = False  # son camp n'est pas révélé à sa mort (le joueur a choisi le sien)
    priorite_nuit: int = 2  # plus petit = joue plus tôt dans la nuit (à égalité : ordre des joueurs)


ROLES = {
    "loup": Role(
        key="loup",
        nom="Loup-Garou",
        emoji="🐺",
        degrade="radial-gradient(circle at 50% 30%, #6b1f22, #2a0a0c 75%)",
        camp="loups",
        unique=False,
        nuit=_nuit_loup,
    ),
    "sorciere": Role(
        key="sorciere",
        nom="Sorcière",
        emoji="🧪",
        degrade="radial-gradient(circle at 50% 30%, #3d1f5c, #170a29 75%)",
        etat_initial={"potions_sorciere": 2, "soin_sorciere": False},
        nuit=_nuit_sorciere,
    ),
    "voyante": Role(
        key="voyante",
        nom="Voyante",
        emoji="🔮",
        degrade="radial-gradient(circle at 50% 30%, #1c2b5c, #090f29 75%)",
        nuit=_nuit_voyante,
    ),
    "cupidon": Role(
        key="cupidon",
        nom="Cupidon",
        emoji="🏹",
        degrade="radial-gradient(circle at 50% 30%, #6b2748, #29101f 75%)",
        nuit=_nuit_cupidon,
    ),
    "chasseur": Role(
        key="chasseur",
        nom="Chasseur",
        emoji="🔫",
        degrade="radial-gradient(circle at 50% 30%, #6b4a1f, #291b0a 75%)",
        tir_a_la_mort=True,
        nuit=_nuit_chasseur,
    ),
    "salvateur": Role(
        key="salvateur",
        nom="Salvateur",
        emoji="🛡️",
        degrade="radial-gradient(circle at 50% 30%, #1f5c55, #0a2925 75%)",
        etat_initial={"protege_nuit": None, "protege_precedent": None},
        recommande=False,
        nuit=_nuit_salvateur,
    ),
    "enfant_sauvage": Role(
        key="enfant_sauvage",
        nom="Enfant sauvage",
        emoji="🧒",
        degrade="radial-gradient(circle at 50% 30%, #4a5c1f, #1c260a 75%)",
        etat_initial={"mentor_enfant": None},
        recommande=False,
        nuit=_nuit_enfant_sauvage,
    ),
    "voleur": Role(
        key="voleur",
        nom="Voleur",
        emoji="🃏",
        degrade="radial-gradient(circle at 50% 30%, #5c4a1f, #261d0a 75%)",
        cartes_en_plus=2,
        recommande=False,
        priorite_nuit=0,
        nuit=_nuit_voleur,
    ),
    "renard": Role(
        key="renard",
        nom="Renard",
        emoji="🦊",
        degrade="radial-gradient(circle at 50% 30%, #8a3f12, #33150a 75%)",
        recommande=False,
        nuit=_nuit_renard,
    ),
    "loup_blanc": Role(
        key="loup_blanc",
        nom="Loup Blanc",
        emoji="🌕",
        degrade="radial-gradient(circle at 50% 30%, #6e6e78, #24242b 75%)",
        camp="loups",
        etat_initial={"cible_loup_blanc": None, "vote_loup_blanc": None},
        recommande=False,
        solitaire=True,
        nuit=_nuit_loup_blanc,
    ),
    "chien_loup": Role(
        key="chien_loup",
        nom="Chien-Loup",
        emoji="🐕",
        degrade="radial-gradient(circle at 50% 30%, #5a4632, #1e1710 75%)",
        recommande=False,
        camp_secret=True,
        priorite_nuit=1,
        nuit=_nuit_chien_loup,
    ),
    "villageois": Role(
        key="villageois",
        nom="Villageois",
        emoji="🧑‍🌾",
        degrade="radial-gradient(circle at 50% 30%, #35431f, #141a0d 75%)",
        unique=False,
        nuit=_nuit_villageois,
    ),
}

# Rôles proposés (avec un nombre à régler) dans l'écran de composition : tous
# sauf le loup (obligatoire, quantité libre, traité à part) et le villageois
# (calculé automatiquement en reste de table).
ROLES_SPECIAUX = [r for cle, r in ROLES.items() if cle not in ("loup", "villageois")]


# --------------------------------------------------------------------------
# Sauvegarde disque
# --------------------------------------------------------------------------

def save_game(s):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def clear_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def log(s, texte, moment=None):
    """Ajoute un événement au journal. `moment` vaut la phase courante par défaut."""
    s.setdefault("journal", []).append(
        {"jour": s["jour"], "moment": moment or s["phase"], "texte": texte}
    )


def archiver_partie(s, issue):
    """Écrit le journal complet dans parties/ (une seule fois par partie)."""
    if s.get("archive"):
        return
    os.makedirs(HISTORIQUE_DIR, exist_ok=True)
    maintenant = datetime.now()
    fichier = os.path.join(HISTORIQUE_DIR, f"partie_{maintenant:%Y%m%d_%H%M%S}.json")
    donnees = {
        "date": maintenant.isoformat(timespec="seconds"),
        "issue": issue,
        "joueurs": s["joueurs"],
        "journal": s["journal"],
    }
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=2, ensure_ascii=False)
    s["archive"] = fichier


def terminer_partie(s, message):
    log(s, message, "fin")
    s["phase"] = "fin"
    s["message_fin"] = message
    archiver_partie(s, message)


# --------------------------------------------------------------------------
# État du jeu
# --------------------------------------------------------------------------

def nouvelle_partie(noms, composition):
    """noms : liste de noms de joueurs. composition : dict {role: nombre}."""
    roles = []
    for role, n in composition.items():
        roles += [role] * n
    random.shuffle(roles)

    joueurs = {
        nom: {"role": role, "vivant": True, "amoureux": False}
        for nom, role in zip(noms, roles)
    }
    cartes_milieu = roles[len(noms):]

    etat = {
        "nb_joueurs": len(noms),
        "jour": 0,
        "phase": "nuit",
        "joueurs": joueurs,
        "loups": [n for n, d in joueurs.items() if ROLES[d["role"]].camp == "loups"],
        "amoureux": [],
        "votes_loups": [],
        "ordre_nuit": [],
        "tour": 0,
        "devoile": False,
        "transfert": False,
        "morts_nuit": [],
        "cartes_milieu": cartes_milieu,
        "morts_tir": [],
        "tirs_en_attente": [],
        "retour_tir": None,
        "journal": [],
        "maire": None,
        "dernier_maire": None,
    }
    for role in ROLES.values():
        etat.update(role.etat_initial)
    paquet = ", ".join(f"{ROLES[cle].nom} ×{n}" for cle, n in composition.items() if n > 0)
    log(etat, f"{len(noms)} joueurs. Paquet : {paquet}.", "debut")
    log(etat, "Distribution : " + ", ".join(
        f"{n} ({ROLES[d['role']].nom})" for n, d in joueurs.items()
    ) + ".", "debut")
    return etat


def vivants(s):
    return [n for n, d in s["joueurs"].items() if d["vivant"]]


def camp(s, nom):
    """Camp effectif d'un joueur : celui qu'il a choisi (Chien-Loup) sinon celui de son rôle."""
    d = s["joueurs"][nom]
    return d.get("camp_choisi") or ROLES[d["role"]].camp


def _convertir_enfant_sauvage(s, morts):
    """Si le mentor de l'enfant sauvage est mort, l'enfant (s'il vit encore) devient loup-garou."""
    mentor = s.get("mentor_enfant")
    if mentor is None or mentor not in morts:
        return
    s["mentor_enfant"] = None
    for n in vivants(s):
        d = s["joueurs"][n]
        if d["role"] == "enfant_sauvage":
            d["role"] = "loup"
            d["enfant_sauvage"] = True
            log(s, f"Le mentor {mentor} est mort : {n} (Enfant sauvage) devient loup-garou.")
            s["loups"].append(n)


def tuer(s, nom, cause="meurt"):
    """Tue un joueur et entraîne son amoureux dans la mort. Renvoie la liste des morts."""
    if nom not in s["joueurs"] or not s["joueurs"][nom]["vivant"]:
        return []
    s["joueurs"][nom]["vivant"] = False
    morts = [nom]
    if s["joueurs"][nom]["amoureux"]:
        for autre in s["amoureux"]:
            if autre != nom and s["joueurs"][autre]["vivant"]:
                s["joueurs"][autre]["vivant"] = False
                morts.append(autre)
    if s.get("maire") in morts:
        s["dernier_maire"] = s["maire"]
        s["maire"] = None
    for i, mort in enumerate(morts):
        raison = cause if i == 0 else "meurt de chagrin (amoureux)"
        log(s, f"{mort} ({ROLES[s['joueurs'][mort]['role']].nom}) {raison}.")
    _convertir_enfant_sauvage(s, morts)
    for mort in morts:
        if ROLES[s["joueurs"][mort]["role"]].tir_a_la_mort:
            s.setdefault("tirs_en_attente", []).append(mort)
    return morts


def vainqueur(s):
    en_vie = vivants(s)
    loups = [n for n in en_vie if camp(s, n) == "loups"]
    autres = [n for n in en_vie if camp(s, n) != "loups"]
    solitaires = [n for n in en_vie if ROLES[s["joueurs"][n]["role"]].solitaire]

    if len(en_vie) == 2 and all(s["joueurs"][n]["amoureux"] for n in en_vie):
        return "Les amoureux l'emportent : ils sont les deux derniers survivants."
    if solitaires:
        # Tant qu'il vit, ni le village ni la meute ne peuvent conclure : il doit rester seul.
        if len(en_vie) == 1:
            return f"{solitaires[0]} ({ROLES[s['joueurs'][solitaires[0]]['role']].nom}) l'emporte seul."
        return None
    if not loups:
        return "Le village a gagné : tous les loups sont morts."
    if len(loups) >= len(autres):
        return "Les loups ont gagné : ils sont aussi nombreux que les villageois."
    return None


def fin_de_tour(s):
    """Passe au joueur suivant dans la nuit."""
    s["tour"] += 1
    s["devoile"] = False
    s["transfert"] = False


# --------------------------------------------------------------------------
# Écrans
# --------------------------------------------------------------------------

def composition_recommandee(nb):
    """Suggestion de départ raisonnable pour un nombre de joueurs donné."""
    loups = max(1, nb // 4)
    reste = nb - loups
    speciaux = {}
    for role in ROLES_SPECIAUX:
        n = 1 if (role.unique and role.recommande and reste >= 1) else 0
        speciaux[role.key] = n
        reste -= n
    return loups, speciaux


def ecran_installation():
    st.markdown("#### 🐺 Loup-Garou")

    if "config_etape" not in st.session_state:
        st.session_state.config_etape = "roles"

    if st.session_state.config_etape == "roles":
        etape_roles()
    else:
        etape_noms()


def afficher_composition(nb, total, composition, n_villageois):
    lignes = "".join(
        f'<div class="panneau-ligne"><span>{ROLES[cle].emoji} {ROLES[cle].nom}</span><span>{n}</span></div>'
        for cle, n in composition.items()
        if n > 0
    )
    st.markdown(
        f"""
        <div class="panneau panneau-dense">
            <div class="panneau-titre">Composition</div>
            <div class="panneau-grille">{lignes}</div>
            <div class="panneau-ligne panneau-total"><span><b>Total</b></span><span><b>{total} / {total}</b></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if n_villageois < 0:
        st.error(
            f"Trop de rôles spéciaux pour {total} cartes "
            f"(il en manque {-n_villageois}) : réduis-en un ou augmente le nombre de joueurs."
        )
        return

    icones = "".join(
        f'<div class="icone-role" style="background: {ROLES[cle].degrade};" title="{ROLES[cle].nom}">{ROLES[cle].emoji}</div>'
        for cle, n in composition.items()
        for _ in range(n)
    )
    st.markdown(f'<div class="pictogramme">{icones}</div>', unsafe_allow_html=True)
    if total > nb:
        st.caption(f"{total - nb} cartes restent au milieu de la table ({nb} joueurs, {total} cartes).")


def etape_roles():
    """Tout tient sans scroller : réglages à gauche, aperçu de la composition et bouton à droite."""
    with st.container(key="setup_roles"):
        st.markdown("##### 1. Composition de la partie")
        gauche, droite = st.columns([3, 2], gap="large")

        # Réservé ici, rempli une fois les rôles de la colonne de gauche connus.
        with droite:
            apercu = st.empty()

        with gauche:
            col_nb, col_loup = st.columns(2)
            nb = col_nb.number_input(
                "Nombre de joueurs",
                min_value=5,
                max_value=18,
                value=7,
                step=1,
                key="nb_joueurs_setup",
            )
            loups_defaut, speciaux_defaut = composition_recommandee(nb)
            n_loup = col_loup.number_input(
                f"{ROLES['loup'].emoji} {ROLES['loup'].nom}s",
                min_value=1, max_value=max(1, nb - 1),
                value=min(loups_defaut, max(1, nb - 1)), key="n_loup",
            )
            composition = {"loup": n_loup}

            # Rôles uniques (au plus un exemplaire) : une simple case à cocher, en
            # grille de 3 colonnes ; le reste de la table devient Villageois.
            st.markdown("**Autres rôles** · coche ceux qui jouent")
            uniques = [role for role in ROLES_SPECIAUX if role.unique]
            for i in range(0, len(uniques), 3):
                cols = st.columns(3)
                for col, role in zip(cols, uniques[i:i + 3]):
                    with col:
                        composition[role.key] = int(st.checkbox(
                            f"{role.emoji} {role.nom}",
                            value=bool(speciaux_defaut[role.key]), key=f"n_{role.key}",
                        ))

            # Rôles spéciaux en quantité libre (aucun aujourd'hui, mais le prochain
            # rôle de ce type n'aura besoin que d'une entrée dans ROLES).
            for role in ROLES_SPECIAUX:
                if not role.unique:
                    composition[role.key] = st.slider(
                        f"{role.emoji} {role.nom}", min_value=0, max_value=nb,
                        value=speciaux_defaut[role.key], key=f"n_{role.key}",
                    )

        total = nb + sum(ROLES[cle].cartes_en_plus * n for cle, n in composition.items())
        n_villageois = total - sum(composition.values())
        composition["villageois"] = max(n_villageois, 0)

        with apercu.container():
            afficher_composition(nb, total, composition, n_villageois)

        with droite:
            if st.button(
                "Suivant : noms des joueurs →", type="primary",
                disabled=n_villageois < 0, use_container_width=True,
            ):
                st.session_state.config_nb = nb
                st.session_state.config_composition = composition
                st.session_state.config_etape = "noms"
                st.rerun()


def etape_noms():
    nb = st.session_state.config_nb
    st.subheader("2. Qui joue ?")
    st.caption(f"{nb} joueurs — vous vous passerez l'appareil à tour de rôle pendant la nuit.")

    with st.form("noms"):
        noms = []
        cols = st.columns(2)
        for i in range(nb):
            with cols[i % 2]:
                noms.append(st.text_input(f"Joueur {i + 1}", key=f"nom_{i}").strip())

        col_retour, col_lance = st.columns([1, 2])
        retour = col_retour.form_submit_button("← Retour")
        lance = col_lance.form_submit_button("Distribuer les rôles", type="primary")

    if retour:
        st.session_state.config_etape = "roles"
        st.rerun()

    if lance:
        if any(not n for n in noms):
            st.error("Il manque un nom.")
        elif len(set(noms)) != nb:
            st.error("Deux joueurs portent le même nom.")
        else:
            st.session_state.partie = nouvelle_partie(noms, st.session_state.config_composition)
            for cle in ("config_etape", "config_nb", "config_composition"):
                st.session_state.pop(cle, None)
            st.rerun()


def ecran_nuit(s):
    if not s["ordre_nuit"]:
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
        st.header("🔄 Changement de joueur")
        carte_dos()
        plaquette(f"Passe le PC à {nom}, puis pose-le et éloigne-toi de l'écran.", icone="🔄")
        if st.button(f"C'est fait, {nom} a le PC", type="primary", key=f"transfert_{s['jour']}_{s['tour']}"):
            s["transfert"] = True
            st.rerun()
        return

    if not s["devoile"]:
        st.header(f"C'est ton tour, {nom}")
        carte_dos()
        plaquette("Confirme que c'est bien toi avant de voir ton rôle.", icone="🗝️")
        if st.button(f"Oui, je suis {nom}", type="primary", key=f"pret_{s['jour']}_{s['tour']}"):
            s["devoile"] = True
            st.rerun()
        return

    st.header("🃏 Ta carte")
    carte_role(nom, role)
    cle = f"{s['jour']}_{s['tour']}"

    with st.container(height=340, border=False):
        gerer_nuit = ROLES[role].nuit or _nuit_villageois
        gerer_nuit(s, nom, cle)

    if donnees["amoureux"] and s["jour"] > 0:
        autre = [n for n in s["amoureux"] if n != nom]
        with st.sidebar:
            badge_amour(autre[0])


def resoudre_nuit(s):
    morts = []
    if s["jour"] > 0:
        comptes = Counter(s["votes_loups"]).most_common()
        victime = None
        if len(comptes) > 1 and comptes[0][1] == comptes[1][1]:
            log(s, "Les loups ne s'accordent pas : personne n'est dévoré.")
        elif comptes:
            victime = comptes[0][0]
        sauveurs = []
        if victime and s["soin_sorciere"]:
            sauveurs.append("la potion de la sorcière")
        if victime and victime == s.get("protege_nuit"):
            sauveurs.append("le salvateur")
        if sauveurs:
            log(s, f"{victime} était la cible des loups mais est sauvé par {' et '.join(sauveurs)}.")
            victime = None
        if victime:
            morts = tuer(s, victime, "est dévoré par les loups")
        # Le festin du Loup Blanc échappe à la sorcière et au salvateur.
        if s.get("cible_loup_blanc"):
            morts += tuer(s, s["cible_loup_blanc"], "est dévoré par le Loup Blanc")
        if not morts:
            log(s, "Personne ne meurt cette nuit.")

    s["morts_nuit"] = morts
    s["morts_tir"] = []
    s["votes_loups"] = []
    s["cible_loup_blanc"] = None
    s["protege_precedent"] = s.get("protege_nuit")
    s["protege_nuit"] = None
    s["soin_sorciere"] = False
    s["ordre_nuit"] = []
    s["tour"] = 0
    s["devoile"] = False
    s["phase"] = "reveil"


def _camp_txt(s, nom):
    role = ROLES[s["joueurs"][nom]["role"]]
    if role.camp_secret:
        return f"était le {role.nom.upper()} : son camp reste secret jusqu'à la fin"
    return "était LOUP-GAROU" if camp(s, nom) == "loups" else "n'était pas loup-garou"


def annonce_tirs(s):
    for mort in s.get("morts_tir", []):
        st.error(f"🔫 {mort} a été abattu par le chasseur. Il {_camp_txt(s, mort)}.")


def bouton_tir(s, retour):
    """Bouton menant à l'écran de tir s'il reste un chasseur à faire tirer."""
    chasseur = s["tirs_en_attente"][0]
    st.warning(f"{chasseur} était le chasseur : il peut tirer sa dernière balle.")
    if st.button("🔫 Le chasseur décide", type="primary", key=f"bouton_tir_{retour}"):
        s["retour_tir"] = retour
        s["phase"] = "tir_chasseur"
        st.rerun()


def ecran_reveil(s):
    st.title(f"☀️ Réveil — jour {s['jour']}")
    if s["morts_nuit"]:
        for mort in s["morts_nuit"]:
            st.error(f"{mort} est mort. Il {_camp_txt(s, mort)}.")
        if len(s["amoureux"]) == 2 and set(s["amoureux"]) <= set(s["morts_nuit"]):
            st.caption("Les amoureux sont morts ensemble.")
    else:
        st.success("Personne n'est mort cette nuit.")
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
    st.title("👑 Élection du maire")

    if s.get("dernier_maire"):
        st.warning(
            f"{s['dernier_maire']} était le maire et il est mort : le village doit élire son successeur."
        )
    else:
        st.info("Avant le premier vote, le village élit son maire.")

    st.caption(
        "Débattez et votez à voix haute comme d'habitude, puis saisis ici le nom élu."
    )

    en_vie = vivants(s)
    elu = st.radio("Le village élit comme maire", en_vie, key=f"election_maire_{s['jour']}")
    if st.button("Valider l'élection", type="primary"):
        s["maire"] = elu
        log(s, f"{elu} est élu maire.")
        s["dernier_maire"] = None
        s["phase"] = "conseil"
        st.rerun()


def ecran_conseil(s):
    st.title("🗳️ Conseil du village")

    if s["jour"] == 0:
        st.info("Première nuit passée : pas de vote aujourd'hui.")
        if st.button("La nuit retombe", type="primary"):
            s["jour"] += 1
            s["phase"] = "nuit"
            st.rerun()
        return

    en_vie = vivants(s)
    st.write("En vie : " + ", ".join(en_vie))

    if st.session_state.get(f"resultat_{s['jour']}"):
        for mort in st.session_state[f"resultat_{s['jour']}"]:
            if ROLES[s["joueurs"][mort]["role"]].camp_secret:
                st.warning(f"{mort} {_camp_txt(s, mort)}.")
            elif camp(s, mort) == "loups":
                st.success(f"{mort} était LOUP-GAROU.")
            else:
                st.error(f"{mort} n'était PAS loup-garou.")
        annonce_tirs(s)

        gagnant = vainqueur(s)
        if s.get("tirs_en_attente"):
            bouton_tir(s, "conseil")
        elif gagnant:
            if st.button("Voir le résultat", type="primary"):
                terminer_partie(s, gagnant)
                st.rerun()
        elif st.button("La nuit tombe", type="primary"):
            s["jour"] += 1
            s["phase"] = "nuit"
            st.rerun()

    else:
        st.caption("Débattez à voix haute, puis le capitaine saisit le résultat du vote.")
        condamne = st.radio("Le village élimine", en_vie, key=f"vote_{s['jour']}")
        if st.button("Valider le vote", type="primary"):
            st.session_state[f"resultat_{s['jour']}"] = tuer(s, condamne, "est éliminé par le village")
            st.rerun()


def ecran_tir_chasseur(s):
    chasseur = s["tirs_en_attente"][0]
    st.title("🔫 Dernière balle")
    st.warning(
        f"{chasseur} était le chasseur et vient de mourir. "
        "Il peut désigner quelqu'un qui mourra sur-le-champ, ou renoncer à tirer."
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

    col1, col2 = st.columns(2)
    tirer = col1.button(
        f"🔫 Tirer sur {choix}" if choix else "🔫 Tirer",
        type="primary", disabled=choix is None, key="tir_confirmer",
    )
    renoncer = col2.button("Renoncer à tirer", key="tir_renoncer")

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


def ecran_fin(s):
    st.title("🏁 Fin de la partie")
    st.header(s["message_fin"])
    st.subheader("Les rôles")
    for nom, d in s["joueurs"].items():
        etat = "en vie" if d["vivant"] else "mort"
        coeur = " 💘" if d["amoureux"] else ""
        ancien = " (ex-enfant sauvage)" if d.get("enfant_sauvage") else ""
        ancien += " (ex-voleur)" if d.get("voleur") else ""
        ancien += " (ex-renard)" if d.get("renard") else ""
        if d.get("camp_choisi"):
            ancien += " (loup-garou)" if d["camp_choisi"] == "loups" else " (villageois)"
        st.write(f"{ROLES[d['role']].emoji} **{nom}** — {ROLES[d['role']].nom}{ancien} ({etat}){coeur}")

    st.subheader("Historique de la partie")
    afficher_historique(s)
    st.download_button(
        "Télécharger l'historique (JSON)",
        data=json.dumps(
            {"issue": s["message_fin"], "joueurs": s["joueurs"], "journal": s["journal"]},
            indent=2, ensure_ascii=False,
        ),
        file_name="historique_partie.json",
        mime="application/json",
    )
    if s.get("archive"):
        st.caption(f"Archive enregistrée dans {s['archive']}")


def afficher_historique(s):
    """Journal regroupé par nuit / jour, dans l'ordre chronologique."""
    def bloc(e):
        if e["moment"] in ("debut", "fin"):
            return e["moment"], None
        return ("nuit" if e["moment"] == "nuit" else "jour"), e["jour"]

    titres = {"debut": "🎲 Début de partie", "fin": "🏁 Fin"}
    courant = None
    lignes = []

    def vider():
        if lignes:
            st.markdown("\n".join(lignes))
            lignes.clear()

    for e in s["journal"]:
        b = bloc(e)
        if b != courant:
            vider()
            courant = b
            kind, jour = b
            if kind == "nuit":
                st.markdown(f"##### 🌙 Nuit {jour}" + (" (première nuit)" if jour == 0 else ""))
            elif kind == "jour":
                st.markdown(f"##### ☀️ Jour {jour}")
            else:
                st.markdown(f"##### {titres[kind]}")
        lignes.append(f"- {e['texte']}")
    vider()


# --------------------------------------------------------------------------
# Point d'entrée
# --------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Loup-Garou", page_icon="🐺", layout="wide")
    css_cartes()

    if "partie" not in st.session_state:
        sauvegarde = load_game()
        if sauvegarde:
            st.session_state.partie = sauvegarde
        else:
            ecran_installation()
            return

    s = st.session_state.partie

    with st.sidebar:
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

        st.markdown(
            f"""
            <div class="panneau">
                <div class="panneau-titre">{PHASE_EMOJI.get(s['phase'], '')} Jour {s['jour']} — {PHASE_LABEL.get(s['phase'], s['phase'])}</div>
                <div class="panneau-ligne"><span>👥 Vivants</span><span>{len(vivants(s))} / {s['nb_joueurs']}</span></div>
                <div class="panneau-ligne"><span>🐺 Loups</span><span>{loups_vivants}</span></div>
                <div class="panneau-ligne"><span>🧑‍🌾 Village</span><span>{village_vivants}</span></div>
                {ligne_secret}
            </div>
            <div class="panneau">
                <div class="panneau-ligne"><span>👑 Maire</span><span>{maire_txt}</span></div>
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

    with st.sidebar:
        if os.path.exists(MUSIQUE_FILE):
            if st.checkbox("🎵 Musique de fond", value=True, key="musique_on"):
                st.audio(MUSIQUE_FILE, format="audio/mp3", loop=True, autoplay=True)

        if st.button("🚪 Abandonner la partie", key="abandon"):
            if s["phase"] != "fin":
                log(s, "Partie abandonnée.", "fin")
                archiver_partie(s, "Partie abandonnée")
            clear_save()
            st.session_state.clear()
            st.rerun()

    save_game(s)


main()
