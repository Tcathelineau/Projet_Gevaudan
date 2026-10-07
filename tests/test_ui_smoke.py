"""Parcours de l'interface avec le banc d'essai de Streamlit (sans navigateur).

Joue une partie complète en cliquant au hasard (graine fixe) : détecte les exceptions
d'affichage et les écrans sans issue après un changement dans ui/.
"""

import random
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

SRC = str(Path(__file__).resolve().parent.parent / "src")
ENTREE = str(Path(SRC) / "loup_garou_app.py")


def _app(partie=None, **session):
    sys.path.insert(0, SRC)
    at = AppTest.from_file(ENTREE, default_timeout=60)
    if partie is not None:
        at.session_state["partie"] = partie
    for cle, valeur in session.items():
        at.session_state[cle] = valeur
    return at.run()


def _creer_partie(nb_joueurs=18, nb_loups=2, sans=()):
    at = _app()
    assert not at.exception
    at.button(key="accueil_btn_nouvelle").click().run()
    for c in at.checkbox:
        c.check()
    for c in at.checkbox:
        if c.key in sans:
            c.uncheck()
    at.session_state["nb_joueurs_setup"] = nb_joueurs
    at.session_state["n_loup"] = nb_loups
    at.run()
    [b for b in at.button if b.label.startswith("Suivant")][0].click().run()
    for i, t in enumerate(at.text_input):
        t.set_value(f"J{i + 1}")
    [b for b in at.button if b.label == "Distribuer les rôles"][0].click().run()
    assert not at.exception
    assert "partie" in at.session_state, [e.value for e in at.error]
    return at.session_state["partie"]


def test_accueil_et_historique_s_affichent():
    at = _app()
    assert not at.exception
    at.session_state["ecran"] = "historique"
    assert not at.run().exception


# Deux tables qui, à elles deux, font jouer tous les rôles (les 18 joueurs ne tiennent pas avec tout coché).
TABLES = [
    pytest.param(("n_frere", "n_soeur"), 7, id="sans_fratries"),
    pytest.param(("n_soeur", "n_voleur", "n_loup_blanc", "n_chien_loup", "n_bouc_emissaire", "n_idiot"), 11, id="avec_freres"),
]


@pytest.mark.parametrize("sans, graine", TABLES)
def test_partie_complete_jusqu_a_la_fin(sans, graine):
    rng = random.Random(graine)
    at = _app(_creer_partie(sans=sans))
    ignores = ("Menu", "Recharger")
    for _ in range(1500):
        assert not at.exception, at.exception
        s = at.session_state["partie"]
        if s["phase"] == "fin":
            break
        boutons = [
            b for b in at.button
            if not b.disabled and b.key != "bouton_option"
            and not (b.key or "").startswith("recharg")
            and not any(m in b.label for m in ignores)
        ]
        formulaires = [
            b for b in boutons if (b.key or "").startswith("FormSubmitter") and "Retour" not in b.label
        ]
        boutons = formulaires or boutons
        assert boutons, f"écran sans issue en phase {s['phase']}"
        for r in at.radio:
            if rng.random() < 0.5:
                r.set_value(rng.choice(r.options))
        rng.choice(boutons).click().run()
    else:
        pytest.fail("la partie ne se termine pas en 1500 clics")
    assert at.session_state["partie"]["phase"] == "fin"


def test_jauges_d_equilibre_dans_la_composition():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    assert "Équilibre de la partie" in texte and "jauge-repere" in texte
    at.checkbox(key="n_voyante").check().run()
    assert not at.exception


def test_page_documentation_liste_tous_les_roles():
    from loup_garou.roles import ROLES

    at = _app()
    at.button(key="accueil_btn_documentation").click().run()
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    import html

    for role in ROLES.values():
        assert html.escape(role.nom) in texte
    at.button(key="retour_menu_documentation").click().run()
    assert not at.exception
    assert any(b.key == "accueil_btn_nouvelle" for b in at.button)


def _conseil(roles, **etat):
    """Partie au conseil du jour 1, aux rôles imposés."""
    from loup_garou.moteur.partie import nouvelle_partie

    composition = {}
    for role in roles.values():
        composition[role] = composition.get(role, 0) + 1
    s = nouvelle_partie(list(roles), composition)
    for nom, role in roles.items():
        s["joueurs"][nom]["role"] = role
    s["loups"] = [n for n, r in roles.items() if r in ("loup", "louveteau")]
    s.update(jour=1, phase="conseil", **etat)
    return s


def _voter(at, nom, cle, bouton="valider_vote"):
    at.button(key=f"pick_vote_{cle}_{nom}").click().run()
    at.button(key=bouton).click().run()
    return at


def _nuit_servante(roles, condamne):
    """Nuit 2, au tour de la servante C ; le village a éliminé `condamne` au jour 1."""
    from loup_garou.moteur.partie import enregistrer_condamne, tuer

    s = _conseil(roles)
    s["jour"] = 1
    tuer(s, condamne, "est éliminé par le village")
    enregistrer_condamne(s, condamne)
    s.update(jour=2, phase="nuit", ordre_nuit=["C"], tour=0, devoile=True, transfert=True)
    return s


def test_la_servante_reprend_le_role_du_condamne_de_nuit():
    roles = {"A": "loup", "B": "loup", "C": "servante", "D": "villageois", "E": "villageois", "F": "villageois"}
    at = _app(_nuit_servante(roles, "B"))
    assert not at.exception
    at.button(key="pick_serv_2_0_B").click().run()
    at.run()  # st.rerun laisse l'arbre périmé : on le rafraîchit
    assert not at.exception
    s = at.session_state["partie"]
    assert s["joueurs"]["C"]["role"] == "loup" and "C" in s["loups"]
    assert s["servante_nuit"] == {"servante": "C", "mort": "B"}
    assert "nouvelle carte" in " ".join(m.value for m in at.markdown)
    at.button(key="fin_2_0").click().run()
    s = at.session_state["partie"]
    assert s["phase"] == "reveil"
    at.run()
    texte = " ".join(m.value for m in at.markdown)
    assert "La servante dévouée est intervenue" in texte and "C</div>" in texte


def test_la_servante_peut_ne_rien_faire():
    roles = {"A": "loup", "B": "villageois", "C": "servante", "D": "villageois", "E": "villageois"}
    at = _app(_nuit_servante(roles, "B"))
    at.button(key="servante_rien_2_0").click().run()
    s = at.session_state["partie"]
    assert s["joueurs"]["C"]["role"] == "servante" and s["phase"] == "reveil"
    at.run()
    assert "La servante dévouée est intervenue" not in " ".join(m.value for m in at.markdown)


def test_la_servante_n_a_rien_a_reprendre_sans_condamne_la_veille():
    roles = {"A": "loup", "B": "villageois", "C": "servante", "D": "villageois", "E": "villageois"}
    s = _nuit_servante(roles, "B")
    s["condamnes"] = None
    at = _app(s)
    assert not at.exception
    assert not any((b.key or "").startswith("pick_serv") for b in at.button)
    assert any(b.key == "fin_2_0" for b in at.button)


def test_le_juge_begue_declenche_un_second_vote():
    roles = {"A": "loup", "B": "villageois", "C": "juge_begue", "D": "villageois", "E": "villageois", "F": "villageois"}
    at = _voter(_app(_conseil(roles, second_vote=1)), "B", 1)
    assert not at.exception
    assert not any(b.label == "La nuit tombe" for b in at.button)
    at = _voter(at, "D", "1b", "valider_vote2")
    assert not at.exception
    s = at.session_state["partie"]
    assert not s["joueurs"]["B"]["vivant"] and not s["joueurs"]["D"]["vivant"]
    assert any(b.label == "La nuit tombe" for b in at.button)


def test_sans_juge_un_seul_vote():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _voter(_app(_conseil(roles)), "B", 1)
    assert any(b.label == "La nuit tombe" for b in at.button)


def _fin(roles, message="Le village a gagné : tous les loups sont morts."):
    from loup_garou.moteur.partie import terminer_partie, tuer

    s = _conseil(roles)
    s["phase"] = "conseil"
    tuer(s, "A", "est éliminé par le village", "village")
    terminer_partie(s, message)
    return s


def test_le_bilan_de_fin_s_affiche():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_fin(roles))
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    assert "bil-tuile" in texte and "Loups démasqués" in texte and "Bon flair" in texte
    assert "Les disparitions" in " ".join(h.value for h in at.subheader)


def test_rejouer_relance_une_partie_avec_les_memes_joueurs():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_fin(roles))
    at.button(key="fin_rejouer").click().run()
    s = at.session_state["partie"]
    assert not at.exception and s["phase"] == "nuit" and s["jour"] == 0
    assert sorted(s["joueurs"]) == ["A", "B", "C", "D"]
    assert sorted(d["role"] for d in s["joueurs"].values()) == ["loup", "villageois", "villageois", "villageois"]


def test_retour_au_menu_apres_la_partie():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_fin(roles))
    at.button(key="fin_menu").click().run()
    assert "partie" not in at.session_state
    assert any(b.key == "accueil_btn_nouvelle" for b in at.button)


def test_documentation_a_un_onglet_regles_et_un_onglet_roles():
    at = _app()
    at.button(key="accueil_btn_documentation").click().run()
    assert [t.label for t in at.tabs] == ["🃏 Les rôles", "📖 Comment jouer"]
    assert "Comment gagner" in " ".join(m.value for m in at.markdown)


def test_rappel_des_regles_dans_la_barre_laterale():
    roles = {"A": "loup", "B": "villageois", "C": "voyante", "D": "villageois"}
    at = _app(_conseil(roles))
    assert any(e.label == "📖 Rappel des règles" for e in at.sidebar.expander)
    assert "Voyante" in " ".join(m.value for m in at.sidebar.markdown)


def test_les_noms_de_la_derniere_partie_sont_preremplis():
    from loup_garou.moteur.persistance import save_joueurs

    save_joueurs(["Alice", "Bob", "Chloé"])
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    [b for b in at.button if b.label.startswith("Suivant")][0].click().run()
    valeurs = [at.text_input(key=f"nom_{i}").value for i in range(len(at.text_input))]
    assert valeurs[:3] == ["Alice", "Bob", "Chloé"] and set(valeurs[3:]) == {""}


def test_distribuer_retient_les_noms():
    from loup_garou.moteur.persistance import load_joueurs

    _creer_partie(nb_joueurs=7, nb_loups=1, sans=tuple(f"n_{r}" for r in (
        "sorciere", "voyante", "cupidon", "chasseur", "salvateur", "enfant_sauvage", "voleur", "renard",
        "loup_blanc", "chien_loup", "louveteau", "soeur", "frere", "servante", "juge_begue")))
    assert sorted(load_joueurs()) == [f"J{i}" for i in range(1, 8)]


def test_aucun_son_par_defaut():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    nuit = _conseil(roles)
    nuit.update(phase="nuit", jour=1, ordre_nuit=["A"], tour=0, devoile=True, transfert=True)
    assert len(_app(nuit).get("audio")) == 0  # même sur la carte d'un loup
    assert len(_app(_conseil(roles)).get("audio")) == 0
    assert len(_app(_fin(roles)).get("audio")) == 0


def test_la_musique_suit_la_phase_et_se_coupe_depuis_le_menu_option():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    nuit = _conseil(roles)
    nuit.update(phase="nuit", jour=1)
    at = _app(nuit, musique_on=True)
    assert len(at.get("audio")) == 1
    at.session_state["options_ouvert"] = True
    at.run()
    at.checkbox(key="case_musique_on").uncheck().run()
    assert len(at.get("audio")) == 0
    assert len(_app(_conseil(roles), musique_on=True).get("audio")) == 1  # musique du conseil


def test_les_reglages_du_son_survivent_a_la_fermeture_du_menu():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_conseil(roles), options_ouvert=True)
    at.checkbox(key="case_musique_on").check().run()
    assert at.session_state["musique_on"] is True and len(at.get("audio")) == 1
    at.session_state["options_ouvert"] = False
    at.run()
    assert at.session_state["musique_on"] is True and len(at.get("audio")) == 1


def test_le_hurlement_accompagne_la_carte_d_un_loup_et_se_coupe():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    s = _conseil(roles)
    s.update(phase="nuit", jour=1, ordre_nuit=["A"], tour=0, devoile=True, transfert=True)
    at = _app(s, musique_on=True, sons_on=True, cri_on=True, options_ouvert=True)
    assert len(at.get("audio")) == 2  # musique de nuit + hurlement
    at.checkbox(key="case_cri_on").uncheck().run()
    assert len(at.get("audio")) == 1



def test_les_roles_a_cocher_sont_ranges_par_categorie():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    texte = " ".join(m.value for m in at.markdown)
    for titre in ("Information", "Protection et pouvoirs de mort", "Chaos", "Loups spéciaux"):
        assert titre in texte
    assert texte.index("Information") < texte.index("Protection et pouvoirs") < texte.index("Loups spéciaux")
    assert "cat-titre" in texte


def test_la_page_statistiques_lit_les_parties_archivees():
    import json
    import os

    os.makedirs("historique")
    for i, issue in enumerate(("Le village a gagné : x", "Les loups ont gagné : y")):
        with open(f"historique/partie_2026010{i}_000000.json", "w", encoding="utf-8") as f:
            json.dump({"date": "2026-01-01T00:00:00", "issue": issue, "journal": [], "joueurs": {
                "A": {"role": "loup", "vivant": i == 1, "amoureux": False},
                "B": {"role": "voyante", "vivant": i == 0, "amoureux": False},
            }}, f)
    at = _app()
    at.session_state["ecran"] = "historique"
    at.run()
    assert not at.exception
    assert [t.label for t in at.tabs] == ["📜 Parties", "📊 Statistiques"]
    texte = " ".join(m.value for m in at.markdown)
    assert "Voyante" in texte and "bil-tuile" in texte and "5 à 8 joueurs" in texte


def test_la_page_statistiques_sans_partie():
    at = _app()
    at.session_state["ecran"] = "historique"
    at.run()
    assert not at.exception


def test_une_ancienne_sauvegarde_se_reprend_sans_erreur():
    import json

    from loup_garou.moteur.migrations import VERSION
    from loup_garou.moteur.partie import nouvelle_partie

    s = nouvelle_partie(list("ABCDE"), {"loup": 1, "voyante": 1, "sorciere": 1, "villageois": 2})
    for cle in ("version", "morts", "composition", "options", "servante_nuit", "double_victime", "instantanes"):
        s.pop(cle, None)
    with open("save.json", "w", encoding="utf-8") as f:
        json.dump(s, f)
    at = _app()
    assert not at.exception
    assert at.session_state["partie"]["version"] == VERSION and at.session_state["partie"]["phase"] == "nuit"


def test_une_sauvegarde_corrompue_ramene_au_menu():
    with open("save.json", "w", encoding="utf-8") as f:
        f.write("{ corrompue")
    at = _app()
    assert not at.exception and any(b.key == "accueil_btn_nouvelle" for b in at.button)


def test_abandonner_la_partie_demande_confirmation():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_conseil(roles), options_ouvert=True)
    at.button(key="abandon_demande_bouton").click().run()
    assert "partie" in at.session_state and any(b.key == "abandon" for b in at.button)
    at.button(key="continuer_partie").click().run()
    assert "partie" in at.session_state and any(b.key == "abandon_demande_bouton" for b in at.button)
    at.button(key="abandon_demande_bouton").click().run()
    at.button(key="abandon").click().run()
    assert "partie" not in at.session_state


def test_recharger_une_etape_garde_les_reglages_du_son():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    s = _conseil(roles)
    s["instantanes"] = [{"id": "nuit_1", "libelle": "Nuit 1", "etat": {k: v for k, v in s.items() if k != "instantanes"}}]
    at = _app(s, options_ouvert=True, musique_on=True, sons_on=True, reload_choix="nuit_1")
    at.button(key="reload_ok").click().run()
    assert at.session_state["musique_on"] is True and at.session_state["sons_on"] is True


def _tour_de_nuit(roles, nom, **etat):
    """Nuit 1, au tour de `nom`, carte découverte."""
    s = _conseil(roles)
    s.update(phase="nuit", jour=1, ordre_nuit=[nom], tour=0, devoile=True, transfert=True, **etat)
    return s


def test_les_loups_peuvent_designer_l_un_des_leurs():
    roles = {"A": "loup", "B": "loup", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "A"))
    assert not at.exception
    boutons = {b.key for b in at.button}
    assert "pick_loup_1_0_B" in boutons and "pick_loup_1_0_C" in boutons
    assert "pick_loup_1_0_A" not in boutons  # pas soi-même


def test_les_loups_votent_contre_un_des_leurs_et_il_meurt():
    roles = {"A": "loup", "B": "loup", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "A"))
    at.button(key="pick_loup_1_0_B").click().run()
    at.button(key="devorer_1_0").click().run()
    s = at.session_state["partie"]
    assert s["phase"] == "reveil" and s["morts_nuit"] == ["B"]


def test_la_voyante_choisit_entre_un_role_et_le_couple_quand_il_est_tire_au_sort():
    roles = {"A": "loup", "B": "voyante", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _tour_de_nuit(roles, "B", amoureux=["C", "D"])
    s["options"]["couple_hasard"] = True
    at = _app(s)
    assert not at.exception
    at.button(key="voy_couple_1_0").click().run()
    partie = at.session_state["partie"]
    assert partie["voyante_a_vu_couple"] is True
    assert "Les amoureux sont C et D" in " ".join(m.value for m in at.markdown)
    assert any("découvre le couple" in e["texte"] for e in partie["journal"])


def test_la_voyante_peut_preferer_un_role():
    roles = {"A": "loup", "B": "voyante", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _tour_de_nuit(roles, "B", amoureux=["C", "D"])
    s["options"]["couple_hasard"] = True
    at = _app(s)
    at.button(key="voy_role_1_0").click().run()
    assert any(b.key == "pick_voy_1_0_C" for b in at.button)  # les dalles de sondage apparaissent


def test_la_voyante_n_a_que_les_roles_sans_couple_tire_au_sort():
    roles = {"A": "loup", "B": "voyante", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    assert not any((b.key or "").startswith("voy_couple") for b in at.button)
    assert any(b.key == "pick_voy_1_0_C" for b in at.button)


def test_le_couple_n_est_decouvrable_qu_une_fois():
    roles = {"A": "loup", "B": "voyante", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _tour_de_nuit(roles, "B", amoureux=["C", "D"], voyante_a_vu_couple=True)
    s["options"]["couple_hasard"] = True
    at = _app(s)
    assert not any((b.key or "").startswith("voy_couple") for b in at.button)


def test_cupidon_est_grise_quand_le_couple_est_tire_au_sort():
    at = _app(opt_couple_hasard=True)
    at.button(key="accueil_btn_nouvelle").click().run()
    case = at.checkbox(key="n_cupidon")
    assert case.disabled and "devient villageois" in case.label
    sans = _app()
    sans.button(key="accueil_btn_nouvelle").click().run()
    assert not sans.checkbox(key="n_cupidon").disabled


def test_la_fin_de_partie_montre_les_coulisses_et_la_liste_compacte():
    roles = {"A": "loup", "B": "sorciere", "C": "villageois", "D": "villageois"}
    s = _fin(roles)
    s["amoureux"] = ["B", "C"]
    s["joueurs"]["B"]["amoureux"] = s["joueurs"]["C"]["amoureux"] = True
    from loup_garou.moteur.journal import log

    log(s, "Cupidon X lie B et C.", "nuit")
    log(s, "La sorcière B utilise une potion de soin.", "nuit")
    at = _app(s)
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    assert "roles-grille" in texte and "Les amoureux" in texte and "Les potions" in texte
    assert "Il restait" in texte and "Mise en place" in texte
    assert "Les coulisses" in " ".join(h.value for h in at.subheader)


def test_le_gong_sonne_au_reveil_quand_un_innocent_meurt():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    s = _conseil(roles)
    s.update(phase="reveil", morts_nuit=["B"])
    assert len(_app(s).get("audio")) == 0  # son désactivé par défaut
    assert len(_app(s, sons_on=True).get("audio")) == 1  # le gong (pas de musique : réglage coupé)
    assert len(_app(s, sons_on=True, musique_on=True).get("audio")) == 2  # gong + musique tendue du conseil


def test_les_hurlements_accompagnent_la_victoire_des_loups_meme_sans_les_bruitages():
    roles = {"A": "loup", "B": "loup", "C": "villageois"}
    s = _fin(roles, "Les loups ont gagné : ils sont plus nombreux que les villageois.")
    assert len(_app(s, cri_on=True).get("audio")) == 1
    assert len(_app(s, sons_on=True).get("audio")) == 1
    assert len(_app(s).get("audio")) == 0


def test_la_composition_n_a_plus_de_panneau_liste_mais_garde_l_equilibre_centre():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    texte = " ".join(m.value for m in at.markdown)
    assert "apercu-centre" in texte and "Équilibre de la partie" in texte
    assert 'class="panneau-titre">Composition' not in texte and "apercu-grille" not in texte


def test_la_fenetre_du_couple_s_ouvre_une_seule_fois_par_amoureux():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    s = _tour_de_nuit(roles, "B", amoureux=["B", "C"])
    s["joueurs"]["B"]["amoureux"] = s["joueurs"]["C"]["amoureux"] = True
    at = _app(s)
    assert not at.exception
    assert at.session_state["partie"]["joueurs"]["B"]["couple_vu"] is True
    assert not at.session_state["partie"]["joueurs"]["C"].get("couple_vu")  # C ne l'a pas encore découvert


def test_pas_de_fenetre_de_couple_pour_un_joueur_seul():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    assert not at.exception and not at.session_state["partie"]["joueurs"]["B"].get("couple_vu")


def test_les_compteurs_de_joueurs_et_de_loups_se_pilotent_par_boutons_ronds():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    assert at.session_state["nb_joueurs_setup"] == 7 and at.session_state["n_loup"] == 1
    at.button(key="nb_joueurs_setup_plus").click().run()
    assert at.session_state["nb_joueurs_setup"] == 8
    at.button(key="n_loup_plus").click().run()
    assert at.session_state["n_loup"] == 2
    at.button(key="n_loup_moins").click().run()
    assert at.session_state["n_loup"] == 1 and at.button(key="n_loup_moins").disabled


def test_le_nombre_de_joueurs_est_borne():
    at = _app(nb_joueurs_setup=5)
    at.button(key="accueil_btn_nouvelle").click().run()
    assert at.button(key="nb_joueurs_setup_moins").disabled
    at.session_state["nb_joueurs_setup"] = 18
    at.run()
    assert at.button(key="nb_joueurs_setup_plus").disabled


def test_le_nombre_de_loups_suit_le_plafond_quand_les_joueurs_diminuent():
    at = _app(nb_joueurs_setup=8, n_loup=7)
    at.button(key="accueil_btn_nouvelle").click().run()
    at.session_state["nb_joueurs_setup"] = 5
    at.run()
    assert at.session_state["n_loup"] == 4  # au plus joueurs - 1


def test_les_categories_n_ont_plus_de_precisions():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    texte = " ".join(m.value for m in at.markdown)
    assert "Information" in texte and "Apprennent qui est qui" not in texte and "Changent les camps" not in texte


def test_les_boutons_plus_et_moins_n_ont_pas_d_infobulle():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    for cle in ("nb_joueurs_setup_moins", "nb_joueurs_setup_plus", "n_loup_moins", "n_loup_plus"):
        assert not at.button(key=cle).help


def test_les_deux_compteurs_coexistent():
    # L'agencement en une rangée se vérifie dans le navigateur ; ici, que les deux compteurs répondent.
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    assert not at.exception
    assert at.session_state["nb_joueurs_setup"] == 7 and at.session_state["n_loup"] == 1


def test_le_panneau_du_reveil_annonce_le_grognement_de_l_ours_et_le_corbeau():
    roles = {"A": "montreur_ours", "B": "loup", "C": "villageois", "D": "corbeau", "E": "villageois"}
    s = _conseil(roles)
    s.update(phase="reveil", morts_nuit=[], corbeau_cible="C")
    texte = " ".join(m.value for m in _app(s).markdown)
    assert "L'ours grogne" in texte and "Le corbeau l'a désigné" in texte


def test_le_panneau_reste_muet_sans_loup_voisin_de_l_ours():
    roles = {"A": "montreur_ours", "B": "villageois", "C": "loup", "D": "villageois", "E": "villageois"}
    s = _conseil(roles)
    s.update(phase="reveil", morts_nuit=[])
    assert "L'ours grogne" not in " ".join(m.value for m in _app(s).markdown)


def test_le_corbeau_designe_un_joueur_pour_le_prochain_vote():
    roles = {"A": "loup", "B": "corbeau", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    at.button(key="pick_corb_1_0_C").click().run()
    at.button(key="corbeau_1_0").click().run()
    s = at.session_state["partie"]
    assert s["corbeau_cible"] == "C" and any("deux voix de plus" in e["texte"] for e in s["journal"])


def test_le_corbeau_peut_ne_designer_personne():
    roles = {"A": "loup", "B": "corbeau", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    at.button(key="corbeau_rien_1_0").click().run()
    assert not at.session_state["partie"].get("corbeau_cible")


def test_le_conseil_rappelle_la_designation_du_corbeau():
    roles = {"A": "loup", "B": "corbeau", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _conseil(roles)
    s["corbeau_cible"] = "C"
    assert "Le corbeau a désigné C" in " ".join(m.value for m in _app(s).markdown)


def test_la_petite_fille_espionne_sans_etre_surprise(monkeypatch):
    import random

    monkeypatch.setattr(random, "random", lambda: 0.9)
    roles = {"A": "loup", "B": "petite_fille", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _tour_de_nuit(roles, "B", votes_loups=["C"])
    at = _app(s)
    at.button(key="pf_espionne_1_0").click().run()
    at.run()
    partie = at.session_state["partie"]
    assert not partie["petite_fille_surprise"]
    texte = " ".join(m.value for m in at.markdown)
    assert "Les loups ont désigné C" in texte and "deux silhouettes" in texte and "A" in texte


def test_la_petite_fille_surprise_sera_devoree(monkeypatch):
    import random

    monkeypatch.setattr(random, "random", lambda: 0.1)
    roles = {"A": "loup", "B": "petite_fille", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "B", votes_loups=["C"]))
    at.button(key="pf_espionne_1_0").click().run()
    assert at.session_state["partie"]["petite_fille_surprise"] == "B"


def test_la_petite_fille_peut_dormir():
    roles = {"A": "loup", "B": "petite_fille", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    at.button(key="pf_dort_1_0").click().run()
    assert at.session_state["partie"]["phase"] == "reveil"


def test_l_idiot_condamne_survit_la_premiere_fois():
    roles = {"A": "loup", "B": "idiot", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _voter(_app(_conseil(roles)), "B", 1)
    s = at.session_state["partie"]
    assert s["joueurs"]["B"]["vivant"] and s["joueurs"]["B"]["vote_perdu"]
    at.run()
    assert "idiot du village" in " ".join(m.value for m in at.markdown)
    assert any(b.label == "La nuit tombe" for b in at.button)


def test_l_idiot_deja_revele_meurt_au_second_vote():
    roles = {"A": "loup", "B": "idiot", "C": "villageois", "D": "villageois", "E": "villageois"}
    s = _conseil(roles)
    s["joueurs"]["B"].update(idiot_revele=True, vote_perdu=True)
    at = _voter(_app(s), "B", 1)
    assert not at.session_state["partie"]["joueurs"]["B"]["vivant"]


def test_le_bouc_emissaire_est_condamne_en_cas_d_egalite():
    roles = {"A": "loup", "B": "bouc_emissaire", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_conseil(roles))
    at.button(key="bouc_1").click().run()
    assert not at.session_state["partie"]["joueurs"]["B"]["vivant"]


def test_pas_de_bouton_d_egalite_sans_bouc_emissaire():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    assert not any((b.key or "").startswith("bouc_") for b in _app(_conseil(roles)).button)


def test_la_meute_s_affiche_dans_le_menu_de_gauche():
    roles = {"A": "loup", "B": "loup", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _app(_tour_de_nuit(roles, "A"))
    assert "La meute" in " ".join(m.value for m in at.sidebar.markdown)
    assert "La meute" not in " ".join(m.value for m in at.main.markdown)


def test_les_textes_d_information_ont_un_emoji_de_chaque_cote():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    at = _app(_tour_de_nuit(roles, "B"))
    plaquettes = [m.value for m in at.main.markdown if m.value.startswith('<div class="plaquette')]
    assert plaquettes and all(p.count('class="plaquette-icone"') == 2 for p in plaquettes)
    icones = [p.split('plaquette-icone">')[1].split("<")[0] for p in plaquettes]
    assert all(p.split('plaquette-icone">')[-1].split("<")[0] == i for p, i in zip(plaquettes, icones))
