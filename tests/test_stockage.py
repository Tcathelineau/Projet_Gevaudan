"""Stockage SQL (SQLite en local, Postgres si TEST_DATABASE_URL est fourni) : plusieurs parties, archives par code, ménage."""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from loup_garou.moteur import stockage as module_stockage
from loup_garou.moteur.codes import afficher_code, nouveau_code, normaliser_code
from loup_garou.moteur.migrations import VERSION, migrer
from loup_garou.moteur.partie import nouvelle_partie
from loup_garou.moteur.persistance import (
    archiver_partie, clear_save, lister_historique, load_game, load_joueurs, load_preferences, maj_preferences,
    multi_parties, resume_sauvegarde, save_game,
)


def _urls():
    urls = ["sqlite"]
    if os.environ.get("TEST_DATABASE_URL"):
        urls.append("externe")
    return urls


@pytest.fixture(params=_urls())
def base(request, tmp_path, monkeypatch):
    """Une base vide : SQLite dans un dossier temporaire, ou la base Postgres de la CI (nettoyée avant et après)."""
    url = f"sqlite:///{tmp_path}/test.db" if request.param == "sqlite" else os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", url)
    module_stockage._stockage_sql.cache_clear()
    sql = module_stockage.stockage()
    with sql.engine.begin() as c:
        c.execute(sql.parties.delete())
        c.execute(sql.archives.delete())
    yield sql
    with sql.engine.begin() as c:
        c.execute(sql.parties.delete())
        c.execute(sql.archives.delete())
    module_stockage._stockage_sql.cache_clear()


def _partie():
    return nouvelle_partie(["A", "B", "C", "D"], {"loup": 1, "villageois": 3})


def test_sans_base_les_fichiers_servent_une_seule_partie():
    assert not multi_parties()


def test_avec_une_base_plusieurs_parties_cohabitent(base):
    assert multi_parties()
    a, b = _partie(), _partie()
    b["jour"] = 3
    save_game(a)
    save_game(b)
    assert load_game(a["code"])["jour"] == 0
    assert load_game(b["code"])["jour"] == 3
    clear_save(a["code"])
    assert load_game(a["code"]) is None and load_game(b["code"])["jour"] == 3


def test_une_partie_se_met_a_jour_sans_doublon(base):
    s = _partie()
    save_game(s)
    s["jour"] = 2
    save_game(s)
    assert load_game(s["code"])["jour"] == 2
    with base.engine.connect() as c:
        assert len(c.execute(base.parties.select()).all()) == 1


def test_sans_code_ou_avec_un_code_inconnu_rien_n_est_repris(base):
    save_game(_partie())
    assert load_game() is None
    assert load_game(nouveau_code()) is None


def test_une_partie_sans_code_ne_peut_pas_etre_rangee_en_base(base):
    with pytest.raises(ValueError):
        save_game({"joueurs": {}, "phase": "nuit", "jour": 0})


def test_un_contenu_corrompu_est_mis_de_cote_sous_un_autre_code(base):
    code = nouveau_code()
    with base.engine.begin() as c:
        c.execute(base.parties.insert().values(code=code, etat="{ pas du json", maj=datetime.now(timezone.utc).isoformat()))
    assert load_game(code) is None
    with base.engine.connect() as c:
        assert [r.code for r in c.execute(base.parties.select())] == [f"{code}.corrompue"]


def test_resume_de_la_sauvegarde_donne_une_date_au_fuseau_local(base):
    s = _partie()
    save_game(s)
    partie, texte, date = resume_sauvegarde(s["code"])
    assert partie["code"] == s["code"] and "Nuit 0" in texte and "/" in date


def test_les_archives_ne_se_voient_qu_avec_le_code_de_la_partie(base):
    a, b = _partie(), _partie()
    for s in (a, b):
        archiver_partie(s, "Le village a gagné : tous les loups sont morts.")
        assert s["archive"] == "la base de données"
    archiver_partie(a, "ignorée : déjà archivée")
    assert len(lister_historique(a["code"])) == 1 and len(lister_historique(b["code"])) == 1
    assert lister_historique() == []  # pas de code : on ne montre pas les parties des autres groupes


def test_preferences_et_noms_ne_sont_pas_partages_entre_groupes(base):
    maj_preferences(son={"musique_on": True})
    assert load_preferences() == {} and load_joueurs() == []


def test_le_menage_supprime_les_parties_et_archives_trop_anciennes(base):
    vieux = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat(timespec="seconds")
    ancien = nouveau_code()
    with base.engine.begin() as c:
        c.execute(base.parties.insert().values(code=ancien, etat="{}", maj=vieux))
        c.execute(base.archives.insert().values(code=ancien, date=vieux, donnees="{}"))
    save_game(_partie())  # une nouvelle partie déclenche le ménage
    with base.engine.connect() as c:
        assert ancien not in [r.code for r in c.execute(base.parties.select())]
        assert c.execute(base.archives.select()).all() == []


def test_les_adresses_des_hebergeurs_sont_normalisees():
    from loup_garou.moteur.stockage import StockageSQL

    assert StockageSQL.normaliser_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert StockageSQL.normaliser_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert StockageSQL.normaliser_url("sqlite:///x.db") == "sqlite:///x.db"


# --- codes de partie ---------------------------------------------------------

def test_un_code_se_normalise_et_s_affiche():
    code = nouveau_code()
    assert normaliser_code(afficher_code(code).lower()) == code
    assert afficher_code("K7M2QX9P") == "K7M2-QX9P"
    assert normaliser_code(" k7m2-qx9p ") == "K7M2QX9P"
    for invalide in (None, "", "K7M2", "K7M2QX9P1", "K7M2QX9O", 12345678):  # trop court, trop long, O interdit, pas du texte
        assert normaliser_code(invalide) is None


def test_chaque_nouvelle_partie_a_son_code():
    assert len({_partie()["code"] for _ in range(20)}) == 20
    assert _partie()["version"] == VERSION


def test_la_migration_donne_un_code_aux_anciennes_parties_et_a_leurs_instantanes():
    s = {"joueurs": {"A": {"role": "loup", "vivant": True, "amoureux": False}}, "phase": "nuit", "jour": 1, "version": 1,
         "instantanes": [{"id": "nuit_1", "etat": {"jour": 1}}], "options": {}, "cartes_milieu": [], "journal": []}
    migrer(s)
    assert s["version"] == VERSION and normaliser_code(s["code"]) == s["code"]
    assert s["instantanes"][0]["etat"]["code"] == s["code"]
    code = s["code"]
    migrer(s)  # idempotent
    assert s["code"] == code


def test_les_sauvegardes_d_avant_les_codes_se_reprennent_en_fichiers():
    ancienne = json.dumps({"joueurs": {"A": {"role": "loup", "vivant": True, "amoureux": False}}, "phase": "nuit", "jour": 0, "version": 1})
    with open("save.json", "w", encoding="utf-8") as f:
        f.write(ancienne)
    s = load_game()
    assert s is not None and normaliser_code(s["code"])
