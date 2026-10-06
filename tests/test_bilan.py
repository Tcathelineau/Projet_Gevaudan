from loup_garou.moteur.bilan import bilan_partie
from loup_garou.moteur.partie import enregistrer_condamne, tuer


def chiffres(s):
    return {libelle: valeur for _, libelle, valeur in bilan_partie(s)["chiffres"]}


def test_chaque_mort_est_enregistree_avec_son_genre(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"})
    s["phase"] = "conseil"
    s["jour"] = 1
    tuer(s, "B", "est éliminé par le village", "village")
    assert s["morts"] == [{"nom": "B", "role": "villageois", "camp": "village", "genre": "village",
                           "jour": 1, "moment": "jour"}]


def test_la_mort_d_un_amoureux_est_un_chagrin(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    s["amoureux"] = ["A", "B"]
    s["joueurs"]["A"]["amoureux"] = s["joueurs"]["B"]["amoureux"] = True
    tuer(s, "A", "est dévoré par les loups", "loups")
    assert [m["genre"] for m in s["morts"]] == ["loups", "chagrin"]


def test_chiffres_cles(faire_partie):
    s = faire_partie({"A": "loup", "B": "loup", "C": "villageois", "D": "villageois", "E": "villageois"})
    s["jour"] = 2
    s["phase"] = "nuit"
    tuer(s, "C", "est dévoré par les loups", "loups")
    s["phase"] = "conseil"
    tuer(s, "A", "est éliminé par le village", "village")
    tuer(s, "D", "est éliminé par le village", "village")
    c = chiffres(s)
    assert c["Nuits"] == 3 and c["Morts"] == 3 and c["Dévorés par les loups"] == 1
    assert c["Loups démasqués"] == 1 and c["Innocents condamnés"] == 1 and c["Survivants"] == 2


def test_distinctions(faire_partie):
    s = faire_partie({"A": "loup", "B": "chasseur", "C": "villageois", "D": "villageois"})
    s["jour"] = 1
    s["phase"] = "conseil"
    tuer(s, "C", "est éliminé par le village", "village")
    tuer(s, "A", "est abattu par le chasseur B", "tir")
    titres = [t for _, t, _ in bilan_partie(s)["distinctions"]]
    assert titres[0] == "Première victime"
    assert {"Erreur judiciaire", "Dernière balle", "Loup le plus discret"} <= set(titres)


def test_le_loup_survivant_est_le_plus_discret(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    texte = [x for _, t, x in bilan_partie(s)["distinctions"] if t == "Loup le plus discret"]
    assert texte == ["A a survécu jusqu'au bout."]


def test_frise_groupe_les_morts_par_nuit_et_par_jour(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois", "E": "villageois"})
    s["jour"], s["phase"] = 1, "nuit"
    tuer(s, "B", "est dévoré par les loups", "loups")
    s["phase"] = "conseil"
    tuer(s, "C", "est éliminé par le village", "village")
    enregistrer_condamne(s, "C")
    assert [t for t, _ in bilan_partie(s)["frise"]] == ["🌙 Nuit 1", "☀️ Jour 1"]


def test_bilan_d_une_ancienne_partie_sans_morts_enregistrees(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    s.pop("morts")
    assert bilan_partie(s)["frise"] == []
