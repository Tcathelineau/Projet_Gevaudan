"""Configuration d'une nouvelle partie : composition, options et noms des joueurs."""

import streamlit as st

from loup_garou.equilibre import (
    MAX_CHAOS, MAX_INFO, bilan, niveau_chaos, niveau_info, position_equilibre, remplissage,
)
from loup_garou.moteur.partie import composition_recommandee, nouvelle_partie
from loup_garou.moteur.persistance import load_joueurs, save_joueurs
from loup_garou.options import CADENCES, OPTIONS_DEFAUT
from loup_garou.roles import ROLES, ROLES_SPECIAUX
from loup_garou.ui.ecrans.accueil import aller_a
from loup_garou.ui.illustrations import svg_role
from loup_garou.ui.styles import css_infobulles


def ecran_installation():
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("← Menu", key="retour_menu_installation"):
            aller_a("accueil")
        st.markdown("#### 🐺 Loup-Garou")

    if "config_etape" not in st.session_state:
        st.session_state.config_etape = "roles"

    if st.session_state.config_etape == "roles":
        etape_roles()
    else:
        etape_noms()


def afficher_composition(nb, total, composition, n_villageois, options):
    if n_villageois < 0:
        st.error(
            f"Trop de rôles spéciaux pour {total} cartes "
            f"(il en manque {-n_villageois}) : réduis-en un ou augmente le nombre de joueurs."
        )
        return

    lignes = "".join(
        f'<div class="panneau-ligne"><span>{ROLES[cle].emoji} {ROLES[cle].nom}</span><span>{n}</span></div>'
        for cle, n in composition.items()
        if n > 0
    )
    st.markdown(
        f"""
        <div class="apercu-grille">
            <div class="panneau panneau-dense">
                <div class="panneau-titre">Composition</div>
                {lignes}
                <div class="panneau-ligne panneau-total"><span><b>Total</b></span><span><b>{total} / {total}</b></span></div>
            </div>
            {jauges_html(bilan(composition, nb, options)).strip()}
        </div>
        """,
        unsafe_allow_html=True,
    )

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


def saisir_options(composition):
    """Options de règles, limitées aux rôles présents dans la partie. Renvoie le dict d'options."""
    options = dict(OPTIONS_DEFAUT)
    with st.expander("⚙️ Options avancées"):
        if composition.get("sorciere"):
            col_soin, col_mort = st.columns(2)
            options["potions_sorciere"] = col_soin.number_input(
                "🧪 Potions de soin de la sorcière", min_value=1, max_value=5,
                value=OPTIONS_DEFAUT["potions_sorciere"], step=1, key="opt_potions",
            )
            options["potions_mort"] = col_mort.number_input(
                "☠️ Potions de mort de la sorcière", min_value=0, max_value=5,
                value=OPTIONS_DEFAUT["potions_mort"], step=1, key="opt_potions_mort",
            )
        if composition.get("voyante"):
            options["cadence_voyante"] = st.radio(
                "🔮 Visions de la voyante", list(CADENCES), format_func=CADENCES.get,
                index=OPTIONS_DEFAUT["cadence_voyante"] - 1, horizontal=True, key="opt_voyante",
            )
        if composition.get("loup_blanc"):
            options["cadence_loup_blanc"] = st.radio(
                "🌕 Festins du Loup Blanc", list(CADENCES), format_func=CADENCES.get,
                index=OPTIONS_DEFAUT["cadence_loup_blanc"] - 1, horizontal=True, key="opt_loup_blanc",
            )
        options["couple_hasard"] = st.toggle(
            "🎲 Couple tiré au sort, sans Cupidon",
            value=OPTIONS_DEFAUT["couple_hasard"], key="opt_couple_hasard",
            help="Le couple est désigné au hasard dès le départ ; Cupidon est remplacé par un villageois.",
        )
        options["trouple"] = st.toggle(
            "🎉 Mode fun : un trouple au lieu d'un couple",
            value=OPTIONS_DEFAUT["trouple"], key="opt_trouple",
            help="L'amour lie trois joueurs (choisis par Cupidon, ou tirés au sort). "
                 "Si l'un meurt, les deux autres le suivent.",
        )
        options["maire_depart"] = st.toggle(
            "👑 À égalité loups / village, le maire départage",
            value=OPTIONS_DEFAUT["maire_depart"], key="opt_maire",
            help="Activé : la partie continue à égalité, sauf si le maire est un loup. "
                 "Désactivé : les loups gagnent dès qu'ils sont aussi nombreux que les autres.",
        )
    return options


def etape_roles():
    st.markdown(css_infobulles(), unsafe_allow_html=True)
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

        with st.container(key="info_loup"):
            st.markdown(f"**{ROLES['loup'].emoji} {ROLES['loup'].nom}**")
            n_loup = st.number_input(
                f"{ROLES['loup'].emoji} {ROLES['loup'].nom}s",
                min_value=1, max_value=max(1, nb - 1),
                value=min(loups_defaut, max(1, nb - 1)), key="n_loup",
                label_visibility="collapsed",
            )
        composition = {"loup": n_loup}

        # Rôles uniques (au plus un exemplaire) : une simple case à cocher, en
        # grille de 4 colonnes ; le reste de la table devient Villageois.
        st.markdown("**Autres rôles** · coche ceux qui jouent")
        uniques = [role for role in ROLES_SPECIAUX if role.unique]
        for i in range(0, len(uniques), 4):
            cols = st.columns(4)
            for col, role in zip(cols, uniques[i:i + 4]):
                with col, st.container(key=f"info_{role.key}"):
                    composition[role.key] = role.lot * int(st.checkbox(
                        f"{role.emoji} {role.nom}" + (f" ×{role.lot}" if role.lot > 1 else ""),
                        value=bool(speciaux_defaut[role.key]), key=f"n_{role.key}",
                    ))

        # Rôles spéciaux en quantité libre (aucun aujourd'hui, mais le prochain
        # rôle de ce type n'aura besoin que d'une entrée dans ROLES).
        for role in ROLES_SPECIAUX:
            if not role.unique:
                with st.container(key=f"info_{role.key}"):
                    composition[role.key] = st.slider(
                        f"{role.emoji} {role.nom}", min_value=0, max_value=nb,
                        value=speciaux_defaut[role.key], key=f"n_{role.key}",
                    )

        total = nb + sum(ROLES[cle].cartes_en_plus * n for cle, n in composition.items())
        n_villageois = total - sum(composition.values())
        composition["villageois"] = max(n_villageois, 0)

        options = saisir_options(composition)
        if options["couple_hasard"] and composition.get("cupidon"):
            composition["villageois"] += composition["cupidon"]
            composition["cupidon"] = 0

        with apercu.container():
            afficher_composition(nb, total, composition, n_villageois, options)

        if st.button("Suivant : noms des joueurs →", type="primary", disabled=n_villageois < 0):
            st.session_state.config_nb = nb
            st.session_state.config_composition = composition
            st.session_state.config_options = options
            st.session_state.config_etape = "noms"
            st.rerun()


def etape_noms():
    nb = st.session_state.config_nb
    st.subheader("2. Qui joue ?")
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
        st.session_state.config_etape = "roles"
        st.rerun()

    if lance:
        if any(not n for n in noms):
            st.error("Il manque un nom.")
        elif len(set(noms)) != nb:
            st.error("Deux joueurs portent le même nom.")
        else:
            save_joueurs(noms)
            st.session_state.partie = nouvelle_partie(
                noms, st.session_state.config_composition, st.session_state.get("config_options"),
            )
            for cle in ("config_etape", "config_nb", "config_composition", "config_options"):
                st.session_state.pop(cle, None)
            st.rerun()
