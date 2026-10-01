import pytest

from loup_garou.moteur.partie import nouvelle_partie
from loup_garou.roles import ROLES


@pytest.fixture(autouse=True)
def dossier_isole(tmp_path, monkeypatch):
    """save.json et historique/ sont relatifs au dossier courant : chaque test travaille dans un dossier vide."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def faire_partie():
    """faire_partie({"Alice": "loup", "Bob": "villageois"}, **options) : partie aux rôles imposés."""

    def _faire(roles_par_nom, **options):
        noms = list(roles_par_nom)
        composition = {}
        for role in roles_par_nom.values():
            composition[role] = composition.get(role, 0) + 1
        s = nouvelle_partie(noms, composition, options)
        for nom, role in roles_par_nom.items():
            s["joueurs"][nom]["role"] = role
        s["loups"] = [n for n, r in roles_par_nom.items() if ROLES[r].camp == "loups"]
        return s

    return _faire
