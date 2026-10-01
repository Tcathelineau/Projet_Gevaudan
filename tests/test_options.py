from loup_garou.options import CADENCES, OPTIONS_DEFAUT, nuit_active, opt, prochaine_nuit, taille_couple


def test_opt_retombe_sur_le_defaut_pour_une_ancienne_sauvegarde():
    assert opt({}, "potions_sorciere") == OPTIONS_DEFAUT["potions_sorciere"]


def test_opt_lit_la_valeur_de_la_partie():
    assert opt({"options": {"potions_sorciere": 3}}, "potions_sorciere") == 3


def test_taille_couple():
    assert taille_couple({}) == 2
    assert taille_couple({"options": {"trouple": True}}) == 3


def test_nuit_active_jamais_la_nuit_zero():
    assert not nuit_active({"jour": 0}, 1)


def test_nuit_active_toutes_les_nuits():
    assert all(nuit_active({"jour": j}, 1) for j in range(1, 6))


def test_nuit_active_une_nuit_sur_deux():
    assert [j for j in range(0, 8) if nuit_active({"jour": j}, 2)] == [1, 3, 5, 7]


def test_nuit_active_une_nuit_sur_trois():
    assert [j for j in range(0, 9) if nuit_active({"jour": j}, 3)] == [1, 4, 7]


def test_prochaine_nuit():
    assert prochaine_nuit({"jour": 1}, 2) == 3
    assert prochaine_nuit({"jour": 2}, 2) == 3
    assert prochaine_nuit({"jour": 1}, 3) == 4


def test_cadences_couvrent_les_options_proposees():
    assert set(CADENCES) == {1, 2, 3}
