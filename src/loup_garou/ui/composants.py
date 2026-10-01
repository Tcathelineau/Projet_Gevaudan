"""Briques d'interface réutilisables (cartes, bandeaux, dalles de sélection...)."""

import html
import random

import streamlit as st

from loup_garou.moteur.journal import etapes_chronologie
from loup_garou.moteur.partie import fin_de_tour
from loup_garou.roles import ROLES


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


def badge_amour(autres):
    label = "En couple avec" if len(autres) == 1 else "En trouple avec"
    st.markdown(
        f"""
        <div class="badge-amour">
            <span class="badge-icone">💘</span>
            <div>
                <div class="badge-label">{label}</div>
                <div class="badge-nom">{" & ".join(autres)}</div>
                <div class="badge-sous">Si l'un meurt, {"l'autre le suit" if len(autres) == 1 else "les autres le suivent"}.</div>
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
    # Plus il y a de choix, plus on élargit la grille : elle reste sur 3 lignes (7 colonnes au plus).
    n_col = 2 if len(choix) <= 4 else min(7, max(3, -(-len(choix) // 3)))
    clic = None
    dense = "_dense" if n_col >= 6 else ""
    with st.container(key=f"dalles_{theme}_{cle}{dense}"):
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


def panneau_avis(titre, sous, papiers):
    """Panneau d'affichage du village : planche de bois portant des avis punaisés."""
    st.markdown(
        '<div class="avis"><div class="avis-poteau avis-poteau-g"></div><div class="avis-poteau avis-poteau-d"></div>'
        f'<div class="avis-planche"><div class="avis-titre">{titre}</div>'
        f'<div class="avis-sous">{sous}</div><div class="avis-papiers">{"".join(papiers)}</div></div></div>',
        unsafe_allow_html=True,
    )


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
