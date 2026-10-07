import streamlit as st

from loup_garou.ui.sons import effet_autorise, effet_courant, marquer_cri, musique_courante


def partie(phase, **extra):
    s = {
        "phase": phase, "jour": 1, "tour": 0, "devoile": False, "ordre_nuit": [], "morts_nuit": [],
        "joueurs": {
            "A": {"role": "loup"}, "B": {"role": "villageois"}, "C": {"role": "voyante"}, "D": {"role": "loup"},
        },
    }
    s.update(extra)
    return s


def test_une_musique_par_ambiance():
    assert musique_courante(partie("nuit")) == "musique_nuit"
    assert musique_courante(partie("election_maire")) == "musique_conseil"
    assert musique_courante(partie("conseil")) == "musique_conseil"
    assert musique_courante(partie("tir_chasseur")) == "musique_conseil"


def test_le_reveil_calme_garde_la_musique_du_jour():
    assert musique_courante(partie("reveil")) == "musique_jour"


def test_la_tension_du_conseil_commence_des_le_reveil_quand_il_y_a_des_morts():
    assert musique_courante(partie("reveil", morts_nuit=["B"])) == "musique_conseil"


def test_pas_de_musique_en_fin_de_partie():
    assert musique_courante(partie("fin")) is None


def test_la_fin_depend_du_vainqueur():
    assert effet_courant(partie("fin", message_fin="Le village a gagné : x")) == "victoire_village"
    assert effet_courant(partie("fin", message_fin="Les amoureux l'emportent")) == "victoire_village"
    assert effet_courant(partie("fin", message_fin="Les loups ont gagné : x")) == "victoire_loups"
    assert effet_courant(partie("fin", message_fin="A (Loup Blanc) l'emporte seul.")) == "victoire_loups"


def test_un_gong_grave_quand_un_innocent_meurt_la_nuit():
    assert effet_courant(partie("reveil", morts_nuit=["B"])) == "mort_gentil"
    assert effet_courant(partie("reveil", morts_nuit=["C", "A"])) == "mort_gentil"


def test_pas_de_gong_quand_seul_un_loup_meurt_ou_que_personne_ne_meurt():
    assert effet_courant(partie("reveil", morts_nuit=["A"])) is None
    assert effet_courant(partie("reveil")) is None


def test_le_gong_accompagne_aussi_le_verdict_du_village():
    assert effet_courant(partie("conseil"), ["B"]) == "mort_gentil"
    assert effet_courant(partie("conseil"), ["A"]) is None
    assert effet_courant(partie("conseil"), []) is None


def nuit(role, devoile=True, tour=0):
    s = partie("nuit", tour=tour, devoile=devoile, ordre_nuit=["A", "B"])
    s["joueurs"]["A"]["role"] = role
    return s


def test_le_hurlement_ne_sonne_que_pour_un_loup_qui_decouvre_sa_carte():
    assert effet_courant(nuit("loup")) == "hurlement"
    assert effet_courant(nuit("louveteau")) == "hurlement"
    assert effet_courant(nuit("villageois")) is None
    assert effet_courant(nuit("loup", devoile=False)) is None


def test_le_hurlement_reste_pendant_le_tour_mais_pas_aux_nuits_suivantes():
    s = nuit("loup")
    assert effet_courant(s) == "hurlement"
    marquer_cri(s)
    assert effet_courant(s) == "hurlement"  # même tour : le lecteur reste en place
    s["jour"] = 2
    assert effet_courant(s) is None  # le loup connaît déjà son rôle


def test_un_hurlement_non_joue_n_est_pas_consomme():
    s = nuit("loup")
    effet_courant(s)  # son désactivé : jamais marqué
    s["jour"] = 2
    assert effet_courant(s) == "hurlement"


def test_le_hurlement_est_aussi_pour_un_joueur_devenu_loup():
    s = nuit("villageois")
    assert effet_courant(s) is None
    s["joueurs"]["A"]["role"] = "loup"
    assert effet_courant(s) == "hurlement"


def test_reglages_des_effets(monkeypatch):
    def avec(**reglages):
        monkeypatch.setattr(st, "session_state", reglages)

    avec()
    assert not any(effet_autorise(e) for e in ("hurlement", "victoire_loups", "victoire_village", "mort_gentil"))
    avec(sons_on=True)
    assert effet_autorise("mort_gentil") and effet_autorise("victoire_village") and effet_autorise("victoire_loups")
    assert not effet_autorise("hurlement")
    avec(cri_on=True)
    assert effet_autorise("hurlement") and effet_autorise("victoire_loups")  # la victoire des loups hurle aussi
    assert not effet_autorise("mort_gentil") and not effet_autorise("victoire_village")
