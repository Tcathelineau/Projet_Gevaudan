import pytest

from loup_garou.roles import CATEGORIES, ROLES, ROLES_SPECIAUX


def test_chaque_role_est_range_sous_sa_cle():
    assert all(cle == role.key for cle, role in ROLES.items())


def test_les_camps_sont_connus():
    assert {r.camp for r in ROLES.values()} <= {"village", "loups"}


def test_roles_speciaux_excluent_loup_et_villageois():
    cles = {r.key for r in ROLES_SPECIAUX}
    assert "loup" not in cles and "villageois" not in cles
    assert cles == set(ROLES) - {"loup", "villageois"}


def test_cles_d_etat_initial_sans_collision_entre_roles():
    vues = {}
    for role in ROLES.values():
        for cle in role.etat_initial:
            assert cle not in vues, f"{cle} déclarée par {vues[cle]} et {role.key}"
            vues[cle] = role.key


def test_les_roles_sont_immuables():
    with pytest.raises(Exception):
        ROLES["loup"].nom = "Autre"


def test_chaque_role_a_un_tour_de_nuit():
    pytest.importorskip("streamlit")
    from loup_garou.ui.nuit_roles import NUIT_ROLES

    assert set(NUIT_ROLES) == set(ROLES)


def test_chaque_role_a_une_description():
    for role in ROLES.values():
        assert role.description.strip(), role.key


def test_chaque_role_special_a_une_categorie_connue():
    for role in ROLES_SPECIAUX:
        assert role.categorie in CATEGORIES, role.key


def test_chaque_categorie_a_au_moins_un_role():
    utilisees = {role.categorie for role in ROLES_SPECIAUX}
    assert set(CATEGORIES) == utilisees


def test_les_roles_de_loups_sont_classes_chez_les_loups_speciaux():
    for role in ROLES_SPECIAUX:
        if role.camp == "loups":
            assert role.categorie == "loups"
