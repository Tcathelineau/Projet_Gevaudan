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


def _creer_partie(nb_joueurs=18, nb_loups=2, sans=()):
    at = _app()
    assert not at.exception
    at.button(key="accueil_btn_nouvelle").click().run()
    for c in at.checkbox:
        c.check()
    for c in at.checkbox:
        if c.key in sans:
            c.uncheck()
    at.number_input[0].set_value(nb_joueurs)
    at.number_input[1].set_value(nb_loups)
    at.run()
    [b for b in at.button if b.label.startswith("Suivant")][0].click().run()
    for i, t in enumerate(at.text_input):
        t.set_value(f"J{i + 1}")
    [b for b in at.button if b.label == "Distribuer les rôles"][0].click().run()
    assert not at.exception
    assert "partie" in at.session_state, [e.value for e in at.error]
    return at.session_state["partie"]


def test_accueil_et_historique_s_affichent():
    at = _app()
    assert not at.exception
    at.session_state["ecran"] = "historique"
    assert not at.run().exception


# Deux tables qui, à elles deux, font jouer tous les rôles (les 18 joueurs ne tiennent pas avec tout coché).
TABLES = [
    pytest.param(("n_frere",), 7, id="sans_freres"),
    pytest.param(("n_soeur", "n_voleur", "n_loup_blanc", "n_chien_loup"), 11, id="avec_freres"),
]


@pytest.mark.parametrize("sans, graine", TABLES)
def test_partie_complete_jusqu_a_la_fin(sans, graine):
    rng = random.Random(graine)
    at = _app(_creer_partie(sans=sans))
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


def _conseil(roles, **etat):
    """Partie au conseil du jour 1, aux rôles imposés."""
    from loup_garou.moteur.partie import nouvelle_partie

    composition = {}
    for role in roles.values():
        composition[role] = composition.get(role, 0) + 1
    s = nouvelle_partie(list(roles), composition)
    for nom, role in roles.items():
        s["joueurs"][nom]["role"] = role
    s["loups"] = [n for n, r in roles.items() if r in ("loup", "louveteau")]
    s.update(jour=1, phase="conseil", **etat)
    return s


def _voter(at, nom, cle, bouton="valider_vote"):
    at.button(key=f"pick_vote_{cle}_{nom}").click().run()
    at.button(key=bouton).click().run()
    return at


def _nuit_servante(roles, condamne):
    """Nuit 2, au tour de la servante C ; le village a éliminé `condamne` au jour 1."""
    from loup_garou.moteur.partie import enregistrer_condamne, tuer

    s = _conseil(roles)
    s["jour"] = 1
    tuer(s, condamne, "est éliminé par le village")
    enregistrer_condamne(s, condamne)
    s.update(jour=2, phase="nuit", ordre_nuit=["C"], tour=0, devoile=True, transfert=True)
    return s


def test_la_servante_reprend_le_role_du_condamne_de_nuit():
    roles = {"A": "loup", "B": "loup", "C": "servante", "D": "villageois", "E": "villageois", "F": "villageois"}
    at = _app(_nuit_servante(roles, "B"))
    assert not at.exception
    at.button(key="pick_serv_2_0_B").click().run()
    at.run()  # st.rerun laisse l'arbre périmé : on le rafraîchit
    assert not at.exception
    s = at.session_state["partie"]
    assert s["joueurs"]["C"]["role"] == "loup" and "C" in s["loups"]
    assert s["servante_nuit"] == {"servante": "C", "mort": "B"}
    assert "nouvelle carte" in " ".join(m.value for m in at.markdown)
    at.button(key="fin_2_0").click().run()
    s = at.session_state["partie"]
    assert s["phase"] == "reveil"
    at.run()
    texte = " ".join(m.value for m in at.markdown)
    assert "La servante dévouée est intervenue" in texte and "C</div>" in texte


def test_la_servante_peut_ne_rien_faire():
    roles = {"A": "loup", "B": "villageois", "C": "servante", "D": "villageois", "E": "villageois"}
    at = _app(_nuit_servante(roles, "B"))
    at.button(key="servante_rien_2_0").click().run()
    s = at.session_state["partie"]
    assert s["joueurs"]["C"]["role"] == "servante" and s["phase"] == "reveil"
    at.run()
    assert "La servante dévouée est intervenue" not in " ".join(m.value for m in at.markdown)


def test_la_servante_n_a_rien_a_reprendre_sans_condamne_la_veille():
    roles = {"A": "loup", "B": "villageois", "C": "servante", "D": "villageois", "E": "villageois"}
    s = _nuit_servante(roles, "B")
    s["condamnes"] = None
    at = _app(s)
    assert not at.exception
    assert not any((b.key or "").startswith("pick_serv") for b in at.button)
    assert any(b.key == "fin_2_0" for b in at.button)


def test_le_juge_begue_declenche_un_second_vote():
    roles = {"A": "loup", "B": "villageois", "C": "juge_begue", "D": "villageois", "E": "villageois", "F": "villageois"}
    at = _voter(_app(_conseil(roles, second_vote=1)), "B", 1)
    assert not at.exception
    assert not any(b.label == "La nuit tombe" for b in at.button)
    at = _voter(at, "D", "1b", "valider_vote2")
    assert not at.exception
    s = at.session_state["partie"]
    assert not s["joueurs"]["B"]["vivant"] and not s["joueurs"]["D"]["vivant"]
    assert any(b.label == "La nuit tombe" for b in at.button)


def test_sans_juge_un_seul_vote():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois", "E": "villageois"}
    at = _voter(_app(_conseil(roles)), "B", 1)
    assert any(b.label == "La nuit tombe" for b in at.button)


def test_le_bruitage_suit_la_phase_et_se_coupe():
    roles = {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    nuit = _conseil(roles)
    nuit.update(phase="nuit", jour=1)
    at = _app(nuit)
    assert len(at.get("audio")) == 1
    at.checkbox(key="sons_on").uncheck().run()
    assert len(at.get("audio")) == 0
    assert len(_app(_conseil(roles)).get("audio")) == 0
