from loup_garou.moteur.bilan import coulisses


def e(jour, moment, texte):
    return {"jour": jour, "moment": moment, "texte": texte}


JOUEURS = {
    "Julie": {"role": "villageois", "vivant": False, "amoureux": True},
    "Bob": {"role": "loup", "vivant": False, "amoureux": True},
    "Chloé": {"role": "sorciere", "vivant": True, "amoureux": False},
}
JOURNAL = [
    e(0, "debut", "3 joueurs. Paquet : Loup-Garou ×1."),
    e(0, "nuit", "Cupidon Zoé lie Julie et Bob."),
    e(1, "nuit", "La voyante Léa sonde Bob : Loup-Garou."),
    e(1, "nuit", "Bob (Loup-Garou) désigne Julie."),
    e(1, "nuit", "La sorcière Chloé utilise une potion de soin."),
    e(1, "nuit", "Julie était la cible des loups mais est sauvé par la potion de la sorcière."),
    e(2, "nuit", "Le salvateur Max protège Chloé."),
    e(2, "nuit", "Le Loup Blanc Rex dévore Bob."),
    e(2, "nuit", "Rex (Loup Blanc) désigne Chloé."),
    e(2, "conseil", "Bob (Loup-Garou) est éliminé par le village."),
    e(2, "conseil", "Julie (Villageois) meurt de chagrin (amoureux)."),
    e(3, "fin", "Le village a gagné."),
]


def themes():
    return {titre: lignes for _, titre, lignes in coulisses(JOUEURS, JOURNAL)}


def test_le_couple_et_ses_roles_sont_listes_en_premier():
    t = coulisses(JOUEURS, JOURNAL)
    assert t[0][1] == "Les amoureux"
    assert t[0][2][0] == "Le couple : Julie (Villageois), Bob (Loup-Garou) : couple mixte, un camp à part."
    assert "Nuit 0 : Cupidon Zoé lie Julie et Bob." in t[0][2]


def test_un_prenom_en_lie_ne_passe_pas_pour_un_couple():
    # « Julie » contient « lie » : seule la forme « X lie Y » doit compter
    assert "Nuit 1 : Julie était la cible des loups mais est sauvé par la potion de la sorcière." in themes()["Les potions"]
    assert not any("cible des loups" in ligne for ligne in themes()["Les amoureux"])


def test_potions_protections_et_visions():
    t = themes()
    assert "Nuit 1 : La sorcière Chloé utilise une potion de soin." in t["Les potions"]
    assert t["Les protections"] == ["Nuit 2 : Le salvateur Max protège Chloé."]
    assert t["Les visions"] == ["Nuit 1 : La voyante Léa sonde Bob : Loup-Garou."]


def test_les_votes_des_loups_ne_polluent_pas_le_theme_du_loup_blanc():
    assert themes()["Le Loup Blanc"] == ["Nuit 2 : Le Loup Blanc Rex dévore Bob."]


def test_le_chagrin_est_dans_les_amoureux_et_la_mise_en_place_est_exclue():
    t = themes()
    assert "Jour 2 : Julie (Villageois) meurt de chagrin (amoureux)." in t["Les amoureux"]
    assert not any("Paquet" in ligne for lignes in t.values() for ligne in lignes)


def test_themes_vides_omis():
    assert coulisses({"A": {"role": "villageois", "vivant": True, "amoureux": False}}, [e(1, "nuit", "A dort.")]) == []
