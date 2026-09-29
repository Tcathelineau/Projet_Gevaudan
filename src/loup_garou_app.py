"""
Loup-Garou — version Streamlit (jeu en hotseat : on se passe l'écran).

Lancement :  streamlit run loup_garou_app.py
"""

import json
import os
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Optional

import streamlit as st

SAVE_FILE = "save.json"
MUSIQUE_FILE = "musique.mp3"

PHASE_EMOJI = {
    "nuit": "🌙",
    "reveil": "🌅",
    "election_maire": "👑",
    "conseil": "🗳️",
    "fin": "🏁",
}

PHASE_LABEL = {
    "nuit": "Nuit",
    "reveil": "Réveil",
    "election_maire": "Élection du maire",
    "conseil": "Conseil",
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
        .pictogramme {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin: 1rem 0 1.5rem 0;
        }
        .icone-role {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 2px solid #c9a44c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
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
        div[class*="st-key-voygrid_"] {
            max-width: min(360px, 70vw);
            margin: 0 auto;
        }
        div[class*="st-key-voypick_"] button {
            position: relative;
            background: rgba(28,43,92,.35);
            border: 2px solid rgba(201,164,76,.45);
            border-radius: 10px;
            color: #ece3d2;
            font-family: 'Cinzel', serif;
            font-size: 0.95rem;
            padding: 0.9rem 1.1rem;
            transition: all .18s ease;
        }
        div[class*="st-key-voypick_"] button:hover {
            background: rgba(28,43,92,.8);
            border-color: #c9a44c;
            color: #ffffff;
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 16px rgba(201,164,76,.4);
        }
        div[class*="st-key-voypick_"] button::after {
            content: "👁";
            display: block;
            opacity: 0;
            font-size: 1.2rem;
            margin-top: 0.3rem;
            transition: opacity .18s ease;
        }
        div[class*="st-key-voypick_"] button:hover::after {
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


def plaquette(texte, icone="🌙", ton="neutre"):
    classe = "plaquette" if ton == "neutre" else f"plaquette plaquette-{ton}"
    st.markdown(
        f'<div class="{classe}"><span class="plaquette-icone">{icone}</span><span class="plaquette-texte">{texte}</span></div>',
        unsafe_allow_html=True,
    )


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

def _nuit_loup(s, nom, cle):
    complices = [l for l in s["loups"] if l != nom and s["joueurs"][l]["vivant"]]
    badge_meute(nom, complices)
    if s["jour"] == 0:
        plaquette("Première nuit : vous vous découvrez, personne ne meurt encore.", icone="🐾")
        bouton_fin(s, cle)
    else:
        cibles = [n for n in vivants(s) if ROLES[s["joueurs"][n]["role"]].camp != "loups"]
        cible = st.radio("Qui dévorez-vous ?", cibles, key=f"loup_{cle}")
        if st.button("Confirmer la victime", type="primary", key=f"ok_loup_{cle}"):
            s["votes_loups"].append(cible)
            fin_de_tour(s)
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
        with st.container(key=f"voygrid_{cle}"):
            cols = st.columns(2)
            for i, candidat in enumerate(candidats):
                with cols[i % 2]:
                    if st.button(candidat, key=f"voypick_{cle}_{candidat}", use_container_width=True):
                        st.session_state[f"vu_{cle}"] = candidat
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
                for n in couple:
                    s["joueurs"][n]["amoureux"] = True
                fin_de_tour(s)
                st.rerun()


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
        "journal": [],
        "maire": None,
        "dernier_maire": None,
    }
    for role in ROLES.values():
        etat.update(role.etat_initial)
    return etat


def vivants(s):
    return [n for n, d in s["joueurs"].items() if d["vivant"]]


def tuer(s, nom):
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
    return morts


def vainqueur(s):
    en_vie = vivants(s)
    loups = [n for n in en_vie if ROLES[s["joueurs"][n]["role"]].camp == "loups"]
    autres = [n for n in en_vie if ROLES[s["joueurs"][n]["role"]].camp != "loups"]

    if len(en_vie) == 2 and all(s["joueurs"][n]["amoureux"] for n in en_vie):
        return "Les amoureux l'emportent : ils sont les deux derniers survivants."
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
        n = 1 if (role.unique and reste >= 1) else 0
        speciaux[role.key] = n
        reste -= n
    return loups, speciaux


def ecran_installation():
    st.title("🐺 Loup-Garou")
    st.caption("Configure la partie, puis ajoute les joueurs.")

    if "config_etape" not in st.session_state:
        st.session_state.config_etape = "roles"

    if st.session_state.config_etape == "roles":
        etape_roles()
    else:
        etape_noms()


def afficher_composition(nb, composition, n_villageois):
    lignes = "".join(
        f'<div class="panneau-ligne"><span>{ROLES[cle].emoji} {ROLES[cle].nom}</span><span>{n}</span></div>'
        for cle, n in composition.items()
    )
    st.markdown(
        f"""
        <div class="panneau">
            <div class="panneau-titre">Composition</div>
            {lignes}
            <div class="panneau-ligne"><span><b>Total</b></span><span><b>{nb} / {nb}</b></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if n_villageois < 0:
        st.error(
            f"Trop de rôles spéciaux pour {nb} joueurs "
            f"(il en manque {-n_villageois}) : réduis-en un ou augmente le nombre de joueurs."
        )
        return

    icones = "".join(
        f'<div class="icone-role" style="background: {ROLES[cle].degrade};" title="{ROLES[cle].nom}">{ROLES[cle].emoji}</div>'
        for cle, n in composition.items()
        for _ in range(n)
    )
    st.markdown(f'<div class="pictogramme">{icones}</div>', unsafe_allow_html=True)


def etape_roles():
    st.subheader("1. Composition de la partie")

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
    # grille — beaucoup plus compact qu'un réglage numérique par rôle, et ça
    # tient à l'échelle si d'autres rôles uniques s'ajoutent un jour.
    st.markdown("**Autres rôles**")
    st.caption("Coche les rôles spéciaux présents. Le reste de la table devient Villageois.")

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

    n_villageois = nb - sum(composition.values())
    composition["villageois"] = max(n_villageois, 0)

    with apercu.container():
        afficher_composition(nb, composition, n_villageois)

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
        s["ordre_nuit"] = vivants(s)
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

    with st.container(height=250, border=False):
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
        if comptes and not (len(comptes) > 1 and comptes[0][1] == comptes[1][1]):
            victime = comptes[0][0]
        if s["soin_sorciere"]:
            victime = None
        if victime:
            morts = tuer(s, victime)

    s["morts_nuit"] = morts
    s["votes_loups"] = []
    s["soin_sorciere"] = False
    s["ordre_nuit"] = []
    s["tour"] = 0
    s["devoile"] = False
    s["phase"] = "reveil"


def ecran_reveil(s):
    st.title(f"☀️ Réveil — jour {s['jour']}")
    if s["morts_nuit"]:
        for mort in s["morts_nuit"]:
            role = s["joueurs"][mort]["role"]
            texte = "était LOUP-GAROU" if ROLES[role].camp == "loups" else "n'était pas loup-garou"
            st.error(f"{mort} est mort. Il {texte}.")
        if len(s["morts_nuit"]) > 1:
            st.caption("Les amoureux sont morts ensemble.")
    else:
        st.success("Personne n'est mort cette nuit.")

    gagnant = vainqueur(s)
    if gagnant:
        if st.button("Voir le résultat", type="primary"):
            s["phase"] = "fin"
            s["message_fin"] = gagnant
            st.rerun()
        return

    texte = "Passer au premier conseil" if s["jour"] == 0 else "Ouvrir le conseil du village"
    if st.button(texte, type="primary"):
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
            role = s["joueurs"][mort]["role"]
            if ROLES[role].camp == "loups":
                st.success(f"{mort} était LOUP-GAROU.")
            else:
                st.error(f"{mort} n'était PAS loup-garou.")

        gagnant = vainqueur(s)
        if gagnant:
            if st.button("Voir le résultat", type="primary"):
                s["phase"] = "fin"
                s["message_fin"] = gagnant
                st.rerun()
        elif st.button("La nuit tombe", type="primary"):
            s["jour"] += 1
            s["phase"] = "nuit"
            st.rerun()

    else:
        st.caption("Débattez à voix haute, puis le capitaine saisit le résultat du vote.")
        condamne = st.radio("Le village élimine", en_vie, key=f"vote_{s['jour']}")
        if st.button("Valider le vote", type="primary"):
            st.session_state[f"resultat_{s['jour']}"] = tuer(s, condamne)
            st.rerun()


def ecran_fin(s):
    st.title("🏁 Fin de la partie")
    st.header(s["message_fin"])
    st.subheader("Les rôles")
    for nom, d in s["joueurs"].items():
        etat = "en vie" if d["vivant"] else "mort"
        coeur = " 💘" if d["amoureux"] else ""
        st.write(f"{ROLES[d['role']].emoji} **{nom}** — {d['role']} ({etat}){coeur}")


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
        loups_vivants = sum(
            1 for n in vivants(s) if ROLES[s["joueurs"][n]["role"]].camp == "loups"
        )
        village_vivants = len(vivants(s)) - loups_vivants
        maire_txt = s.get("maire") or "— (pas encore élu)"

        st.markdown(
            f"""
            <div class="panneau">
                <div class="panneau-titre">{PHASE_EMOJI.get(s['phase'], '')} Jour {s['jour']} — {PHASE_LABEL.get(s['phase'], s['phase'])}</div>
                <div class="panneau-ligne"><span>👥 Vivants</span><span>{len(vivants(s))} / {s['nb_joueurs']}</span></div>
                <div class="panneau-ligne"><span>🐺 Loups</span><span>{loups_vivants}</span></div>
                <div class="panneau-ligne"><span>🧑‍🌾 Village</span><span>{village_vivants}</span></div>
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
    else:
        ecran_fin(s)

    with st.sidebar:
        if os.path.exists(MUSIQUE_FILE):
            if st.checkbox("🎵 Musique de fond", value=True, key="musique_on"):
                st.audio(MUSIQUE_FILE, format="audio/mp3", loop=True, autoplay=True)

        if st.button("🚪 Abandonner la partie", key="abandon"):
            clear_save()
            st.session_state.clear()
            st.rerun()

    save_game(s)


main()
