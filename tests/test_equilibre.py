import pytest

from loup_garou.equilibre import NOTES, bilan, niveau_chaos, niveau_equilibre, niveau_info
from loup_garou.roles import ROLES


def test_chaque_role_a_ses_notes():
    assert set(NOTES) == set(ROLES)
    for notes in NOTES.values():
        assert 0 <= notes.info <= 5 and 0 <= notes.chaos <= 5


def test_force_des_camps_a_le_bon_signe():
    for cle, role in ROLES.items():
        if role.camp == "loups":
            assert NOTES[cle].force < 0
    assert NOTES["voyante"].force > 0


def test_bilan_somme_les_notes():
    b = bilan({"loup": 2, "voyante": 1, "villageois": 5}, 8, {"cadence_voyante": 1})
    assert b.force == -12 + 7 + 5
    assert b.info == 2 + 5
    assert b.joueurs == 8


def test_cadence_de_la_voyante_modifie_sa_force():
    compo = {"voyante": 1}
    assert bilan(compo, 1, {"cadence_voyante": 1}).force == 7
    assert bilan(compo, 1, {"cadence_voyante": 2}).force == 5
    assert bilan(compo, 1, {"cadence_voyante": 3}).force == 4


def test_potions_de_la_sorciere():
    base = bilan({"sorciere": 1}, 1)
    assert bilan({"sorciere": 1}, 1, {"potions_sorciere": 3}).force == base.force + 2
    avec_mort = bilan({"sorciere": 1}, 1, {"potions_mort": 2})
    assert avec_mort.force == base.force + 2 and avec_mort.chaos == base.chaos + 1


def test_options_de_couple_et_de_maire():
    base = bilan({"villageois": 4}, 4)
    assert bilan({"villageois": 4}, 4, {"couple_hasard": True}).chaos == base.chaos + 2
    assert bilan({"villageois": 4}, 4, {"trouple": True}).chaos == base.chaos
    assert bilan({"cupidon": 1, "villageois": 3}, 4, {"trouple": True}).chaos == bilan({"cupidon": 1, "villageois": 3}, 4).chaos + 3
    assert bilan({"villageois": 4}, 4, {"maire_depart": False}).force == base.force - 2


@pytest.mark.parametrize("force, libelle, camp", [
    (0, "Équilibrée", None),
    (-3, "Équilibrée", None),
    (4, "Léger avantage au village", "village"),
    (-9, "Léger avantage aux loups", "loups"),
    (10, "Net avantage au village", "village"),
    (-12, "Net avantage aux loups", "loups"),
])
def test_niveau_equilibre(force, libelle, camp):
    assert niveau_equilibre(force) == (libelle, camp)


def test_niveaux_info_et_chaos_rapportes_a_la_table():
    assert niveau_info(bilan({"loup": 3, "villageois": 11}, 14)) == "Faible"
    assert niveau_info(bilan({"voyante": 1, "renard": 1, "villageois": 2}, 4)) == "Forte"
    assert niveau_chaos(bilan({"loup": 3, "villageois": 11}, 14)) == "Calme"
    assert niveau_chaos(bilan({"cupidon": 1, "voleur": 1, "villageois": 2}, 4)) == "Imprévisible"
