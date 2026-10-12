import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outils"))

from verifier_changelog import journal_manquant  # noqa: E402


def test_une_pr_de_code_sans_journal_est_refusee():
    assert journal_manquant(["src/loup_garou/app.py"])
    assert journal_manquant(["tests/test_partie.py", "README.md"])


def test_une_pr_de_code_avec_journal_passe():
    assert not journal_manquant(["src/loup_garou/app.py", "CHANGELOG.md"])


def test_une_pr_sans_code_n_a_pas_besoin_du_journal():
    assert not journal_manquant(["README.md"])
    assert not journal_manquant([])
