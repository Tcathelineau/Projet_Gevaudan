"""
Loup-Garou — version Streamlit (jeu en hotseat : on se passe l'écran).

Lancement :  streamlit run loup_garou_app.py
"""

import copy
import glob
import html
import json
import os
import random
from collections import Counter
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

SAVE_FILE = "save.json"
HISTORIQUE_DIR = "historique"
MUSIQUE_FILE = "musique.mp3"



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
        .annonce {
            --a-couleur: #e0a93b;
            --a-fond: rgba(120,84,20,.45);
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: .6rem 0 1rem;
            padding: .75rem 1.1rem;
            border: 1.5px solid var(--a-couleur);
            border-radius: 12px;
            background: linear-gradient(100deg, var(--a-fond), rgba(16,18,26,.85));
            box-shadow: 0 4px 16px rgba(0,0,0,.4);
        }
        .annonce-danger { --a-couleur: #cf5a50; --a-fond: rgba(120,32,32,.5); }
        .annonce-succes { --a-couleur: #6fae6a; --a-fond: rgba(30,84,42,.5); }
        .annonce-mystere { --a-couleur: #a08ade; --a-fond: rgba(64,44,118,.5); }
        .annonce-signe {
            flex: 0 0 auto;
            width: 2.3rem;
            height: 2.3rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            font-size: 1.45rem;
            line-height: 1;
            color: #1a1408;
            background: var(--a-couleur);
            box-shadow: 0 0 14px var(--a-couleur);
            animation: annonce-pulse 2.6s ease-in-out infinite;
        }
        .annonce-texte {
            font-family: 'EB Garamond', serif;
            font-size: 1.2rem;
            line-height: 1.3;
            color: #f3ebd8;
        }
        @keyframes annonce-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
        .potion-bandeau {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .7rem;
            width: fit-content;
            margin: 1rem auto 1.1rem;
            padding: .55rem 1.5rem;
            border: 1.5px solid rgba(201,164,76,.75);
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(20,52,36,.15), rgba(40,110,72,.45) 50%, rgba(20,52,36,.15));
            box-shadow: 0 0 18px rgba(80,200,120,.22), inset 0 0 12px rgba(0,0,0,.35);
        }
        .potion-fioles { font-size: 1.3rem; letter-spacing: .2rem; filter: drop-shadow(0 0 6px rgba(90,220,130,.7)); }
        .potion-texte {
            font-family: 'Cinzel', serif;
            font-size: 1rem;
            letter-spacing: .06em;
            color: #e8f3d8;
        }
        div[class*="st-key-sorciere_boutons"] button[data-testid="stBaseButton-primary"] {
            background-color: #2f9a55;
            border-color: #2f9a55;
            color: #fff;
        }
        div[class*="st-key-sorciere_boutons"] button[data-testid="stBaseButton-primary"]:hover {
            background-color: #38b165;
            border-color: #38b165;
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
        .chrono {
            display: flex;
            flex-wrap: wrap;
            row-gap: 0.55rem;
            max-height: 30vh;
            overflow-y: auto;
            padding: 0.25rem 0.1rem 0.1rem;
        }
        .chrono-pas { display: flex; align-items: flex-start; }
        .chrono-etape { display: flex; flex-direction: column; align-items: center; gap: 2px; width: 24px; }
        .chrono-noeud {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.62rem;
        }
        .chrono-start { background: #6b5a2e; color: #f0d890; font-size: 0.55rem; }
        .chrono-nuit { background: #44589a; }
        .chrono-jour { background: #abc4d0; }
        .chrono-actuel { box-shadow: 0 0 0 2px #c9a44c, 0 0 10px rgba(201,164,76,.6); }
        .chrono-lien {
            width: 5px;
            height: 3px;
            margin: 9px 1px 0;
            border-radius: 2px;
            background: #d9d9d9;
        }
        .chrono-label {
            font-family: 'EB Garamond', serif;
            font-size: 0.65rem;
            line-height: 1;
            color: #b9b09c;
            white-space: nowrap;
        }
        .chrono-actuel + .chrono-label { color: #f0d890; font-weight: 600; }
        .chrono-etape.chrono-debut { width: 30px; }
        .panneau-dense { padding: 0.6rem 0.9rem; margin-bottom: 0.6rem; }
        .panneau-dense .panneau-titre {
            font-size: 0.95rem;
            padding-bottom: 0.3rem;
            margin-bottom: 0.35rem;
        }
        .maire-nom { font-size: 1.2rem; font-weight: 400; color: #f0d890; }
        .panneau-dense .panneau-ligne { font-size: 0.92rem; padding: 0.05rem 0; }
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
        div[class*="st-key-options"],
        [data-testid="stLayoutWrapper"]:has(> div[class*="st-key-options"]),
        [data-testid="stElementContainer"]:has(> div[class*="st-key-options"]) {
            margin-top: auto;
            margin-bottom: -1.5rem;
        }
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stExpandSidebarButton"] {
            display: none !important;
        }
        div[class*="st-key-options"] {
            position: relative;
        }
        div[class*="st-key-menu_option"] {
            position: absolute;
            bottom: calc(100% + 0.5rem);
            left: 0;
            right: 0;
            z-index: 1000;
            background: #1c1c22;
            border: 1px solid rgba(201,164,76,.55);
            border-radius: 0.6rem;
            padding: 0.8rem;
            box-shadow: 0 8px 28px rgba(0,0,0,.6);
        }
        div[class*="st-key-validation_"] {
            display: flex;
            flex-direction: column;
            align-items: center;
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
            /* Le conteneur rogne ce qui dépasse : la marge laisse la place à la lueur des dalles choisies. */
            padding: 1rem 1rem 0.6rem;
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
        div[class*="st-key-dalles_flair_"] button {
            background: rgba(150,80,20,.3);
            border-color: rgba(220,140,60,.55);
        }
        div[class*="st-key-dalles_flair_"] button:hover {
            background: rgba(190,100,28,.6);
            border-color: #e8953f;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(232,149,63,.45);
        }
        div[class*="st-key-dalles_flair_"] button::after { content: "👃"; }
        div[class*="st-key-dalles_cupi_"] button {
            background: rgba(150,40,90,.3);
            border-color: rgba(230,100,150,.55);
        }
        div[class*="st-key-dalles_cupi_"] button:hover {
            background: rgba(190,50,110,.6);
            border-color: #e8649a;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(232,100,154,.45);
        }
        div[class*="st-key-dalles_cupi_"] button::after { content: "💘"; }
        div[class*="st-key-dalles_maire_"] button::after { content: "👑"; }
        div[class*="st-key-dalles_vote_"] button {
            background: rgba(120,60,20,.35);
            border-color: rgba(210,120,50,.55);
        }
        div[class*="st-key-dalles_vote_"] button:hover {
            background: rgba(170,80,25,.65);
            border-color: #e0843f;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(224,132,63,.45);
        }
        div[class*="st-key-dalles_vote_"] button::after { content: "⚖️"; }
        div[class*="st-key-dalles_"] button[data-testid="stBaseButton-primary"] {
            border-width: 3px;
            border-color: #f0d890;
            color: #ffffff;
            box-shadow: 0 0 14px rgba(240,216,144,.55);
        }
        div[class*="st-key-dalles_flair_"] button[data-testid="stBaseButton-primary"] {
            background: rgba(200,110,30,.75);
        }
        div[class*="st-key-dalles_cupi_"] button[data-testid="stBaseButton-primary"] {
            background: rgba(200,60,120,.75);
        }
        div[class*="st-key-dalles_vote_"] button[data-testid="stBaseButton-primary"] {
            background: rgba(190,90,30,.75);
        }
        div[class*="st-key-dalles_"] button[data-testid="stBaseButton-primary"]::after {
            opacity: 1;
        }
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


CSS_SCENES = """
<style>
.ciel {
    position: relative;
    height: 250px;
    max-width: 1000px;
    container-type: inline-size;
    margin: 0.4rem auto 1.2rem;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid rgba(201,164,76,.55);
    box-shadow: 0 8px 28px rgba(0,0,0,.5);
}
.ciel-nuit { background: linear-gradient(180deg, #060a22 0%, #131c4a 55%, #2b3072 100%); }
.ciel-jour { background: linear-gradient(180deg, #34346f 0%, #b5638f 40%, #f2a468 72%, #ffe3a0 100%); }
.ciel-etoile {
    position: absolute;
    border-radius: 50%;
    background: #fff8dc;
    animation: scintille 2.8s ease-in-out infinite;
}
.ciel-astre { position: absolute; border-radius: 50%; }
.ciel-lune {
    width: 62px; height: 62px; right: 16%; top: 22px;
    background:
        radial-gradient(circle at 30% 35%, rgba(190,180,140,.55) 0 7px, transparent 8px),
        radial-gradient(circle at 62% 60%, rgba(190,180,140,.5) 0 9px, transparent 10px),
        radial-gradient(circle at 55% 25%, rgba(190,180,140,.4) 0 4px, transparent 5px),
        #f6efcf;
    box-shadow: 0 0 22px 6px rgba(246,239,207,.45), 0 0 70px 24px rgba(246,239,207,.18);
    animation: monte-lune 2.4s ease-out both;
}
.ciel-soleil {
    width: 74px; height: 74px; left: 50%; margin-left: -37px; bottom: 58px;
    background: radial-gradient(circle, #fff6c2 0%, #ffd45c 55%, #ffb03b 100%);
    box-shadow: 0 0 26px 10px rgba(255,200,90,.6), 0 0 90px 40px rgba(255,170,80,.3);
    animation: monte-soleil 2.6s ease-out both;
}
.ciel-nuage {
    position: absolute;
    height: 22px;
    border-radius: 22px;
    animation: derive linear infinite;
}
.ciel-nuage::before, .ciel-nuage::after {
    content: "";
    position: absolute;
    background: inherit;
    border-radius: 50%;
}
.ciel-nuage::before { width: 34px; height: 34px; left: 14px; top: -16px; }
.ciel-nuage::after { width: 26px; height: 26px; left: 42px; top: -10px; }
.ciel-nuit .ciel-nuage { background: rgba(120,130,190,.28); }
.ciel-jour .ciel-nuage { background: rgba(255,240,225,.88); }
.ciel-village { position: absolute; left: 0; right: 0; bottom: 0; height: 70px; }
.ciel-maison {
    position: absolute;
    bottom: 0;
    clip-path: polygon(0 38%, 50% 0, 100% 38%, 100% 100%, 0 100%);
}
.ciel-nuit .ciel-maison { background: #080b1c; }
.ciel-jour .ciel-maison { background: #2b2140; }
.ciel-maison::after {
    content: "";
    position: absolute;
    left: 28%; bottom: 22%;
    width: 16%; height: 20%;
    background: #ffd76a;
    box-shadow: 0 0 6px 2px rgba(255,215,106,.7), calc(var(--l, 40px) * 0.7) 0 0 0 #ffd76a;
    opacity: 0;
}
.ciel-nuit .ciel-maison::after { opacity: 1; animation: fenetre 5s ease-in-out infinite; }
.ciel-sol {
    position: absolute; left: 0; right: 0; bottom: 0; height: 12px;
}
.ciel-nuit .ciel-sol { background: #05071a; }
.ciel-jour .ciel-sol { background: #221a33; }
.ciel-texte {
    position: absolute; left: 0; right: 0; top: 26%;
    text-align: center;
    animation: apparait 1.6s ease-out both;
}
.ciel-titre {
    font-family: 'Cinzel', serif;
    font-weight: 700;
    font-size: clamp(1.4rem, 4vw, 2.1rem);
    letter-spacing: .06em;
    color: #fff4d0;
    text-shadow: 0 2px 14px rgba(0,0,0,.7), 0 0 26px rgba(255,220,130,.35);
}
.ciel-sous {
    font-family: 'EB Garamond', serif;
    font-size: 1.1rem;
    color: #ece3d2;
    text-shadow: 0 1px 8px rgba(0,0,0,.8);
    margin-top: .2rem;
}
.ciel-victoire-village { background: linear-gradient(180deg, #3b86d0 0%, #86c4ee 55%, #ffeeba 100%); }
.ciel-victoire-village .ciel-nuage { background: rgba(255,255,255,.92); }
.ciel-victoire-village .ciel-maison { background: #a4573a; }
.ciel-victoire-village .ciel-sol { background: #3f7d3a; }
.ciel-rayons {
    position: absolute; left: 50%; top: -190px; width: 460px; height: 460px; margin-left: -230px;
    border-radius: 50%;
    background: repeating-conic-gradient(rgba(255,240,170,.38) 0 7deg, transparent 7deg 22deg);
    -webkit-mask-image: radial-gradient(circle, #000 15%, transparent 68%);
    mask-image: radial-gradient(circle, #000 15%, transparent 68%);
    animation: tourne 60s linear infinite;
}
.ciel-soleil-haut {
    width: 70px; height: 70px; left: 50%; margin-left: -35px; top: 8px;
    background: radial-gradient(circle, #fffbd6 0%, #ffe066 55%, #ffb733 100%);
    box-shadow: 0 0 24px 10px rgba(255,214,90,.7), 0 0 80px 34px rgba(255,200,80,.35);
}
.ciel-confetti {
    position: absolute; top: -14px; width: 7px; height: 12px; opacity: 0;
    animation: chute linear infinite;
}
.ciel-victoire-loups { background: linear-gradient(180deg, #12030a 0%, #4a0d1c 52%, #a3302f 100%); }
.ciel-victoire-loups .ciel-etoile { background: #ffd0c0; }
.ciel-victoire-loups .ciel-nuage { background: rgba(60,10,20,.45); }
.ciel-victoire-loups .ciel-maison { background: #0a0308; }
.ciel-victoire-loups .ciel-sol { background: #050205; }
.ciel-victoire-loups .ciel-titre { color: #ffd9d0; text-shadow: 0 2px 14px rgba(0,0,0,.85), 0 0 26px rgba(255,60,50,.45); }
.ciel-lune-sang {
    width: 120px; height: 120px; right: 9%; top: 60px;
    background: radial-gradient(circle at 38% 34%, #ff9a72 0%, #d8352e 55%, #8f1420 100%);
    box-shadow: 0 0 30px 10px rgba(230,50,40,.5), 0 0 110px 44px rgba(200,30,30,.28);
    animation: monte-lune 2.4s ease-out both, pulse-sang 4s ease-in-out 2.4s infinite;
}
.ciel-colline {
    position: absolute; right: -8%; bottom: -70px; width: 46%; height: 130px;
    border-radius: 50%; background: #050205;
}
.ciel-loup {
    position: absolute; right: 16%; bottom: 52px; font-size: 64px; line-height: 1;
    filter: brightness(0);
}
.ciel-chauve {
    position: absolute; font-size: 20px; line-height: 1; filter: brightness(0);
    animation: vole linear infinite;
}
@keyframes tourne { to { transform: rotate(360deg); } }
@keyframes chute {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    100% { transform: translateY(270px) rotate(540deg); opacity: 1; }
}
@keyframes pulse-sang { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.06); } }
@keyframes vole {
    0% { transform: translate(-40px, 0); }
    25% { transform: translate(25cqw, 18px); }
    50% { transform: translate(50cqw, -6px); }
    75% { transform: translate(75cqw, 14px); }
    100% { transform: translate(100cqw, 0); }
}
@keyframes scintille { 0%, 100% { opacity: .25; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.25); } }
@keyframes derive { from { transform: translateX(-140px); } to { transform: translateX(100cqw); } }
@keyframes monte-lune { from { transform: translateY(70px); opacity: 0; } to { transform: none; opacity: 1; } }
@keyframes monte-soleil { from { transform: translateY(90px); } to { transform: none; } }
@keyframes apparait { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes fenetre { 0%, 100% { opacity: 1; } 45% { opacity: .55; } 60% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .ciel *, .ciel, .avis-papier { animation: none !important; } }
.avis { position: relative; max-width: 470px; margin: .2rem auto 1.2rem; padding: 0 24px 16px; }
.avis-poteau {
    position: absolute; bottom: 0; top: 24px; width: 18px; z-index: 0;
    background: linear-gradient(90deg, #3a220f, #5e3a1e 50%, #3a220f);
    border-radius: 3px;
}
.avis-poteau-g { left: 28px; }
.avis-poteau-d { right: 28px; }
.avis-planche {
    position: relative; z-index: 1;
    padding: 1rem 1.1rem 1.1rem;
    border: 3px solid #4a2c17;
    border-radius: 8px;
    background:
        repeating-linear-gradient(90deg, rgba(0,0,0,.09) 0 2px, transparent 2px 52px),
        linear-gradient(180deg, #8f5f37 0%, #6d4425 100%);
    box-shadow: 0 10px 26px rgba(0,0,0,.55), inset 0 0 26px rgba(0,0,0,.35);
}
.avis-planche::before {
    content: ""; position: absolute; left: -14px; right: -14px; top: -18px; height: 20px;
    border-radius: 8px 8px 2px 2px; background: linear-gradient(180deg, #55351c, #3a2212);
    box-shadow: 0 3px 6px rgba(0,0,0,.5);
}
.avis-titre {
    text-align: center; font-family: 'Cinzel', serif; font-weight: 700;
    font-size: clamp(.95rem, 2.4vw, 1.2rem); letter-spacing: .12em; text-transform: uppercase;
    color: #f7e8c4; text-shadow: 0 2px 6px rgba(0,0,0,.65);
}
.avis-sous {
    text-align: center; font-family: 'EB Garamond', serif; font-style: italic;
    color: #ecd9ad; margin: .05rem 0 .7rem; font-size: .95rem;
}
.avis-papiers { display: flex; flex-direction: column; gap: .7rem; }
.avis-papier {
    position: relative;
    padding: .55rem 1rem .5rem 1.1rem;
    background: linear-gradient(170deg, #f3e6c0 0%, #e6d3a3 100%);
    color: #3b2a14;
    border-left: 6px solid #a53a32;
    box-shadow: 0 4px 10px rgba(0,0,0,.5);
    transform: rotate(-.7deg);
    animation: colle .6s ease-out both;
}
.avis-papier:nth-child(even) { transform: rotate(.6deg); animation-delay: .25s; }
.avis-papier::before {
    content: ""; position: absolute; top: -6px; left: 50%; width: 12px; height: 12px; margin-left: -6px;
    border-radius: 50%; background: radial-gradient(circle at 35% 30%, #ff8a7a, #b3261e 70%);
    box-shadow: 0 2px 3px rgba(0,0,0,.5);
}
.avis-papier-calme { border-left-color: #5e8c55; text-align: center; }
.avis-nom {
    font-family: 'Cinzel', serif; font-weight: 700; font-size: 1.05rem; letter-spacing: .04em;
}
.avis-detail { font-family: 'EB Garamond', serif; font-style: italic; font-size: .98rem; margin-top: 0; }
@keyframes colle { from { opacity: 0; transform: translateY(-14px) rotate(-3deg); } }
</style>
"""


def _svg_css(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="") + '")'


def _village_svg(couleur_mur="#080b1c", fenetre="#ffd76a", sol="#05071a"):
    maisons = ((30, 70, 46), (120, 90, 78), (230, 64, 52), (310, 100, 96), (430, 74, 56), (520, 96, 84),
               (640, 66, 50), (730, 92, 76), (840, 72, 56), (920, 70, 60))
    corps = []
    for x, largeur, hauteur in maisons:
        bas, mur = 130, hauteur * 0.38
        corps.append(f'<polygon fill="{couleur_mur}" points="{x},{bas} {x},{bas - hauteur + mur:.0f} {x + largeur / 2:.0f},{bas - hauteur} '
                     f'{x + largeur},{bas - hauteur + mur:.0f} {x + largeur},{bas}"/>')
        if fenetre:
            corps.append(f'<rect fill="{fenetre}" x="{x + largeur * 0.3:.0f}" y="{bas - 30}" width="{max(largeur * 0.16, 8):.0f}" height="14"/>')
            if largeur > 80:
                corps.append(f'<rect fill="{fenetre}" x="{x + largeur * 0.6:.0f}" y="{bas - 30}" width="{largeur * 0.16:.0f}" height="14"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="130" viewBox="0 0 1000 130">'
            + "".join(corps) + f'<rect y="116" width="1000" height="14" fill="{sol}"/></svg>')


def _nuages_svg(couleur="#7882be", opacite=0.3):
    nuages = ((60, 40, 1.0), (420, 90, 0.7), (760, 30, 0.85), (1050, 80, 0.6), (1250, 45, 0.9))
    corps = "".join(
        f'<g fill="{couleur}" opacity="{opacite}"><rect x="{x}" y="{y}" width="{110 * k:.0f}" height="{24 * k:.0f}" rx="{12 * k:.0f}"/>'
        f'<circle cx="{x + 34 * k:.0f}" cy="{y - 2 * k:.0f}" r="{18 * k:.0f}"/><circle cx="{x + 68 * k:.0f}" cy="{y + 4 * k:.0f}" r="{14 * k:.0f}"/></g>'
        for x, y, k in nuages
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="200" viewBox="0 0 1400 200">{corps}</svg>'


CSS_PASSAGE = """
<style>
div[class*="st-key-scene_passage"] {
    position: relative;
    max-width: 1150px;
    margin: 0.4rem auto 1rem;
    padding: 2.2rem 1.6rem 150px;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid rgba(201,164,76,.55);
    box-shadow: 0 8px 28px rgba(0,0,0,.5);
    background-color: #131c4a;
    background-image:
        __NUAGES__,
        radial-gradient(circle at calc(100% - 110px) 74px, #f6efcf 0 30px, rgba(246,239,207,.4) 34px, rgba(246,239,207,.12) 80px, transparent 140px),
        linear-gradient(180deg, #060a22 0%, #131c4a 55%, #2b3072 100%);
    background-repeat: repeat-x, no-repeat, no-repeat;
    background-size: 1400px 200px, auto, auto;
    background-position: 0 0, 0 0, 0 0;
    animation: passage-nuages 90s linear infinite;
}
div[class*="st-key-scene_passage"]::before {
    content: "";
    position: absolute;
    inset: 0 0 35% 0;
    pointer-events: none;
    background-image:
        radial-gradient(1.5px 1.5px at 20px 30px, #fff8dc, transparent),
        radial-gradient(1px 1px at 90px 120px, #fff8dc, transparent),
        radial-gradient(2px 2px at 160px 60px, #fff8dc, transparent),
        radial-gradient(1px 1px at 210px 150px, #fff8dc, transparent),
        radial-gradient(1px 1px at 60px 175px, #fff8dc, transparent),
        radial-gradient(2px 2px at 120px 10px, #fff8dc, transparent);
    background-size: 240px 200px;
    animation: passage-etoiles 3s ease-in-out infinite;
}
div[class*="st-key-scene_passage"]::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 130px;
    pointer-events: none;
    background: __VILLAGE__ repeat-x left bottom / 1000px 130px;
}
div[class*="st-key-scene_passage"] > * { position: relative; z-index: 1; }
div[class*="st-key-scene_passage"] h2 {
    text-align: center;
    color: #fff4d0;
    text-shadow: 0 2px 14px rgba(0,0,0,.7);
}
div[class*="st-key-scene_passage"] .plaquette { max-width: 640px; margin: 0.7rem auto; background: rgba(8,10,28,.72); }
@keyframes passage-etoiles { 0%, 100% { opacity: .3; } 50% { opacity: 1; } }
@keyframes passage-nuages {
    from { background-position: 0 0, 0 0, 0 0; }
    to { background-position: 1400px 0, 0 0, 0 0; }
}
@media (prefers-reduced-motion: reduce) {
    div[class*="st-key-scene_passage"], div[class*="st-key-scene_passage"]::before { animation: none !important; }
}
</style>
""".replace("__VILLAGE__", _svg_css(_village_svg())).replace("__NUAGES__", _svg_css(_nuages_svg()))


CSS_ACCUEIL = """
<style>
div[class*="st-key-scene_accueil"] {
    position: relative;
    max-width: 1150px;
    min-height: 580px;
    margin: 0.4rem auto 1rem;
    padding: 2rem 1.6rem 150px;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid rgba(201,164,76,.55);
    box-shadow: 0 8px 28px rgba(0,0,0,.5);
    background: #1a1240;
    justify-content: center;
    align-items: center;
}
div[class*="st-key-scene_accueil"] > * { position: relative; z-index: 2; width: 100%; }
div[class*="st-key-scene_accueil"] > div[data-testid="stElementContainer"]:has(.acc-fond) {
    position: absolute; inset: 0; z-index: 0; width: auto;
}
.acc-fond { position: absolute; inset: 0; overflow: hidden; container-type: inline-size; }
.acc-couche {
    position: absolute; inset: 0; opacity: 0;
    background-repeat: repeat-x, no-repeat;
    background-size: 1400px 200px, auto;
    animation: acc-fondu 48s linear infinite, acc-nuages 90s linear infinite;
}
.acc-jour { opacity: 1;
    background-image: __N_JOUR__, linear-gradient(180deg, #34346f 0%, #b5638f 40%, #f2a468 72%, #ffe3a0 100%); }
.acc-nuit { animation-delay: -36s, 0s;
    background-image: __N_NUIT__, linear-gradient(180deg, #060a22 0%, #131c4a 55%, #2b3072 100%); }
.acc-loups { animation-delay: -24s, 0s;
    background-image: __N_LOUPS__, linear-gradient(180deg, #12030a 0%, #4a0d1c 52%, #a3302f 100%); }
.acc-victoire { animation-delay: -12s, 0s;
    background-image: __N_VICT__, linear-gradient(180deg, #3b86d0 0%, #86c4ee 55%, #ffeeba 100%); }
.acc-nuit::before, .acc-loups::before {
    content: ""; position: absolute; inset: 0 0 35% 0; pointer-events: none;
    color: #fff8dc;
    background-image:
        radial-gradient(1.5px 1.5px at 20px 30px, currentColor, transparent),
        radial-gradient(1px 1px at 90px 120px, currentColor, transparent),
        radial-gradient(2px 2px at 160px 60px, currentColor, transparent),
        radial-gradient(1px 1px at 210px 150px, currentColor, transparent),
        radial-gradient(1px 1px at 60px 175px, currentColor, transparent),
        radial-gradient(2px 2px at 120px 10px, currentColor, transparent);
    background-size: 240px 200px;
    animation: passage-etoiles 3s ease-in-out infinite;
}
.acc-loups::before { color: #ffd0c0; }
.acc-couche::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 130px; pointer-events: none;
    background-repeat: repeat-x; background-position: left bottom; background-size: 1000px 134px;
}
.acc-jour::after { background-image: __V_JOUR__; }
.acc-nuit::after { background-image: __V_NUIT__; }
.acc-loups::after { background-image: __V_LOUPS__; right: auto; width: 62%; }
.acc-victoire::after { background-image: __V_VICT__; }
.acc-couche .ciel-soleil { left: 20%; bottom: 110px; }
.acc-couche .ciel-lune { width: 84px; height: 84px; right: 12%; top: 60px; }
.acc-couche .ciel-lune-sang { width: 150px; height: 150px; right: 12%; top: 50px; }
.acc-couche .ciel-colline { bottom: -90px; height: 190px; }
.acc-couche .ciel-loup { right: 14%; bottom: 92px; font-size: 84px; }
.acc-couche .ciel-rayons, .acc-couche .ciel-soleil-haut { left: 80%; }
.acc-couche .ciel-confetti { animation-name: acc-chute; }
.acc-titre-bloc { text-align: center; }
.acc-surtitre { font-size: 3.2rem; line-height: 1; filter: drop-shadow(0 3px 10px rgba(0,0,0,.6)); }
.acc-titre {
    font-family: 'Cinzel', serif; font-weight: 700; text-transform: uppercase;
    font-size: clamp(2rem, 6vw, 3.6rem); letter-spacing: .08em; color: #fff4d0;
    text-shadow: 0 3px 18px rgba(0,0,0,.75), 0 0 34px rgba(255,220,130,.35);
}
.acc-sous {
    font-family: 'EB Garamond', serif; font-style: italic; font-size: 1.25rem; color: #f3ead8;
    text-shadow: 0 1px 10px rgba(0,0,0,.85); margin: .3rem 0 1.4rem;
}
div[class*="st-key-accueil_btn_"] button {
    min-width: 230px; padding: .7rem 1.6rem;
    box-shadow: 0 4px 14px rgba(0,0,0,.5);
}
div[class*="st-key-accueil_btn_"] button p {
    font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 600; letter-spacing: .06em;
}
div[class*="st-key-accueil_btn_nouvelle"] button { background-color: #3f7d4f; border-color: #2f5f3b; color: #f2e9d8; }
div[class*="st-key-accueil_btn_nouvelle"] button:hover { background-color: #4a9059; border-color: #3f7d4f; color: #fff; }
div[class*="st-key-accueil_btn_historique"] button {
    background-color: rgba(8,10,28,.75); border: 1.5px solid rgba(201,164,76,.85); color: #fff4d0;
}
div[class*="st-key-accueil_btn_historique"] button:hover { background-color: rgba(30,28,70,.85); border-color: #e2c274; color: #fff; }
@keyframes acc-fondu { 0%, 20% { opacity: 1; } 25%, 95% { opacity: 0; } 100% { opacity: 1; } }
@keyframes acc-nuages {
    from { background-position: 0 0, 0 0; }
    to { background-position: 1400px 0, 0 0; }
}
@keyframes acc-chute {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    100% { transform: translateY(620px) rotate(540deg); opacity: 1; }
}
@media (prefers-reduced-motion: reduce) { .acc-couche, .acc-couche *, .acc-couche::before { animation: none !important; } }
</style>
""".replace("__N_JOUR__", _svg_css(_nuages_svg("#fff0e1", 0.8))
).replace("__N_NUIT__", _svg_css(_nuages_svg())
).replace("__N_LOUPS__", _svg_css(_nuages_svg("#3c0a14", 0.45))
).replace("__N_VICT__", _svg_css(_nuages_svg("#ffffff", 0.92))
).replace("__V_JOUR__", _svg_css(_village_svg("#2b2140", None, "#221a33"))
).replace("__V_NUIT__", _svg_css(_village_svg())
).replace("__V_LOUPS__", _svg_css(_village_svg("#0a0308", None, "#050205"))
).replace("__V_VICT__", _svg_css(_village_svg("#a4573a", "#fff2b0", "#3f7d3a")))

CSS_SANS_SIDEBAR = """
<style>
section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] { display: none; }
</style>
"""


def scene_ciel(mode, titre, sous_titre=""):
    """Bandeau animé : "nuit" (lune, étoiles) ou "jour" (lever de soleil), nuages et village."""
    rnd = random.Random(7)
    elements = []
    if mode == "nuit":
        for _ in range(34):
            taille = rnd.choice((1, 1, 2, 2, 3))
            elements.append(
                f'<span class="ciel-etoile" style="left:{rnd.uniform(1, 99):.1f}%;top:{rnd.uniform(3, 62):.1f}%;'
                f'width:{taille}px;height:{taille}px;animation-delay:-{rnd.uniform(0, 3):.1f}s"></span>'
            )
        elements.append('<div class="ciel-astre ciel-lune"></div>')
    else:
        elements.append('<div class="ciel-astre ciel-soleil"></div>')
    for i, (haut, largeur, duree) in enumerate(((16, 70, 46), (52, 90, 62), (34, 60, 54))):
        elements.append(
            f'<div class="ciel-nuage" style="top:{haut}%;width:{largeur}px;'
            f'animation-duration:{duree}s;animation-delay:-{i * 17}s"></div>'
        )
    maisons = ((3, 46, 40), (15, 60, 52), (31, 42, 36), (46, 70, 56), (64, 50, 44), (77, 64, 50), (90, 40, 34))
    elements.append('<div class="ciel-village">' + "".join(
        f'<div class="ciel-maison" style="left:{gauche}%;width:{largeur}px;height:{hauteur}px;--l:{largeur}px"></div>'
        for gauche, largeur, hauteur in maisons
    ) + '<div class="ciel-sol"></div></div>')
    sous = f'<div class="ciel-sous">{sous_titre}</div>' if sous_titre else ""
    elements.append(f'<div class="ciel-texte"><div class="ciel-titre">{titre}</div>{sous}</div>')
    st.markdown(
        f'<div class="ciel ciel-{mode}">' + "".join(elements) + "</div>", unsafe_allow_html=True,
    )


def scene_victoire(camp_gagnant, titre, sous_titre=""):
    """Bandeau animé de fin de partie : "village" (fête sous le soleil) ou "loups" (lune de sang)."""
    rnd = random.Random(11)
    elements = []
    if camp_gagnant == "village":
        elements.append('<div class="ciel-rayons"></div><div class="ciel-astre ciel-soleil-haut"></div>')
        couleurs = ("#ff5a5a", "#ffd23f", "#4cc9f0", "#7bd88f", "#f78fd0", "#ffffff")
        for _ in range(34):
            elements.append(
                f'<span class="ciel-confetti" style="left:{rnd.uniform(1, 99):.1f}%;'
                f'background:{rnd.choice(couleurs)};animation-duration:{rnd.uniform(3.2, 5.6):.1f}s;'
                f'animation-delay:-{rnd.uniform(0, 5):.1f}s"></span>'
            )
    else:
        for _ in range(30):
            taille = rnd.choice((1, 1, 2, 2, 3))
            elements.append(
                f'<span class="ciel-etoile" style="left:{rnd.uniform(1, 99):.1f}%;top:{rnd.uniform(3, 55):.1f}%;'
                f'width:{taille}px;height:{taille}px;animation-delay:-{rnd.uniform(0, 3):.1f}s"></span>'
            )
        elements.append('<div class="ciel-astre ciel-lune-sang"></div>')
        for i, (haut, duree) in enumerate(((14, 14), (30, 19), (8, 23))):
            elements.append(
                f'<span class="ciel-chauve" style="top:{haut}%;animation-duration:{duree}s;'
                f'animation-delay:-{i * 6}s">🦇</span>'
            )
    for i, (haut, largeur, duree) in enumerate(((16, 70, 46), (52, 90, 62))):
        elements.append(
            f'<div class="ciel-nuage" style="top:{haut}%;width:{largeur}px;'
            f'animation-duration:{duree}s;animation-delay:-{i * 21}s"></div>'
        )
    maisons = ((3, 46, 40), (15, 60, 52), (31, 42, 36), (46, 70, 56), (64, 50, 44), (77, 64, 50), (90, 40, 34))
    elements.append('<div class="ciel-village">' + "".join(
        f'<div class="ciel-maison" style="left:{gauche}%;width:{largeur}px;height:{hauteur}px"></div>'
        for gauche, largeur, hauteur in maisons
    ) + '<div class="ciel-sol"></div></div>')
    if camp_gagnant == "loups":
        elements.append('<div class="ciel-colline"></div><span class="ciel-loup">🐺</span>')
    sous = f'<div class="ciel-sous">{sous_titre}</div>' if sous_titre else ""
    elements.append(f'<div class="ciel-texte"><div class="ciel-titre">{titre}</div>{sous}</div>')
    st.markdown(
        f'<div class="ciel ciel-victoire-{camp_gagnant}">' + "".join(elements) + "</div>", unsafe_allow_html=True,
    )


def annonce(texte, signe="!", ton="alerte"):
    """Encart d'annonce avec pastille "!" ou "?" ; ton : alerte, danger, succes, mystere."""
    st.markdown(
        f'<div class="annonce annonce-{ton}"><span class="annonce-signe">{signe}</span>'
        f'<span class="annonce-texte">{html.escape(texte)}</span></div>',
        unsafe_allow_html=True,
    )


def plaquette(texte, icone="🌙", ton="neutre"):
    classe = "plaquette" if ton == "neutre" else f"plaquette plaquette-{ton}"
    st.markdown(
        f'<div class="{classe}"><span class="plaquette-icone">{icone}</span><span class="plaquette-texte">{texte}</span></div>',
        unsafe_allow_html=True,
    )


def grille_dalles(theme, cle, choix, selection=()):
    """Dalles cliquables (style selon `theme`, cf. CSS). Renvoie le nom cliqué ou None.
    Les noms de `selection` sont affichés en surbrillance."""
    # Plus il y a de choix, plus on élargit la grille : elle reste sur peu de lignes.
    n_col = 2 if len(choix) <= 4 else 3 if len(choix) <= 9 else 4 if len(choix) <= 14 else 5
    clic = None
    with st.container(key=f"dalles_{theme}_{cle}"):
        cols = st.columns(n_col)
        for i, nom in enumerate(choix):
            with cols[i % n_col]:
                choisi = nom in selection
                if st.button(
                    nom, key=f"pick_{theme}_{cle}_{nom}", use_container_width=True,
                    type="primary" if choisi else "secondary",
                ):
                    clic = nom
    return clic


def selection_dalles(theme, cle, choix, k):
    """Dalles où l'on en sélectionne `k` (re-cliquer désélectionne). Renvoie la sélection courante."""
    cle_sel = f"sel_{theme}_{cle}"
    sel = [n for n in st.session_state.get(cle_sel, []) if n in choix]
    clic = grille_dalles(theme, cle, choix, selection=sel)
    if clic:
        sel = [n for n in sel if n != clic] if clic in sel else (sel + [clic])[-k:]
        st.session_state[cle_sel] = sel
        st.rerun()
    return sel


def bouton_validation(libelle, cle, disabled=False):
    """Bouton de validation d'une sélection de dalles, centré sous la grille."""
    with st.container(key=f"validation_{cle}"):
        return st.button(libelle, type="primary", disabled=disabled, key=cle)


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
    choix = selection_dalles("loup", cle, cibles, 1)
    cible = choix[0] if choix else None
    if bouton_validation(
        f"🐺 Dévorer {cible}" if cible else "🐺 Dévorer", f"devorer_{cle}", disabled=cible is None,
    ):
        s["votes_loups"].append(cible)
        log(s, f"{nom} ({ROLES[s['joueurs'][nom]['role']].nom}) désigne {cible}.")
        st.session_state.pop(f"sel_loup_{cle}", None)
        return True
    return False


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
    groupe = selection_dalles("flair", cle, candidats, k)
    if bouton_validation("Flairer", f"flairer_{cle}", disabled=len(groupe) != k):
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
        choix = selection_dalles("voy", cle, candidats, 1)
        vu = choix[0] if choix else None
        if bouton_validation(
            f"🔮 Sonder {vu}" if vu else "🔮 Sonder", f"sonder_{cle}", disabled=vu is None,
        ):
            log(s, f"La voyante {nom} sonde {vu} : {ROLES[s['joueurs'][vu]['role']].nom}.")
            st.session_state[f"vu_{cle}"] = vu
            st.rerun()


def _nuit_sorciere(s, nom, cle):
    if s["jour"] == 0 or s["potions_sorciere"] == 0:
        plaquette("Rien à faire cette nuit.", icone="🌙")
        bouton_fin(s, cle)
    else:
        n = s["potions_sorciere"]
        st.markdown(
            f'<div class="potion-bandeau"><span class="potion-fioles">{"🧪" * n}</span>'
            f'<span class="potion-texte">Potion{"s" if n > 1 else ""} de soin restante{"s" if n > 1 else ""} : {n}</span></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="sorciere_boutons", horizontal=True, horizontal_alignment="center"):
            soigne = st.button("Utiliser une potion", type="primary", key=f"soin_{cle}")
            rien = st.button("Ne rien faire", key=f"rien_{cle}")
        if soigne:
            s["soin_sorciere"] = True
            s["potions_sorciere"] -= 1
            log(s, f"La sorcière {nom} utilise une potion de soin.")
            fin_de_tour(s)
            st.rerun()
        if rien:
            fin_de_tour(s)
            st.rerun()


def _nuit_cupidon(s, nom, cle):
    if s["jour"] > 0:
        plaquette("Ton travail est fait. Dors.", icone="🏹")
        bouton_fin(s, cle)
    else:
        st.markdown("**Qui lies-tu par l'amour ?**")
        st.caption("Choisis deux joueurs (toi compris).")
        couple = selection_dalles("cupi", cle, list(s["joueurs"].keys()), 2)
        if bouton_validation("Décocher la flèche", f"ok_cup_{cle}", disabled=len(couple) != 2):
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
        etat_initial={"potions_sorciere": 1, "soin_sorciere": False},
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
    """Écrit le journal complet dans historique/ (une seule fois par partie terminée)."""
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


def prendre_instantane(s, genre):
    """Copie l'état de la partie au début d'une nuit ("nuit") ou à l'annonce du réveil ("jour")."""
    if genre == "nuit":
        libelle = f"🌙 Nuit {s['jour']} · début de la nuit"
    else:
        libelle = f"☀️ Jour {s['jour']} · annonce du réveil"
    cle = f"{genre}_{s['jour']}"
    instantanes = s.setdefault("instantanes", [])
    # Une étape rejouée (après un rechargement) remplace sa version précédente et toutes celles d'après.
    for i, inst in enumerate(instantanes):
        if inst["id"] == cle:
            del instantanes[i:]
            break
    etat = copy.deepcopy({k: v for k, v in s.items() if k != "instantanes"})
    instantanes.append({"id": cle, "libelle": libelle, "etat": etat})


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


def etapes_chronologie(s):
    """Étapes à afficher : le départ (nuit 0 et jour 0 regroupés), puis chaque nuit et chaque jour."""
    etapes = [("start", 0)]
    for j in range(1, s["jour"] + 1):
        etapes.append(("nuit", j))
        if j < s["jour"] or s["phase"] != "nuit":
            etapes.append(("jour", j))
    return etapes


def chronologie_html(s):
    etapes = etapes_chronologie(s)
    pas = []
    for i, (genre, jour) in enumerate(etapes):
        actuel = " chrono-actuel" if i == len(etapes) - 1 else ""
        if genre == "start":
            icone, nom, etiquette, debut = "▶", "Départ", "start", " chrono-debut"
        else:
            icone, nom = ("🌙", "Nuit") if genre == "nuit" else ("☀️", "Jour")
            etiquette, debut = str(jour), ""
        titre = nom if genre == "start" else f"{nom} {jour}"
        lien = '<div class="chrono-lien"></div>' if i < len(etapes) - 1 else ""
        pas.append(
            f'<div class="chrono-pas"><div class="chrono-etape{debut}" title="{titre}">'
            f'<div class="chrono-noeud chrono-{genre}{actuel}">{icone}</div>'
            f'<span class="chrono-label">{etiquette}</span></div>{lien}</div>'
        )
    return '<div class="chrono">' + "".join(pas) + "</div>"


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
    if st.button("← Menu", key="retour_menu_installation"):
        aller_a("accueil")
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
            {lignes}
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
    with st.container(key="setup_roles"):
        st.markdown("##### 1. Composition de la partie")

        # Réservé ici pour apparaître avant "Nombre de joueurs", rempli une fois
        # les rôles ci-dessous connus.
        apercu = st.empty()

        nb = st.number_input(
            "Nombre de joueurs",
            min_value=5,
            max_value=18,
            value=7,
            step=1,
            key="nb_joueurs_setup",
        )

        loups_defaut, speciaux_defaut = composition_recommandee(nb)

        st.markdown(f"**{ROLES['loup'].emoji} {ROLES['loup'].nom}**")
        n_loup = st.number_input(
            f"{ROLES['loup'].emoji} {ROLES['loup'].nom}s",
            min_value=1, max_value=max(1, nb - 1),
            value=min(loups_defaut, max(1, nb - 1)), key="n_loup",
            label_visibility="collapsed",
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

        if st.button("Suivant : noms des joueurs →", type="primary", disabled=n_villageois < 0):
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
        prendre_instantane(s, "nuit")
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
        if s["tour"] == 0:
            scene_ciel("nuit", "La nuit tombe", "Première nuit" if s["jour"] == 0 else f"Nuit {s['jour']}")
        with st.container(key="scene_passage"):
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
    prendre_instantane(s, "jour")


def _camp_txt(s, nom):
    role = ROLES[s["joueurs"][nom]["role"]]
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
    if s["morts_nuit"] and len(s["amoureux"]) == 2 and set(s["amoureux"]) <= set(s["morts_nuit"]):
        papiers.append(
            '<div class="avis-papier"><div class="avis-detail">💔 Les amoureux sont morts ensemble.</div></div>'
        )
    if not papiers:
        papiers.append(
            '<div class="avis-papier avis-papier-calme"><div class="avis-nom">🕊️ Nul n\'a péri</div>'
            '<div class="avis-detail">Le village a passé une nuit paisible.</div></div>'
        )
    sous = "Premier jour" if s["jour"] == 0 else f"Jour {s['jour']}"
    st.markdown(
        '<div class="avis"><div class="avis-poteau avis-poteau-g"></div><div class="avis-poteau avis-poteau-d"></div>'
        f'<div class="avis-planche"><div class="avis-titre">Avis à la population</div>'
        f'<div class="avis-sous">{sous}</div><div class="avis-papiers">{"".join(papiers)}</div></div></div>',
        unsafe_allow_html=True,
    )


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
        s["phase"] = "conseil"
        st.rerun()


def ecran_conseil(s):
    st.title("🗳️ Conseil du village")

    if s["jour"] == 0:
        annonce("Première nuit passée : pas de vote aujourd'hui.", "?", "mystere")
        if st.button("La nuit retombe", type="primary"):
            s["jour"] += 1
            s["phase"] = "nuit"
            st.rerun()
        return

    en_vie = vivants(s)

    if st.session_state.get(f"resultat_{s['jour']}"):
        for mort in st.session_state[f"resultat_{s['jour']}"]:
            if ROLES[s["joueurs"][mort]["role"]].camp_secret:
                annonce(f"{mort} {_camp_txt(s, mort)}.", "?", "mystere")
            elif camp(s, mort) == "loups":
                annonce(f"{mort} était LOUP-GAROU.", "!", "succes")
            else:
                annonce(f"{mort} n'était PAS loup-garou.", "!", "danger")
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
        st.markdown("**Le village élimine**")
        choix = selection_dalles("vote", s["jour"], en_vie, 1)
        condamne = choix[0] if choix else None
        if bouton_validation(
            f"Valider : éliminer {condamne}" if condamne else "Valider le vote",
            "valider_vote", disabled=condamne is None,
        ):
            st.session_state[f"resultat_{s['jour']}"] = tuer(s, condamne, "est éliminé par le village")
            st.session_state.pop(f"sel_vote_{s['jour']}", None)
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


def afficher_roles(joueurs):
    for nom, d in joueurs.items():
        etat = "en vie" if d["vivant"] else "mort"
        coeur = " 💘" if d["amoureux"] else ""
        ancien = " (ex-enfant sauvage)" if d.get("enfant_sauvage") else ""
        ancien += " (ex-voleur)" if d.get("voleur") else ""
        ancien += " (ex-renard)" if d.get("renard") else ""
        if d.get("camp_choisi"):
            ancien += " (loup-garou)" if d["camp_choisi"] == "loups" else " (villageois)"
        st.write(f"{ROLES[d['role']].emoji} **{nom}** — {ROLES[d['role']].nom}{ancien} ({etat}){coeur}")


def ecran_fin(s):
    message = s["message_fin"]
    if message.startswith("Le village a gagné"):
        scene_victoire("village", "Le village a gagné !", "Fin de la partie")
    elif message.startswith("Les loups ont gagné"):
        scene_victoire("loups", "Les loups ont gagné !", "Fin de la partie")
    else:
        st.title("🏁 Fin de la partie")
    st.header(message)
    st.subheader("Les rôles")
    afficher_roles(s["joueurs"])

    with st.expander("📜 Afficher le log de la partie"):
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


# Premier motif trouvé dans le texte gagne : les morts passent avant les rôles.
ICONES_EVENEMENTS = [
    ("meurt de chagrin", "💔"),
    ("abattu par le chasseur", "🔫"),
    ("renonce à tirer", "🕊️"),
    ("éliminé par le village", "⚖️"),
    ("dévoré par le Loup Blanc", "💀"),
    ("dévoré par les loups", "💀"),
    ("Personne ne meurt", "🌅"),
    ("ne s'accordent pas", "🤷"),
    ("sauvé par", "💚"),
    ("devient loup-garou", "🐺"),
    ("est élu maire", "👑"),
    ("comme successeur", "👑"),
    ("Loup Blanc", "🌕"),
    ("Chien-Loup", "🐕"),
    ("renard", "🦊"),
    ("Renard", "🦊"),
    ("voyante", "🔮"),
    ("sorcière", "🧪"),
    ("Cupidon", "💘"),
    ("salvateur", "🛡️"),
    ("mentor", "🐾"),
    ("Voleur", "🃏"),
    ("désigne", "🍖"),
]


def icone_evenement(texte):
    return next((icone for motif, icone in ICONES_EVENEMENTS if motif in texte), "▪️")


def afficher_historique(s):
    """Journal regroupé par nuit / jour, dans l'ordre chronologique (sans l'écran de début de partie)."""
    def bloc(e):
        if e["moment"] == "fin":
            return "fin", None
        return ("nuit" if e["moment"] == "nuit" else "jour"), e["jour"]

    courant = None
    lignes = []

    def vider():
        if lignes:
            st.markdown("\n".join(lignes))
            lignes.clear()

    for e in s["journal"]:
        if e["moment"] == "debut":
            continue
        b = bloc(e)
        if b != courant:
            vider()
            courant = b
            kind, jour = b
            if kind == "nuit":
                st.markdown(f"##### 🌙 Nuit {jour}" + (" · première nuit" if jour == 0 else ""))
            elif kind == "jour":
                st.markdown(f"##### ☀️ Jour {jour}")
            else:
                st.markdown("##### 🏁 Issue de la partie")
        icone = "🏆" if b[0] == "fin" else icone_evenement(e["texte"])
        lignes.append(f"- {icone} {e['texte']}")
    vider()


# --------------------------------------------------------------------------
# Menu d'accueil et historique
# --------------------------------------------------------------------------

def _fond_accueil():
    """Quatre décors qui se fondent en boucle : jour, nuit, lune de sang, victoire du village."""
    rnd = random.Random(5)
    couleurs = ("#ff5a5a", "#ffd23f", "#4cc9f0", "#7bd88f", "#f78fd0", "#ffffff")
    confettis = "".join(
        f'<span class="ciel-confetti" style="left:{rnd.uniform(1, 99):.1f}%;background:{rnd.choice(couleurs)};'
        f'animation-duration:{rnd.uniform(3.2, 5.6):.1f}s;animation-delay:-{rnd.uniform(0, 5):.1f}s"></span>'
        for _ in range(40)
    )
    chauves = "".join(
        f'<span class="ciel-chauve" style="top:{haut}%;animation-duration:{duree}s;animation-delay:-{i * 6}s">🦇</span>'
        for i, (haut, duree) in enumerate(((14, 14), (30, 19), (8, 23)))
    )
    return (
        '<div class="acc-fond">'
        '<div class="acc-couche acc-jour"><div class="ciel-astre ciel-soleil"></div></div>'
        '<div class="acc-couche acc-nuit"><div class="ciel-astre ciel-lune"></div></div>'
        '<div class="acc-couche acc-loups"><div class="ciel-astre ciel-lune-sang"></div>' + chauves +
        '<div class="ciel-colline"></div><span class="ciel-loup">🐺</span></div>'
        '<div class="acc-couche acc-victoire"><div class="ciel-rayons"></div>'
        '<div class="ciel-astre ciel-soleil-haut"></div>' + confettis + '</div>'
        '</div>'
    )


def aller_a(ecran):
    st.session_state.ecran = ecran
    st.rerun()


def ecran_accueil():
    st.markdown(CSS_SANS_SIDEBAR, unsafe_allow_html=True)
    with st.container(key="scene_accueil"):
        st.markdown(_fond_accueil(), unsafe_allow_html=True)
        st.markdown(
            '<div class="acc-titre-bloc"><div class="acc-surtitre">🐺</div>'
            '<div class="acc-titre">Projet Gévaudan</div>'
            '<div class="acc-sous">Un loup-garou grandeur nature, mené par une application</div></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="accueil_boutons", horizontal=True, horizontal_alignment="center"):
            if st.button("🐺 Nouvelle partie", key="accueil_btn_nouvelle", type="primary"):
                aller_a("installation")
            if st.button("📜 Historique", key="accueil_btn_historique"):
                aller_a("historique")


def lister_historique():
    """Parties archivées, de la plus récente à la plus ancienne (les fichiers illisibles sont ignorés)."""
    parties = []
    for fichier in sorted(glob.glob(os.path.join(HISTORIQUE_DIR, "partie_*.json")), reverse=True):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                p = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(p, dict) and {"issue", "joueurs", "journal"} <= p.keys():
            parties.append(p)
    return parties


def _date_partie(p):
    try:
        return datetime.fromisoformat(p["date"]).strftime("%d/%m/%Y à %H:%M")
    except (KeyError, ValueError):
        return "date inconnue"


def ecran_historique():
    st.markdown(CSS_SANS_SIDEBAR, unsafe_allow_html=True)
    if st.button("← Menu", key="retour_menu_historique"):
        aller_a("accueil")
    scene_ciel("nuit", "Historique des parties", "Les parties terminées, de la plus récente à la plus ancienne")

    parties = lister_historique()
    if not parties:
        st.info("Aucune partie terminée pour l'instant. Les parties abandonnées ne sont pas conservées.")
        return

    village = sum(p["issue"].startswith("Le village a gagné") for p in parties)
    loups = sum(p["issue"].startswith("Les loups ont gagné") for p in parties)
    st.caption(f"{len(parties)} parties · 🏡 {village} victoires du village · 🐺 {loups} victoires des loups")
    for p in parties:
        icone = "🏡" if p["issue"].startswith("Le village a gagné") else "🐺" if p["issue"].startswith("Les loups ont gagné") else "🏁"
        with st.expander(f"{icone} {_date_partie(p)} · {p['issue']}"):
            st.markdown(f"**{len(p['joueurs'])} joueurs**")
            afficher_roles(p["joueurs"])
            st.markdown("**📜 Journal**")
            afficher_historique(p)


# --------------------------------------------------------------------------
# Point d'entrée
# --------------------------------------------------------------------------

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


def main():
    st.set_page_config(page_title="Loup-Garou", page_icon="🐺", layout="wide", initial_sidebar_state="expanded")
    css_cartes()
    st.markdown(CSS_SCENES, unsafe_allow_html=True)
    st.markdown(CSS_PASSAGE, unsafe_allow_html=True)
    st.markdown(CSS_ACCUEIL, unsafe_allow_html=True)
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
            else:
                ecran_accueil()
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

    with st.sidebar:
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


main()
