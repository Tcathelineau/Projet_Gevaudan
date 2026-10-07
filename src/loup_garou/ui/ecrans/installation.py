"""Configuration d'une nouvelle partie en quatre étapes : table, rôles, options, joueurs."""

from types import SimpleNamespace

import streamlit as st

from loup_garou.equilibre import (
    MAX_CHAOS, MAX_INFO, bilan, niveau_chaos, niveau_info, position_equilibre, remplissage,
)
from loup_garou.moteur.partie import composition_recommandee, nouvelle_partie
from loup_garou.moteur.persistance import load_joueurs, load_preferences, maj_preferences, save_joueurs
from loup_garou.options import CADENCES, OPTIONS_DEFAUT
from loup_garou.roles import CATEGORIES, ROLES, ROLES_SPECIAUX
from loup_garou.ui.illustrations import svg_role
from loup_garou.ui.styles import css_infobulles

ETAPES = (("table", "Table"), ("roles", "Rôles"), ("options", "Options"), ("noms", "Joueurs"))
CLES_ROLES = [f"n_{role.key}" for role in ROLES_SPECIAUX]
CLES_OPTIONS = (
    "opt_potions", "opt_potions_mort", "opt_voyante", "opt_loup_blanc", "opt_couple_hasard", "opt_trouple", "opt_maire",
)
# Réglage de la composition (clé de session) <-> option de partie.
OPTIONS_SESSION = {
    "opt_potions": "potions_sorciere", "opt_potions_mort": "potions_mort", "opt_voyante": "cadence_voyante",
    "opt_loup_blanc": "cadence_loup_blanc", "opt_couple_hasard": "couple_hasard", "opt_trouple": "trouple",
    "opt_maire": "maire_depart",
}


def _aller(etape):
    st.session_state.config_etape = etape


def _vers_accueil():
    st.session_state.ecran = "accueil"


def _conserver():
    """Un widget qui n'est pas affiché perd son état : on le réaffecte pour qu'il survive aux changements d'étape."""
    for cle in ("nb_joueurs_setup", "n_loup", *CLES_ROLES, *CLES_OPTIONS):
        if cle in st.session_state:
            st.session_state[cle] = st.session_state[cle]


def _charger_composition_precedente():
    """Prérègle la table avec la dernière composition jouée (une seule fois, à l'entrée dans l'assistant)."""
    prec = load_preferences().get("composition", {})
    if "nb" in prec:
        st.session_state.setdefault("nb_joueurs_setup", prec["nb"])
    if "n_loup" in prec:
        st.session_state.setdefault("n_loup", prec["n_loup"])
    for cle, valeur in prec.get("roles", {}).items():
        st.session_state.setdefault(f"n_{cle}", bool(valeur))
    for cle, valeur in prec.get("options", {}).items():
        if cle in CLES_OPTIONS:
            st.session_state.setdefault(cle, valeur)


def composition_courante():
    """Composition lue dans les réglages de la session : joueurs, paquet, options, cartes, villageois restants."""
    nb = int(min(max(st.session_state.get("nb_joueurs_setup", 7), 5), 18))
    loups_defaut, speciaux_defaut = composition_recommandee(nb)
    n_loup = int(min(max(st.session_state.get("n_loup", min(loups_defaut, max(1, nb - 1))), 1), max(1, nb - 1)))
    composition = {"loup": n_loup}
    for role in ROLES_SPECIAUX:
        reglage = st.session_state.get(f"n_{role.key}", speciaux_defaut[role.key] if not role.unique else bool(speciaux_defaut[role.key]))
        composition[role.key] = role.lot * int(bool(reglage)) if role.unique else int(reglage)
    total = nb + sum(ROLES[cle].cartes_en_plus * n for cle, n in composition.items())
    n_villageois = total - sum(composition.values())
    composition["villageois"] = max(n_villageois, 0)
    options = dict(OPTIONS_DEFAUT)
    for cle, nom in OPTIONS_SESSION.items():
        options[nom] = st.session_state.get(cle, OPTIONS_DEFAUT[nom])
    if options["couple_hasard"] and composition.get("cupidon"):
        composition["villageois"] += composition["cupidon"]
        composition["cupidon"] = 0
    return SimpleNamespace(nb=nb, composition=composition, options=options, total=total, n_villageois=n_villageois)


def ecran_installation():
    with st.container(horizontal=True, vertical_alignment="center"):
        st.button("← Menu", key="retour_menu_installation", on_click=_vers_accueil)
        st.markdown("#### 🐺 Loup-Garou")

    if "config_etape" not in st.session_state:
        _charger_composition_precedente()
        st.session_state.config_etape = "table"
    _conserver()
    etape = st.session_state.config_etape
    _progression(etape)

    cfg = composition_courante()
    if etape == "table":
        etape_table(cfg)
    elif etape == "roles":
        etape_roles(cfg)
    elif etape == "options":
        etape_options(cfg)
    else:
        etape_noms(cfg)
        return
    _barre_fixe(etape, cfg)


def _progression(etape):
    index = [cle for cle, _ in ETAPES].index(etape)
    pastilles = "".join(
        f'<span class="etape{" etape-faite" if i < index else " etape-actuelle" if i == index else ""}">'
        f'<b>{i + 1}</b> {libelle}</span>'
        for i, (_, libelle) in enumerate(ETAPES)
    )
    st.markdown(f'<div class="etapes" role="list" aria-label="Étapes">{pastilles}</div>', unsafe_allow_html=True)


def _barre_fixe(etape, cfg):
    """Bandeau fixe en bas de l'écran : retour, équilibre du moment, étape suivante."""
    index = [cle for cle, _ in ETAPES].index(etape)
    precedent = ETAPES[index - 1][0] if index else None
    suivant = ETAPES[index + 1]
    b = bilan(cfg.composition, cfg.nb, cfg.options)
    village = round(position_equilibre(b))
    with st.container(key="barre_fixe", horizontal=True, horizontal_alignment="center", vertical_alignment="center"):
        if precedent:
            st.button("← Retour", key="etape_retour", on_click=_aller, args=(precedent,))
        else:
            st.button("← Menu", key="etape_menu", on_click=_vers_accueil)
        st.markdown(
            f'<div class="barre-equilibre"><span>🐺 {100 - village} %</span>'
            f'<div class="jauge-piste"><div class="jauge-repere" style="left: {position_equilibre(b):.1f}%;"></div></div>'
            f'<span>{village} % 🏡</span></div>',
            unsafe_allow_html=True,
        )
        st.button(
            f"{suivant[1]} →", key="etape_suivant", type="primary", on_click=_aller, args=(suivant[0],),
            disabled=cfg.n_villageois < 0,
        )


def afficher_composition(nb, total, composition, n_villageois, options):
    if n_villageois < 0:
        st.error(
            f"Trop de rôles spéciaux pour {total} cartes "
            f"(il en manque {-n_villageois}) : réduis-en un ou augmente le nombre de joueurs."
        )
        return

    st.markdown(f'<div class="apercu-centre">{jauges_html(bilan(composition, nb, options)).strip()}</div>', unsafe_allow_html=True)

    icones = "".join(
        f'<div class="icone-role" style="background: {ROLES[cle].degrade};" title="{ROLES[cle].nom}">{svg_role(cle, "icone-art", ROLES[cle].emoji)}</div>'
        for cle, n in composition.items()
        for _ in range(n)
    )
    st.markdown(f'<div class="pictogramme">{icones}</div>', unsafe_allow_html=True)
    if total > nb:
        st.caption(f"{total - nb} cartes restent au milieu de la table ({nb} joueurs, {total} cartes).")


def jauges_html(b):
    """Panneau d'équilibre : curseur loups / village, information et chaos."""

    def barre(titre, niveau, fraction):
        pct = 100 * fraction
        return (
            f'<div class="jauge"><div class="jauge-entete"><span>{titre}</span>'
            f'<span class="jauge-valeur">{niveau}</span></div>'
            f'<div class="jauge-piste jauge-piste-simple"><div class="jauge-rempli" style="width: {pct:.1f}%;"></div></div></div>'
        )

    return f"""
        <div class="panneau panneau-dense">
            <div class="panneau-titre">Équilibre de la partie</div>
            <div class="jauge">
                <div class="jauge-piste"><div class="jauge-repere" style="left: {position_equilibre(b):.1f}%;"></div></div>
                <div class="jauge-extremites"><span>🐺 Loups {100 - round(position_equilibre(b))} %</span><span>Village {round(position_equilibre(b))} % 🏡</span></div></div>
            {barre("🔮 Information", niveau_info(b), remplissage(b.info, b.joueurs, MAX_INFO))}
            {barre("🌀 Chaos", niveau_chaos(b), remplissage(b.chaos, b.joueurs, MAX_CHAOS))}
        </div>
    """


def _fixer(cle, valeur):
    st.session_state[cle] = valeur


def choix_segmente(titre, cle, choix, defaut, aide=None):
    """Choix parmi quelques valeurs, en boutons côte à côte (le réglage vit sous `cle`, hors widget)."""
    actuel = st.session_state.setdefault(cle, defaut)
    st.markdown(f'<div class="segment-titre">{titre}</div>', unsafe_allow_html=True)
    if aide:
        st.caption(aide)
    with st.container(key=f"segment_{cle}", horizontal=True):
        for valeur, libelle in choix.items():
            st.button(
                libelle, key=f"{cle}__{valeur}", type="primary" if valeur == actuel else "secondary",
                on_click=_fixer, args=(cle, valeur),
            )
    return actuel


def _pas(cle, sens, mini, maxi):
    st.session_state[cle] = min(max(st.session_state[cle] + sens, mini), maxi)


def compteur(titre, cle, mini, maxi, defaut, cle_titre=None):
    """Compteur centré : un « − » rond, la valeur, un « + » rond. Le réglage vit sous `cle` (hors widget).
    `cle_titre` : conteneur du seul titre, pour lui donner une infobulle sans en mettre sur les boutons."""
    valeur = int(min(max(st.session_state.get(cle, defaut), mini), maxi))
    st.session_state[cle] = valeur
    with st.container(key=cle_titre or f"titre_{cle}"):
        st.markdown(f'<div class="compteur-titre">{titre}</div>', unsafe_allow_html=True)
    with st.container(key=f"compteur_{cle}", horizontal=True, horizontal_alignment="center", vertical_alignment="center"):
        st.button("−", key=f"{cle}_moins", disabled=valeur <= mini, on_click=_pas, args=(cle, -1, mini, maxi))
        st.markdown(f'<div class="compteur-valeur" aria-live="polite">{valeur}</div>', unsafe_allow_html=True)
        st.button("+", key=f"{cle}_plus", disabled=valeur >= maxi, on_click=_pas, args=(cle, 1, mini, maxi))
    return valeur


def etape_table(cfg):
    st.markdown("##### Combien êtes-vous ?")
    with st.container(key="compteurs", horizontal=True, horizontal_alignment="center", gap="large"):
        with st.container(key="compteur_joueurs"):
            compteur("Nombre de joueurs", "nb_joueurs_setup", 5, 18, 7)
        loups_defaut, _ = composition_recommandee(cfg.nb)
        with st.container(key="compteur_loups"):
            compteur(
                f"{ROLES['loup'].emoji} {ROLES['loup'].nom}", "n_loup", 1, max(1, cfg.nb - 1),
                min(loups_defaut, max(1, cfg.nb - 1)), cle_titre="info_loup",
            )
    st.caption(
        f"{cfg.nb} joueurs, {cfg.composition['loup']} loup{'s' if cfg.composition['loup'] > 1 else ''} : "
        "l'étape suivante répartit les autres rôles."
    )
    st.markdown(css_infobulles(), unsafe_allow_html=True)
    st.markdown('<div class="espace-barre"></div>', unsafe_allow_html=True)


def etape_roles(cfg):
    st.markdown(css_infobulles(), unsafe_allow_html=True)
    with st.container(key="setup_roles"):
        afficher_composition(cfg.nb, cfg.total, cfg.composition, cfg.n_villageois, cfg.options)
        _, speciaux_defaut = composition_recommandee(cfg.nb)

        # Rôles uniques (au plus un exemplaire) : une simple case à cocher, rangée par catégorie
        # en grille de 4 colonnes ; le reste de la table devient Villageois.
        st.markdown("**Autres rôles** · coche ceux qui jouent")
        uniques = [role for role in ROLES_SPECIAUX if role.unique]
        for cle_categorie, (emoji, titre) in CATEGORIES.items():
            roles = [role for role in uniques if role.categorie == cle_categorie]
            if not roles:
                continue
            coches = sum(
                bool(st.session_state.get(f"n_{role.key}", bool(speciaux_defaut[role.key]))) for role in roles
            )
            st.markdown(
                f'<div class="cat-titre"><span>{emoji} {titre}</span>'
                f'<b>{coches} / {len(roles)}</b></div>',
                unsafe_allow_html=True,
            )
            for i in range(0, len(roles), 4):
                cols = st.columns(4)
                for col, role in zip(cols, roles[i:i + 4]):
                    # Couple tiré au sort : Cupidon devient villageois, on le dit au lieu de le faire en silence.
                    remplace = role.key == "cupidon" and bool(st.session_state.get("opt_couple_hasard"))
                    with col, st.container(key=f"info_{role.key}"):
                        st.checkbox(
                            f"{role.emoji} {role.nom}" + (f" ×{role.lot}" if role.lot > 1 else "")
                            + (" (devient villageois)" if remplace else ""),
                            value=bool(speciaux_defaut[role.key]), key=f"n_{role.key}", disabled=remplace,
                            help="Le couple est tiré au sort (option avancée) : Cupidon est remplacé par un villageois."
                            if remplace else None,
                        )

        # Rôles spéciaux en quantité libre (aucun aujourd'hui, mais le prochain
        # rôle de ce type n'aura besoin que d'une entrée dans ROLES).
        for role in ROLES_SPECIAUX:
            if not role.unique:
                with st.container(key=f"info_{role.key}"):
                    compteur(f"{role.emoji} {role.nom}", f"n_{role.key}", 0, cfg.nb, speciaux_defaut[role.key])
    st.markdown('<div class="espace-barre"></div>', unsafe_allow_html=True)


def etape_options(cfg):
    """Réglages de règles, limités aux rôles présents dans la partie."""
    afficher_composition(cfg.nb, cfg.total, cfg.composition, cfg.n_villageois, cfg.options)
    st.markdown("##### Réglages de la partie")
    comp = cfg.composition
    avec_option = False
    if comp.get("sorciere"):
        avec_option = True
        with st.container(key="compteurs_potions", horizontal=True, horizontal_alignment="center", gap="large"):
            with st.container(key="compteur_soin"):
                compteur("🧪 Potions de soin", "opt_potions", 1, 5, OPTIONS_DEFAUT["potions_sorciere"])
            with st.container(key="compteur_mort"):
                compteur("☠️ Potions de mort", "opt_potions_mort", 0, 5, OPTIONS_DEFAUT["potions_mort"])
    if comp.get("voyante"):
        avec_option = True
        choix_segmente("🔮 Visions de la voyante", "opt_voyante", CADENCES, OPTIONS_DEFAUT["cadence_voyante"])
    if comp.get("loup_blanc"):
        avec_option = True
        choix_segmente("🌕 Festins du Loup Blanc", "opt_loup_blanc", CADENCES, OPTIONS_DEFAUT["cadence_loup_blanc"])
    oui_non = {False: "Non", True: "Oui"}
    choix_segmente(
        "🎲 Couple tiré au sort, sans Cupidon", "opt_couple_hasard", oui_non, False,
        "Le couple est désigné au hasard dès le départ ; Cupidon est remplacé par un villageois.",
    )
    choix_segmente(
        "🎉 Mode fun : un trouple au lieu d'un couple", "opt_trouple", oui_non, False,
        "L'amour lie trois joueurs (choisis par Cupidon, ou tirés au sort). Si l'un meurt, les deux autres le suivent.",
    )
    choix_segmente(
        "👑 À égalité loups / village, le maire départage", "opt_maire", oui_non, True,
        "Oui : la partie continue à égalité, sauf si le maire est un loup. "
        "Non : les loups gagnent dès qu'ils sont aussi nombreux que les autres.",
    )
    if not avec_option:
        st.caption("Les réglages propres à un rôle (potions, cadences) apparaissent quand ce rôle est dans la partie.")
    st.markdown('<div class="espace-barre"></div>', unsafe_allow_html=True)


def etape_noms(cfg):
    nb = cfg.nb
    st.subheader("Qui joue ?")
    st.caption(f"{nb} joueurs — vous vous passerez l'appareil à tour de rôle pendant la nuit.")

    recents = load_joueurs()
    if recents:
        st.caption("Les noms de la dernière partie sont préremplis.")
    with st.form("noms"):
        noms = []
        cols = st.columns(2)
        for i in range(nb):
            with cols[i % 2]:
                noms.append(st.text_input(
                    f"Joueur {i + 1}", value=recents[i] if i < len(recents) else "", key=f"nom_{i}",
                ).strip())

        col_retour, col_lance = st.columns([1, 2])
        retour = col_retour.form_submit_button("← Retour")
        lance = col_lance.form_submit_button("Distribuer les rôles", type="primary")

    if retour:
        st.session_state.config_etape = "options"
        st.rerun()

    if lance:
        if any(not n for n in noms):
            st.error("Il manque un nom.")
        elif len(set(noms)) != nb:
            st.error("Deux joueurs portent le même nom.")
        else:
            save_joueurs(noms)
            maj_preferences(composition={
                "nb": nb, "n_loup": cfg.composition["loup"],
                "roles": {r.key: bool(st.session_state.get(f"n_{r.key}", False)) for r in ROLES_SPECIAUX if r.unique},
                "options": {cle: st.session_state[cle] for cle in CLES_OPTIONS if cle in st.session_state},
            })
            st.session_state.partie = nouvelle_partie(noms, cfg.composition, cfg.options)
            for cle in ("config_etape", "nb_joueurs_setup", "n_loup", *CLES_ROLES, *CLES_OPTIONS):
                st.session_state.pop(cle, None)
            st.rerun()
