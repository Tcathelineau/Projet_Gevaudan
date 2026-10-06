from loup_garou.moteur.statistiques import a_gagne, statistiques


def partie(issue, **joueurs):
    return {"issue": issue, "journal": [], "joueurs": {
        nom: {"role": role, "vivant": vivant, "amoureux": False} for nom, (role, vivant) in joueurs.items()
    }}


VILLAGE = "Le village a gagné : tous les loups sont morts."
LOUPS = "Les loups ont gagné : ils sont plus nombreux que les villageois."


def test_victoires_par_camp_et_tailles():
    parties = [
        partie(VILLAGE, A=("loup", False), B=("villageois", True), C=("voyante", True)),
        partie(LOUPS, A=("loup", True), B=("villageois", False), C=("voyante", False)),
        partie(LOUPS, A=("loup", True), B=("villageois", True), C=("voyante", False)),
    ]
    stats = statistiques(parties)
    assert stats["total"] == 3 and stats["joueurs"] == 9
    assert stats["victoires"] == {"village": 1, "loups": 2}
    assert stats["tailles"][0][:2] == ("5 à 8 joueurs", 3) and round(stats["tailles"][0][2], 2) == 0.33
    assert stats["tailles"][1][1] == 0 and stats["tailles"][1][2] is None


def test_fiche_par_role():
    parties = [
        partie(VILLAGE, A=("loup", False), B=("voyante", True)),
        partie(LOUPS, A=("loup", True), B=("voyante", False)),
    ]
    fiches = {cle: (n, v, s) for cle, n, v, s in statistiques(parties)["roles"]}
    assert fiches["voyante"] == (2, 0.5, 0.5) and fiches["loup"] == (2, 0.5, 0.5)


def test_les_roles_inconnus_des_anciennes_archives_sont_ignores():
    stats = statistiques([partie(VILLAGE, A=("role_disparu", True), B=("loup", False))])
    assert [cle for cle, *_ in stats["roles"]] == ["loup"]


def test_qui_a_gagne():
    assert a_gagne("village", {"role": "voyante"}) and not a_gagne("village", {"role": "loup"})
    assert a_gagne("loups", {"role": "chien_loup", "camp_choisi": "loups"})
    assert not a_gagne("village", {"role": "chien_loup", "camp_choisi": "loups"})
    assert a_gagne("couple", {"role": "villageois", "amoureux": True})
    assert a_gagne("loupblanc", {"role": "loup_blanc"}) and not a_gagne("loupblanc", {"role": "loup"})
    assert not a_gagne("autre", {"role": "loup"})
