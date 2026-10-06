from loup_garou.ui.sons import son_courant


def test_la_nuit_boucle():
    assert son_courant({"phase": "nuit"}) == ("nuit", True)


def test_le_reveil_distingue_les_nuits_calmes():
    assert son_courant({"phase": "reveil", "morts_nuit": []}) == ("jour", False)
    assert son_courant({"phase": "reveil", "morts_nuit": ["A"]}) == ("mort", False)


def test_le_conseil_ne_sonne_qu_apres_le_verdict():
    assert son_courant({"phase": "conseil"}) is None
    assert son_courant({"phase": "conseil"}, resultat_vote=True) == ("mort", False)


def test_la_fin_depend_du_vainqueur():
    assert son_courant({"phase": "fin", "message_fin": "Le village a gagné : x"}) == ("victoire_village", False)
    assert son_courant({"phase": "fin", "message_fin": "Les loups ont gagné : x"}) == ("victoire_loups", False)
    assert son_courant({"phase": "fin", "message_fin": "Les amoureux l'emportent"}) == ("victoire_loups", False)


def test_pas_de_son_pendant_l_election_ni_le_tir():
    assert son_courant({"phase": "election_maire"}) is None
    assert son_courant({"phase": "tir_chasseur"}) is None
