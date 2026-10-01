import json
import os

from loup_garou.config import HISTORIQUE_DIR, SAVE_FILE
from loup_garou.moteur.persistance import (
    archiver_partie, clear_save, date_partie, gagnant_partie, load_game, lister_historique, save_game,
)


def test_load_game_sans_sauvegarde():
    assert load_game() is None


def test_sauvegarde_aller_retour_avec_accents():
    s = {"joueurs": {"Élodie": {"role": "sorciere"}}, "jour": 3}
    save_game(s)
    assert load_game() == s


def test_clear_save_supprime_le_fichier_et_tolere_son_absence():
    save_game({"jour": 1})
    clear_save()
    assert not os.path.exists(SAVE_FILE)
    clear_save()


def partie_terminee():
    return {"joueurs": {"A": {"role": "loup"}}, "journal": [{"jour": 1, "moment": "fin", "texte": "Fin."}]}


def test_archiver_ecrit_un_fichier_et_une_seule_fois():
    s = partie_terminee()
    archiver_partie(s, "Le village a gagné : tous les loups sont morts.")
    archiver_partie(s, "autre issue ignorée")
    fichiers = os.listdir(HISTORIQUE_DIR)
    assert len(fichiers) == 1 and fichiers[0].startswith("partie_")
    with open(os.path.join(HISTORIQUE_DIR, fichiers[0]), encoding="utf-8") as f:
        contenu = json.load(f)
    assert contenu["issue"].startswith("Le village a gagné")
    assert contenu["joueurs"] == s["joueurs"] and contenu["journal"] == s["journal"]


def test_lister_historique_ignore_les_fichiers_illisibles_ou_incomplets():
    os.makedirs(HISTORIQUE_DIR)
    with open(os.path.join(HISTORIQUE_DIR, "partie_20200101_000000.json"), "w", encoding="utf-8") as f:
        f.write("pas du json")
    with open(os.path.join(HISTORIQUE_DIR, "partie_20200102_000000.json"), "w", encoding="utf-8") as f:
        json.dump({"issue": "x"}, f)
    assert lister_historique() == []


def test_lister_historique_du_plus_recent_au_plus_ancien():
    os.makedirs(HISTORIQUE_DIR)
    for nom in ("partie_20200101_000000.json", "partie_20210101_000000.json"):
        with open(os.path.join(HISTORIQUE_DIR, nom), "w", encoding="utf-8") as f:
            json.dump({"date": nom, "issue": "x", "joueurs": {}, "journal": []}, f)
    assert [p["date"] for p in lister_historique()] == ["partie_20210101_000000.json", "partie_20200101_000000.json"]


def test_date_partie():
    assert date_partie({"date": "2026-09-30T18:20:51"}) == "30/09/2026 à 18:20"
    assert date_partie({}) == "date inconnue"
    assert date_partie({"date": "n'importe quoi"}) == "date inconnue"


def test_gagnant_partie():
    assert gagnant_partie("Le village a gagné : tous les loups sont morts.")[0] == "village"
    assert gagnant_partie("Les loups ont gagné : ils sont plus nombreux que les villageois.")[0] == "loups"
    assert gagnant_partie("Les amoureux l'emportent : ils sont les deux derniers survivants.")[0] == "couple"
    assert gagnant_partie("Zoé (Loup Blanc) l'emporte seul.")[0] == "loupblanc"
    assert gagnant_partie("Partie abandonnée")[0] == "autre"
