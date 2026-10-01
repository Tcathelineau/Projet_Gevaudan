"""Feuilles de style et décors SVG injectés dans la page."""

from urllib.parse import quote

import streamlit as st

from loup_garou.roles import ROLES


def css_cartes():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=EB+Garamond:ital@0;1&display=swap');

        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        /* Les blocs <style> seuls et l'iframe utilitaire occupent chacun un interstice de 1rem en haut de page. */
        div[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] > style):not(:has(> [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] > :not(style))) {
            display: none;
        }
        div[data-testid="stElementContainer"]:has(> iframe[data-testid="stIFrame"]) {
            position: absolute; width: 1px; height: 1px; pointer-events: none;
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
        .jauge { margin: 0.45rem 0 0.2rem; font-family: 'EB Garamond', serif; color: #ece3d2; }
        .jauge-entete { display: flex; justify-content: space-between; align-items: baseline; font-size: 0.92rem; }
        .jauge-valeur { color: #f0d890; font-weight: 600; }
        .jauge-piste {
            position: relative;
            height: 8px;
            margin: 0.3rem 0 0.15rem;
            border-radius: 4px;
            background: linear-gradient(90deg, #7a2a2e, #4a4637 50%, #3f7d4f);
        }
        .jauge-piste-simple { background: rgba(236,227,210,.15); }
        .jauge-piste-simple > .jauge-rempli { position: absolute; inset: 0 auto 0 0; border-radius: 4px; background: #c9a44c; }
        .jauge-repere {
            position: absolute;
            top: -4px;
            width: 4px;
            height: 16px;
            margin-left: -2px;
            border-radius: 2px;
            background: #f2e9d8;
            box-shadow: 0 0 6px rgba(0,0,0,.6);
        }
        .jauge-extremites { display: flex; justify-content: space-between; font-size: 0.72rem; color: #b9b09c; }
        .apercu-grille { display: grid; grid-template-columns: 2fr 3fr; gap: 0.6rem; align-items: stretch; }
        .apercu-grille .panneau-dense { margin-bottom: 0; }
        .pictogramme {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.35rem;
            margin: 0.6rem 0 1.6rem 0;
            padding-bottom: 0.6rem;
        }
        .icone-role {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: 2px solid #c9a44c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
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
        div[class*="st-key-dalles_"][class*="_dense"] button {
            font-size: 0.72rem;
            padding: 0.45rem 0.1rem;
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
        div[class*="st-key-dalles_poison_"] button {
            background: rgba(60,110,40,.28);
            border-color: rgba(140,210,90,.55);
        }
        div[class*="st-key-dalles_poison_"] button:hover {
            background: rgba(70,140,40,.5);
            border-color: #9be05a;
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(155,224,90,.4);
        }
        div[class*="st-key-dalles_poison_"] button::after { content: "☠️"; }
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
.avis-papier-loup { border-left-color: #5e8c55; }
.avis-papier-secret { border-left-color: #c9a44c; }
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
div[class*="st-key-scene_passage"] .passage-sous {
    text-align: center; margin: -0.6rem 0 0.4rem; color: #f3ead8;
    font-family: 'EB Garamond', serif; font-style: italic; font-size: 1.15rem;
    text-shadow: 0 1px 10px rgba(0,0,0,.85);
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
    max-width: 1300px;
    min-height: 780px;
    margin: 0.4rem auto 1rem;
    padding: 3rem 2rem 190px;
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
    animation: acc-fondu 24s linear infinite, acc-nuages 90s linear infinite;
}
.acc-jour { opacity: 1;
    background-image: __N_JOUR__, linear-gradient(180deg, #34346f 0%, #b5638f 40%, #f2a468 72%, #ffe3a0 100%); }
.acc-nuit { animation-delay: -18s, 0s;
    background-image: __N_NUIT__, linear-gradient(180deg, #060a22 0%, #131c4a 55%, #2b3072 100%); }
.acc-loups { animation-delay: -12s, 0s;
    background-image: __N_LOUPS__, linear-gradient(180deg, #12030a 0%, #4a0d1c 52%, #a3302f 100%); }
.acc-victoire { animation-delay: -6s, 0s;
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
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 170px; pointer-events: none;
    background-repeat: repeat-x; background-position: left bottom; background-size: 1308px 175px;
}
.acc-jour::after { background-image: __V_JOUR__; }
.acc-nuit::after { background-image: __V_NUIT__; }
.acc-loups::after { background-image: __V_LOUPS__; right: auto; width: 62%; }
.acc-victoire::after { background-image: __V_VICT__; }
.acc-couche .ciel-soleil { left: 20%; bottom: 150px; }
.acc-couche .ciel-lune { width: 110px; height: 110px; right: 12%; top: 70px; }
.acc-couche .ciel-lune-sang { width: 190px; height: 190px; right: 12%; top: 60px; }
.acc-couche .ciel-colline { bottom: -90px; height: 190px; }
.acc-couche .ciel-loup { right: 14%; bottom: 120px; font-size: 110px; }
.acc-couche .ciel-rayons, .acc-couche .ciel-soleil-haut { left: 80%; }
.acc-couche .ciel-confetti { animation-name: acc-chute; }
.acc-titre-bloc { text-align: center; }
.acc-surtitre { font-size: 4.4rem; line-height: 1; filter: drop-shadow(0 3px 10px rgba(0,0,0,.6)); }
.acc-titre {
    font-family: 'Cinzel', serif; font-weight: 700; text-transform: uppercase;
    font-size: clamp(2.4rem, 7vw, 5rem); letter-spacing: .08em; color: #fff4d0;
    text-shadow: 0 3px 18px rgba(0,0,0,.75), 0 0 34px rgba(255,220,130,.35);
}
div[class*="st-key-accueil_boutons"] { width: min(380px, 100%); margin: 0 auto; gap: 1rem; }
div[class*="st-key-accueil_btn_"] { width: 100%; }
div[class*="st-key-accueil_btn_"] button {
    width: 100%; padding: 1rem 1.8rem;
    box-shadow: 0 4px 14px rgba(0,0,0,.5);
}
div[class*="st-key-accueil_btn_"] button p {
    font-family: 'Cinzel', serif; font-size: 1.4rem; font-weight: 600; letter-spacing: .06em;
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
    100% { transform: translateY(800px) rotate(540deg); opacity: 1; }
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


CSS_HISTORIQUE = """
<style>
.jrn-bloc {
    --c: #7f8ce0; margin: 0 0 .8rem; border-radius: 10px; overflow: hidden;
    border: 1.5px solid var(--c); background: color-mix(in srgb, var(--c) 9%, transparent);
}
.jrn-nuit { --c: #7f8ce0; }
.jrn-jour { --c: #e0a94a; }
.jrn-fin { --c: #c9a44c; }
.jrn-tete {
    padding: .45rem .9rem; font-family: 'Cinzel', serif; font-weight: 700; letter-spacing: .05em;
    text-transform: uppercase; font-size: .95rem; color: #fff4d0;
    background: color-mix(in srgb, var(--c) 32%, transparent);
    border-bottom: 1.5px solid var(--c);
}
.jrn-tete small { font-family: inherit; font-weight: 400; opacity: .8; text-transform: none; letter-spacing: 0; }
.jrn-ligne { display: flex; gap: .6rem; padding: .35rem .9rem; align-items: baseline; }
.jrn-ligne + .jrn-ligne { border-top: 1px solid color-mix(in srgb, var(--c) 28%, transparent); }
.jrn-ligne > span:first-child { flex: 0 0 1.6rem; text-align: center; }
div[class*="st-key-histo_"] {
    --c: #8a8a9a; border: 2px solid var(--c) !important; border-radius: 12px;
    background: color-mix(in srgb, var(--c) 8%, transparent);
    box-shadow: 0 0 14px color-mix(in srgb, var(--c) 22%, transparent);
}
div[class*="st-key-histo_village_"] { --c: #4caf6a; }
div[class*="st-key-histo_loups_"] { --c: #d64545; }
div[class*="st-key-histo_loupblanc_"] { --c: #eceaf4; }
div[class*="st-key-histo_couple_"] { --c: #f06fb5; }
.hc-tete { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem; margin-bottom: .6rem; }
.hc-gagnant {
    padding: .2rem .8rem; border-radius: 999px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
    font-size: .85rem; color: #10121c; background: var(--c);
}
.hc-date { opacity: .8; font-size: .95rem; }
.hc-ligne { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; margin: .3rem 0; }
.hc-label { flex: 0 0 5.2rem; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; opacity: .6; }
.hc-puce {
    padding: .1rem .65rem; border-radius: 6px; font-size: .9rem;
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16);
}
</style>
"""


def css_infobulles():
    """Infobulle au survol de chaque rôle de l'écran de composition (conteneurs `info_<rôle>`)."""
    regles = "".join(
        f'div[class*="st-key-info_{cle}"]:hover::after {{ content: "{role.description.replace(chr(34), chr(39))}"; }}\n'
        for cle, role in ROLES.items()
    )
    return f"""
        <style>
        div[class*="st-key-info_"] {{ position: relative; }}
        div[class*="st-key-info_"]:hover::after {{
            position: absolute;
            top: 100%;
            left: 0;
            z-index: 1000;
            width: min(280px, 80vw);
            padding: 0.55rem 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(201,164,76,.6);
            background: #1b150d;
            box-shadow: 0 6px 18px rgba(0,0,0,.55);
            font-family: 'EB Garamond', serif;
            font-size: 0.95rem;
            line-height: 1.3;
            color: #f2e9d8;
            pointer-events: none;
        }}
        {regles}
        </style>
    """
