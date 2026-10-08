"""Briques d'interface réutilisables (cartes, bandeaux, dalles de sélection...)."""

import html
import random

import streamlit as st

from loup_garou.moteur.partie import fin_de_tour
from loup_garou.roles import ROLES
from loup_garou.ui.illustrations import svg_role


def carte_role(nom, role):
    """Carte du rôle, retournée à son apparition : le dos (loup) se retourne pour révéler la face."""
    r = ROLES[role]
    st.markdown(
        f"""
        <div class="carte-scene"><div class="carte-retournee">
            <div class="carte-dos">{svg_role("loup", "dos-art", "🐺")}</div>
            <div class="carte" style="background: {r.degrade};">
                <span class="coin-bd"></span><span class="coin-bg"></span>
                <div class="carte-titre">{r.nom}</div>
                <div class="carte-medaillon">{svg_role(role, "carte-art", r.emoji)}</div>
                <div class="carte-nom">{nom}</div>
            </div>
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def carte_dos():
    st.markdown(f'<div class="carte-dos">{svg_role("loup", "dos-art", "🐺")}</div>', unsafe_allow_html=True)


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


def fenetre_couple(autres):
    """Fenêtre qui s'ouvre la première fois qu'un joueur découvre qu'il est amoureux."""
    en_trouple = len(autres) > 1
    titre = "💘 Vous êtes en trouple !" if en_trouple else "💘 Vous êtes en couple !"

    def contenu():
        suite = "les autres le suivent" if en_trouple else "l'autre le suit"
        st.markdown(
            '<div class="dialogue-couple"><div class="dc-coeurs">💗 💘 💗</div>'
            "<div class=\"dc-lien\">Tu es lié par l'amour à</div>"
            f'<div class="dc-noms">{html.escape(" et ".join(autres))}</div>'
            f'<div class="dc-texte">Si l\'un de vous meurt, {suite} dans la tombe.<br>'
            'Gardez le secret, ou pas : à vous de jouer.</div></div>',
            unsafe_allow_html=True,
        )
        # Un bouton dans une fenêtre ne relance que la fenêtre : il faut relancer la page pour la fermer.
        if st.button("Compris", type="primary", key="fermer_couple", use_container_width=True):
            st.rerun()

    st.dialog(titre)(contenu)()


def fenetre_meute(complices):
    """Fenêtre qui s'ouvre la première fois qu'un joueur découvre qu'il est loup."""
    seul = not complices

    def contenu():
        if seul:
            lien, noms, texte = "Aucun autre loup en vie", "Tu chasses seul", "Chaque nuit, tu désignes seul la victime.<br>Garde ton secret."
        else:
            lien, noms = "Tu chasses avec", " et ".join(complices)
            texte = "Chaque nuit, vous désignez ensemble une victime.<br>Gardez le secret : le village ne doit rien savoir."
        st.markdown(
            '<div class="dialogue-meute"><div class="dm-loup">🐺 🌕 🐺</div>'
            f'<div class="dm-lien">{lien}</div>'
            f'<div class="dm-noms">{html.escape(noms)}</div>'
            f'<div class="dm-texte">{texte}</div></div>',
            unsafe_allow_html=True,
        )
        # Un bouton dans une fenêtre ne relance que la fenêtre : il faut relancer la page pour la fermer.
        if st.button("Compris", type="primary", key="fermer_meute", use_container_width=True):
            st.rerun()

    st.dialog("🐺 Tu es le dernier loup !" if seul else "🐺 Vous êtes la meute !")(contenu)()


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


# Silhouettes portées par le vent (de gauche à droite, comme les nuages) : moitié chauves-souris, moitié feuilles.
SILHOUETTES_VENT = (("chauve", "🦇", 14, 14), ("feuille", "🍂", 22, 17), ("chauve", "🦇", 30, 19), ("feuille", "🍃", 8, 23))


def silhouettes_vent():
    return "".join(
        f'<span class="ciel-{genre}" style="top:{haut}%;animation-duration:{duree}s;animation-delay:-{i * 6}s">{emoji}</span>'
        for i, (genre, emoji, haut, duree) in enumerate(SILHOUETTES_VENT)
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
        elements.append(silhouettes_vent())
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
        elements.append('<div class="ciel-colline"></div>')
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
        f'<div class="{classe}"><span class="plaquette-icone">{icone}</span><span class="plaquette-texte">{texte}</span>'
        f'<span class="plaquette-icone">{icone}</span></div>',
        unsafe_allow_html=True,
    )


def grille_dalles(theme, cle, choix, selection=(), rappel=None):
    """Dalles cliquables (style selon `theme`, cf. CSS). Renvoie le nom cliqué ou None.
    Les noms de `selection` sont affichés en surbrillance. Avec `rappel(nom)`, le clic est traité par ce rappel
    (avant la relance du script), ce qui permet de ne relancer qu'un fragment."""
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
                    on_click=rappel, args=(nom,) if rappel else None,
                ):
                    clic = nom
    return clic


def _basculer(cle_sel, choix, k, nom):
    sel = [n for n in st.session_state.get(cle_sel, []) if n in choix]
    st.session_state[cle_sel] = [n for n in sel if n != nom] if nom in sel else (sel + [nom])[-k:]


@st.fragment
def _zone_selection(theme, cle, choix, k, libelle, libelle_vide, cle_bouton):
    cle_sel = f"sel_{theme}_{cle}"
    sel = [n for n in st.session_state.get(cle_sel, []) if n in choix]
    grille_dalles(theme, cle, choix, selection=sel, rappel=lambda nom: _basculer(cle_sel, choix, k, nom))
    if bouton_validation(
        libelle.format(sel=" et ".join(sel)) if sel else libelle_vide, cle_bouton, disabled=len(sel) != k,
    ):
        st.session_state.pop(cle_sel, None)
        st.session_state[f"valide_{cle_bouton}"] = sel
        st.rerun()  # relance toute la page, pour passer à la suite


def selection_et_validation(theme, cle, choix, k, libelle, libelle_vide, cle_bouton):
    """Dalles où l'on en sélectionne `k` (re-cliquer désélectionne), puis un bouton de validation.

    Renvoie la sélection validée, ou None. Les clics sur les dalles ne relancent que ce fragment : la page
    ne clignote pas. `libelle` peut contenir `{sel}` (les noms choisis), `libelle_vide` sert tant que rien n'est choisi."""
    valide = st.session_state.pop(f"valide_{cle_bouton}", None)
    if valide is not None:
        return valide
    _zone_selection(theme, cle, choix, k, libelle, libelle_vide, cle_bouton)
    return None


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
