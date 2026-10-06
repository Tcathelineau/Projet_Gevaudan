import random
import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outils"))

import simuler_equilibre as sim  # noqa: E402
from loup_garou.roles import ROLES  # noqa: E402


def test_les_parties_automatiques_vont_au_bout_avec_tous_les_roles():
    cles = [c for c in ROLES if c not in ("loup", "villageois", "frere")]
    compo = sim.composer(18, 3, {c: ROLES[c].lot for c in cles})
    assert compo is not None
    rng = random.Random(1)
    random.seed(1)
    issues = {sim.jouer(compo, None, rng, .6, .1)[0] for _ in range(60)}
    assert issues <= {"village", "loups", "autre"} and len(issues) >= 2


def test_chaque_role_se_joue_seul():
    rng = random.Random(2)
    for cle, role in ROLES.items():
        if cle in ("loup", "villageois"):
            continue
        compo = sim.composer(12, 2, {cle: role.lot})
        for _ in range(15):
            issue, votes, touches, evenements = sim.jouer(compo, None, rng, .6, .1)
            assert issue in ("village", "loups", "autre") and 0 <= touches <= votes and evenements >= 0


def test_la_regression_retrouve_un_effet_connu():
    # Un loup de plus doit coûter cher au village : sinon le simulateur ou l'ajustement est cassé.
    beta = sim.ajuster(
        __import__("numpy").array([[1, 0], [1, 1], [1, 0], [1, 1]], float),
        __import__("numpy").array([100] * 4, float), __import__("numpy").array([70, 30, 72, 28], float), 1e-6,
    )
    assert beta[1] < -1
