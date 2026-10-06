from loup_garou.ui.sons import effet_courant, musique_courante


def test_une_musique_par_ambiance():
    assert musique_courante({"phase": "nuit"}) == "musique_nuit"
    assert musique_courante({"phase": "reveil"}) == "musique_jour"
    assert musique_courante({"phase": "election_maire"}) == "musique_jour"
    assert musique_courante({"phase": "conseil"}) == "musique_conseil"
    assert musique_courante({"phase": "tir_chasseur"}) == "musique_conseil"


def test_pas_de_musique_en_fin_de_partie():
    assert musique_courante({"phase": "fin"}) is None


def test_la_fin_depend_du_vainqueur():
    assert effet_courant({"phase": "fin", "message_fin": "Le village a gagné : x"}) == "victoire_village"
    assert effet_courant({"phase": "fin", "message_fin": "Les amoureux l'emportent"}) == "victoire_village"
    assert effet_courant({"phase": "fin", "message_fin": "Les loups ont gagné : x"}) == "victoire_loups"
    assert effet_courant({"phase": "fin", "message_fin": "A (Loup Blanc) l'emporte seul."}) == "victoire_loups"


def _nuit(role, devoile=True, tour=0):
    return {
        "phase": "nuit", "jour": 0, "tour": tour, "devoile": devoile, "ordre_nuit": ["A", "B"],
        "joueurs": {"A": {"role": role}, "B": {"role": "loup"}},
    }


def test_le_hurlement_ne_sonne_que_pour_un_loup_qui_decouvre_sa_carte():
    assert effet_courant(_nuit("loup")) == "hurlement"
    assert effet_courant(_nuit("louveteau")) == "hurlement"
    assert effet_courant(_nuit("villageois")) is None
    assert effet_courant(_nuit("loup", devoile=False)) is None


def test_le_hurlement_reste_pendant_le_tour_mais_pas_aux_nuits_suivantes():
    s = _nuit("loup")
    assert effet_courant(s) == "hurlement"
    assert effet_courant(s) == "hurlement"  # même tour : le lecteur reste en place
    s["jour"] = 1
    assert effet_courant(s) is None  # le loup connaît déjà son rôle


def test_le_hurlement_est_aussi_pour_un_joueur_devenu_loup():
    s = _nuit("villageois")
    assert effet_courant(s) is None
    s["joueurs"]["A"]["role"] = "loup"
    assert effet_courant(s) == "hurlement"
