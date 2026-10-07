import copy

from loup_garou.moteur.migrations import VERSION, migrer
from loup_garou.moteur.partie import nouvelle_partie
from loup_garou.roles import ROLES


def ancienne_sauvegarde():
    """Une partie telle que l'écrivait la première version de l'application : sans version ni clés récentes."""
    s = nouvelle_partie(list("ABCDE"), {"loup": 1, "voyante": 1, "sorciere": 1, "villageois": 2})
    for cle in ("version", "morts", "composition", "options", "servante_nuit", "double_victime", "condamnes",
                "juge_utilise", "second_vote", "tirs_en_attente", "morts_tir", "retour_tir", "instantanes",
                "protege_nuit", "mentor_enfant"):
        s.pop(cle, None)
    return s


def test_une_ancienne_sauvegarde_recoit_toutes_les_cles():
    s = migrer(ancienne_sauvegarde())
    assert s["version"] == VERSION
    assert s["morts"] == [] and s["tirs_en_attente"] == [] and s["double_victime"] is False
    assert s["options"]["potions_sorciere"] == 1
    for role in ROLES.values():
        for cle in role.etat_initial:
            assert cle in s, cle


def test_la_composition_est_reconstituee():
    s = migrer(ancienne_sauvegarde())
    assert s["composition"] == {"loup": 1, "voyante": 1, "sorciere": 1, "villageois": 2}


def test_la_migration_garde_les_valeurs_existantes():
    s = ancienne_sauvegarde()
    s["options"] = {"cadence_voyante": 3}
    s["maire"] = "B"
    s = migrer(s)
    assert s["options"]["cadence_voyante"] == 3 and s["options"]["maire_depart"] is True
    assert s["maire"] == "B"


def test_la_migration_est_idempotente():
    une_fois = migrer(ancienne_sauvegarde())
    deux_fois = migrer(copy.deepcopy(une_fois))
    assert une_fois == deux_fois


def test_les_instantanes_sont_migres_aussi():
    s = ancienne_sauvegarde()
    s["instantanes"] = [{"id": "nuit_0", "libelle": "x", "etat": ancienne_sauvegarde()}]
    s = migrer(s)
    assert "morts" in s["instantanes"][0]["etat"]


def test_une_partie_neuve_est_deja_a_la_version_courante():
    assert nouvelle_partie(["A", "B"], {"loup": 1, "villageois": 1})["version"] == VERSION
