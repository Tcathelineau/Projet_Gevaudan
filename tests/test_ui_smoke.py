"""Parcours de l'interface avec le banc d'essai de Streamlit (sans navigateur).

Joue une partie complète en cliquant au hasard (graine fixe) : détecte les exceptions
d'affichage et les écrans sans issue après un changement dans ui/.
"""

import random
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

SRC = str(Path(__file__).resolve().parent.parent / "src")
ENTREE = str(Path(SRC) / "loup_garou_app.py")


def _app(partie=None):
    sys.path.insert(0, SRC)
    at = AppTest.from_file(ENTREE, default_timeout=60)
    if partie is not None:
        at.session_state["partie"] = partie
    return at.run()


def _creer_partie(nb_joueurs=14, nb_loups=3):
    at = _app()
    assert not at.exception
    at.button(key="accueil_btn_nouvelle").click().run()
    for c in at.checkbox:
        c.check()
    at.number_input[0].set_value(nb_joueurs)
    at.number_input[1].set_value(nb_loups)
    at.run()
    [b for b in at.button if b.label.startswith("Suivant")][0].click().run()
    for i, t in enumerate(at.text_input):
        t.set_value(f"J{i + 1}")
    at.run()
    [b for b in at.button if b.label == "Distribuer les rôles"][0].click().run()
    assert not at.exception
    return at.session_state["partie"]


def test_accueil_et_historique_s_affichent():
    at = _app()
    assert not at.exception
    at.session_state["ecran"] = "historique"
    assert not at.run().exception


def test_partie_complete_jusqu_a_la_fin():
    rng = random.Random(7)
    at = _app(_creer_partie())
    ignores = ("Menu", "Recharger")
    for _ in range(1500):
        assert not at.exception, at.exception
        s = at.session_state["partie"]
        if s["phase"] == "fin":
            break
        boutons = [
            b for b in at.button
            if not b.disabled and b.key != "bouton_option"
            and not (b.key or "").startswith("recharg")
            and not any(m in b.label for m in ignores)
        ]
        formulaires = [
            b for b in boutons if (b.key or "").startswith("FormSubmitter") and "Retour" not in b.label
        ]
        boutons = formulaires or boutons
        assert boutons, f"écran sans issue en phase {s['phase']}"
        for r in at.radio:
            if rng.random() < 0.5:
                r.set_value(rng.choice(r.options))
        rng.choice(boutons).click().run()
    else:
        pytest.fail("la partie ne se termine pas en 1500 clics")
    assert at.session_state["partie"]["phase"] == "fin"


def test_jauges_d_equilibre_dans_la_composition():
    at = _app()
    at.button(key="accueil_btn_nouvelle").click().run()
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    assert "Équilibre de la partie" in texte and "jauge-repere" in texte
    at.checkbox(key="n_voyante").check().run()
    assert not at.exception


def test_page_documentation_liste_tous_les_roles():
    from loup_garou.roles import ROLES

    at = _app()
    at.button(key="accueil_btn_documentation").click().run()
    assert not at.exception
    texte = " ".join(m.value for m in at.markdown)
    for role in ROLES.values():
        assert role.nom in texte
    at.button(key="retour_menu_documentation").click().run()
    assert not at.exception
    assert any(b.key == "accueil_btn_nouvelle" for b in at.button)
