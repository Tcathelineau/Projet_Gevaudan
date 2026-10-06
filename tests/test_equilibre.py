import json

from loup_garou.equilibre import (
    DONNEES, ROLES_NOTES, Bilan, bilan, niveau_chaos, niveau_info, position_equilibre, remplissage,
)
from loup_garou.moteur.partie import composition_recommandee
from loup_garou.roles import ROLES


def test_chaque_role_a_ses_mesures():
    assert set(ROLES_NOTES) == set(ROLES)
    assert set(DONNEES["modele"]["roles"]) == set(ROLES) - {"villageois"}
    for notes in ROLES_NOTES.values():
        assert 0 <= notes["info"] <= 100 and 0 <= notes["chaos"] <= 100


def test_les_roles_de_loups_pesent_contre_le_village():
    for cle, role in ROLES.items():
        if role.camp == "loups":
            assert ROLES_NOTES[cle]["impact_pts"] < 0
    assert ROLES_NOTES["voyante"]["impact_pts"] > 0


def test_les_roles_ne_pesent_pas_tous_pareil():
    # Garde-fou contre l'écrasement des valeurs : au moins 8 niveaux d'impact distincts parmi les rôles du village.
    impacts = {round(n["impact_pts"]) for cle, n in ROLES_NOTES.items() if ROLES[cle].camp == "village"}
    assert len(impacts) >= 8


def test_l_information_est_reservee_aux_roles_qui_en_apportent_au_village():
    assert ROLES_NOTES["renard"]["info"] > ROLES_NOTES["chasseur"]["info"]
    assert ROLES_NOTES["voyante"]["info"] > 0 and ROLES_NOTES["louveteau"]["info"] == 0


def test_la_chance_est_une_probabilite():
    for nb in range(5, 19):
        loups, speciaux = composition_recommandee(nb)
        compo = {"loup": loups, **{c: n for c, n in speciaux.items() if n}}
        compo["villageois"] = nb - sum(compo.values())
        assert 0 < bilan(compo, nb).chance < 1


def test_un_loup_de_plus_fait_baisser_la_chance_du_village():
    base = bilan({"loup": 2, "villageois": 10}, 12).chance
    assert bilan({"loup": 3, "villageois": 9}, 12).chance < base


def test_un_role_du_village_fait_monter_la_chance():
    base = bilan({"loup": 3, "villageois": 11}, 14).chance
    assert bilan({"loup": 3, "voyante": 1, "villageois": 10}, 14).chance > base


def test_les_options_modifient_la_chance():
    compo = {"loup": 3, "voyante": 1, "villageois": 10}
    defaut = bilan(compo, 14).chance
    assert bilan(compo, 14, {"cadence_voyante": 1}).chance > defaut
    assert bilan(compo, 14, {"cadence_voyante": 3}).chance < defaut


def test_options_sans_role_correspondant_sans_effet():
    compo = {"loup": 3, "villageois": 11}
    assert bilan(compo, 14, {"cadence_voyante": 1, "potions_sorciere": 4}).chance == bilan(compo, 14).chance


def test_position_du_curseur_est_la_chance_en_pourcent():
    assert position_equilibre(Bilan(.5, 0, 0, 10)) == 50
    assert round(position_equilibre(Bilan(.37, 0, 0, 10))) == 37


def test_niveaux_info_et_chaos_rapportes_a_la_table():
    assert niveau_info(bilan({"loup": 3, "villageois": 11}, 14)) == "Faible"
    assert niveau_info(bilan({"loup": 1, "voyante": 1, "renard": 1, "villageois": 1}, 4)) == "Forte"
    assert niveau_chaos(bilan({"loup": 3, "villageois": 11}, 14)) == "Calme"
    assert niveau_chaos(bilan({"loup": 1, "loup_blanc": 1, "cupidon": 1, "juge_begue": 1}, 4)) == "Imprévisible"


def test_remplissage_borne():
    assert remplissage(1000, 10, 14) == 1.0 and remplissage(0, 10, 14) == 0.0


def test_le_fichier_de_mesures_documente_sa_methode():
    meta = DONNEES["meta"]
    assert meta["parties_par_mesure"] >= 1000 and 0 < meta["flair"] < 1
    assert json.dumps(DONNEES["validation"])
