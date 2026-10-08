import os

from datetime import datetime

from loup_garou.config import HISTORIQUE_DIR
from loup_garou.moteur.partie import (
    camp, composition_recommandee, condamnes_de_la_veille, enregistrer_condamne, fin_de_tour, nouvelle_partie,
    resoudre_nuit, servante_prend_role, terminer_partie, tirer_echeance, tuer, vainqueur, victimes_loups, vivants,
    bouc_emissaire, epargner_idiot, ours_grogne, voisins_vivants,
)
from loup_garou.roles import ROLES_SPECIAUX


# --- nouvelle_partie -------------------------------------------------------

def test_nouvelle_partie_distribue_un_role_par_joueur():
    s = nouvelle_partie(["A", "B", "C", "D"], {"loup": 1, "villageois": 3})
    roles = sorted(d["role"] for d in s["joueurs"].values())
    assert roles == ["loup", "villageois", "villageois", "villageois"]
    assert s["phase"] == "nuit" and s["jour"] == 0
    assert s["loups"] == [n for n, d in s["joueurs"].items() if d["role"] == "loup"]
    assert all(d["vivant"] and not d["amoureux"] for d in s["joueurs"].values())


def test_nouvelle_partie_garde_les_cartes_en_trop_au_milieu():
    s = nouvelle_partie(["A", "B"], {"loup": 1, "villageois": 3})
    assert len(s["cartes_milieu"]) == 2


def test_nouvelle_partie_charge_l_etat_initial_des_roles():
    s = nouvelle_partie(["A", "B", "C"], {"loup": 1, "sorciere": 1, "salvateur": 1})
    assert s["protege_nuit"] is None and s["soin_sorciere"] is False and s["cible_poison"] is None


def test_nouvelle_partie_options_par_defaut_et_potions():
    s = nouvelle_partie(["A", "B"], {"loup": 1, "sorciere": 1})
    assert s["potions_sorciere"] == 1 and s["potions_mort_sorciere"] == 0
    s = nouvelle_partie(["A", "B"], {"loup": 1, "sorciere": 1}, {"potions_sorciere": 3, "potions_mort": 2})
    assert s["potions_sorciere"] == 3 and s["potions_mort_sorciere"] == 2


def test_nouvelle_partie_couple_au_hasard_sans_cupidon():
    s = nouvelle_partie(list("ABCDEF"), {"loup": 1, "villageois": 5}, {"couple_hasard": True})
    assert len(s["amoureux"]) == 2
    assert all(s["joueurs"][n]["amoureux"] for n in s["amoureux"])


def test_nouvelle_partie_trouple():
    s = nouvelle_partie(list("ABCDEF"), {"loup": 1, "villageois": 5}, {"couple_hasard": True, "trouple": True})
    assert len(s["amoureux"]) == 3


def test_nouvelle_partie_journalise_le_depart():
    s = nouvelle_partie(["A", "B"], {"loup": 1, "villageois": 1})
    assert [e["moment"] for e in s["journal"]] == ["debut", "debut"]


# --- vivants / camp / tuer -------------------------------------------------

def test_vivants(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    s["joueurs"]["B"]["vivant"] = False
    assert vivants(s) == ["A", "C"]


def test_camp_par_role_et_camp_choisi(faire_partie):
    s = faire_partie({"A": "loup", "B": "chien_loup", "C": "villageois"})
    assert camp(s, "A") == "loups" and camp(s, "C") == "village"
    assert camp(s, "B") == "village"
    s["joueurs"]["B"]["camp_choisi"] = "loups"
    assert camp(s, "B") == "loups"


def test_tuer_un_joueur(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    assert tuer(s, "B") == ["B"]
    assert not s["joueurs"]["B"]["vivant"]
    assert "B (Villageois) meurt." in s["journal"][-1]["texte"]


def test_tuer_un_mort_ou_un_inconnu_ne_fait_rien(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    tuer(s, "B")
    assert tuer(s, "B") == []
    assert tuer(s, "Fantôme") == []


def test_tuer_entraine_l_amoureux(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    s["amoureux"] = ["A", "B"]
    s["joueurs"]["A"]["amoureux"] = s["joueurs"]["B"]["amoureux"] = True
    assert tuer(s, "A") == ["A", "B"]
    assert vivants(s) == ["C"]


def test_tuer_un_trouple_entraine_les_deux_autres(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"})
    s["amoureux"] = ["A", "B", "C"]
    for n in "ABC":
        s["joueurs"][n]["amoureux"] = True
    assert tuer(s, "B") == ["B", "A", "C"]


def test_tuer_le_maire_le_retire_et_garde_la_trace(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    s["maire"] = "B"
    tuer(s, "B")
    assert s["maire"] is None and s["dernier_maire"] == "B"


def test_tuer_le_chasseur_declenche_un_tir(faire_partie):
    s = faire_partie({"A": "loup", "B": "chasseur", "C": "villageois"})
    tuer(s, "B")
    assert s["tirs_en_attente"] == ["B"]


def test_mort_du_mentor_transforme_l_enfant_sauvage(faire_partie):
    s = faire_partie({"A": "loup", "B": "enfant_sauvage", "C": "villageois", "D": "villageois"})
    s["mentor_enfant"] = "C"
    tuer(s, "C")
    assert s["joueurs"]["B"]["role"] == "loup"
    assert "B" in s["loups"] and camp(s, "B") == "loups"
    assert s["mentor_enfant"] is None


def test_mort_d_un_autre_joueur_laisse_l_enfant_sauvage(faire_partie):
    s = faire_partie({"A": "loup", "B": "enfant_sauvage", "C": "villageois", "D": "villageois"})
    s["mentor_enfant"] = "C"
    tuer(s, "D")
    assert s["joueurs"]["B"]["role"] == "enfant_sauvage"


# --- vainqueur -------------------------------------------------------------

def test_pas_de_vainqueur_en_debut_de_partie(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"})
    assert vainqueur(s) is None


def test_le_village_gagne_sans_loup(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    tuer(s, "A")
    assert vainqueur(s).startswith("Le village a gagné")


def test_les_loups_gagnent_quand_ils_sont_plus_nombreux(faire_partie):
    s = faire_partie({"A": "loup", "B": "loup", "C": "villageois"})
    assert vainqueur(s).startswith("Les loups ont gagné")


def test_egalite_la_partie_continue_sauf_maire_loup(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    assert vainqueur(s) is None
    s["maire"] = "B"
    assert vainqueur(s) is None
    s["maire"] = "A"
    assert "maire" in vainqueur(s)


def test_egalite_les_loups_gagnent_si_l_option_maire_est_desactivee(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"}, maire_depart=False)
    assert vainqueur(s).startswith("Les loups ont gagné")


def test_les_amoureux_gagnent_s_ils_sont_les_derniers(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    s["amoureux"] = ["A", "B"]
    s["joueurs"]["A"]["amoureux"] = s["joueurs"]["B"]["amoureux"] = True
    s["joueurs"]["C"]["vivant"] = False
    assert vainqueur(s).startswith("Les amoureux l'emportent")
    assert "deux" in vainqueur(s)


def test_le_trouple_gagne_a_trois(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"})
    s["amoureux"] = ["A", "B", "C"]
    s["joueurs"]["D"]["vivant"] = False
    assert "trois" in vainqueur(s)


def test_couple_mixte_bloque_les_victoires_des_autres_camps(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"})
    s["amoureux"] = ["A", "B"]
    # Le seul loup vivant est amoureux d'un villageois : le village ne peut pas conclure en le tuant seul.
    s["joueurs"]["D"]["vivant"] = False
    assert vainqueur(s) is None
    s["joueurs"]["C"]["vivant"] = False
    assert vainqueur(s).startswith("Les amoureux")


def test_loup_blanc_bloque_les_autres_victoires(faire_partie):
    s = faire_partie({"A": "loup_blanc", "B": "villageois", "C": "villageois"})
    assert vainqueur(s) is None
    s["joueurs"]["B"]["vivant"] = s["joueurs"]["C"]["vivant"] = False
    assert vainqueur(s) == "A (Loup Blanc) l'emporte seul."


def test_loup_blanc_et_meute_ne_peuvent_pas_conclure_ensemble(faire_partie):
    s = faire_partie({"A": "loup_blanc", "B": "loup", "C": "villageois"})
    assert vainqueur(s) is None


# --- fin_de_tour / terminer_partie ----------------------------------------

def test_fin_de_tour_passe_au_joueur_suivant():
    s = {"tour": 2, "devoile": True, "transfert": True}
    fin_de_tour(s)
    assert s == {"tour": 3, "devoile": False, "transfert": False}


def test_terminer_partie_archive_et_passe_en_phase_fin(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois"})
    terminer_partie(s, "Le village a gagné : tous les loups sont morts.")
    assert s["phase"] == "fin" and s["message_fin"].startswith("Le village")
    assert len(os.listdir(HISTORIQUE_DIR)) == 1


# --- resoudre_nuit ---------------------------------------------------------

def nuit(faire_partie, roles=None, jour=1, votes=("B",)):
    roles = roles or {"A": "loup", "B": "villageois", "C": "villageois", "D": "villageois"}
    s = faire_partie(roles)
    s["jour"] = jour
    s["votes_loups"] = list(votes)
    return s


def test_premiere_nuit_sans_mort(faire_partie):
    s = nuit(faire_partie, jour=0, votes=("B",))
    resoudre_nuit(s)
    assert s["morts_nuit"] == [] and len(vivants(s)) == 4
    assert s["phase"] == "reveil"
    assert s["instantanes"][-1]["id"] == "jour_0"


def test_les_loups_devorent_leur_victime(faire_partie):
    s = nuit(faire_partie, votes=("B", "B"))
    resoudre_nuit(s)
    assert s["morts_nuit"] == ["B"] and not s["joueurs"]["B"]["vivant"]


def test_loups_en_desaccord_personne_ne_meurt(faire_partie):
    s = nuit(faire_partie, votes=("B", "C"))
    resoudre_nuit(s)
    assert s["morts_nuit"] == [] and len(vivants(s)) == 4


def test_la_majorite_des_votes_l_emporte(faire_partie):
    s = nuit(faire_partie, votes=("B", "C", "C"))
    resoudre_nuit(s)
    assert s["morts_nuit"] == ["C"]


def test_potion_de_soin_sauve_la_victime(faire_partie):
    s = nuit(faire_partie)
    s["soin_sorciere"] = True
    resoudre_nuit(s)
    assert s["morts_nuit"] == []
    assert s["soin_sorciere"] is False


def test_la_sorcière_garde_en_memoire_la_personne_sauvee(faire_partie):
    s = nuit(faire_partie)
    s["soin_sorciere"] = True
    resoudre_nuit(s)
    assert s["sauve_par_sorciere"] == "B"
    s["jour"] = 2
    s["votes_loups"] = ["C"]
    resoudre_nuit(s)  # nuit suivante sans soin : la mémoire est remise à zéro
    assert s["sauve_par_sorciere"] is None and s["morts_nuit"] == ["C"]


def test_le_salvateur_seul_ne_compte_pas_comme_un_sauvetage_de_la_sorciere(faire_partie):
    s = nuit(faire_partie, roles={"A": "loup", "B": "villageois", "C": "salvateur", "D": "villageois"})
    s["protege_nuit"] = "B"
    resoudre_nuit(s)
    assert s["sauve_par_sorciere"] is None


def test_echeance_tiree_entre_les_deux_bornes(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"}, echeance_active=True, echeance_min=15, echeance_max=60)
    s["jour"] = 1
    debut = datetime(2026, 1, 1, 12, 0)
    for _ in range(30):
        tirer_echeance(s, debut)
        assert 15 <= s["echeance"]["minutes"] <= 60
        assert (datetime.fromisoformat(s["echeance"]["fin"]) - debut).seconds // 60 == s["echeance"]["minutes"]
        assert s["echeance"]["jour"] == 1


def test_pas_d_echeance_si_l_option_est_coupee_ou_au_premier_jour(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"})
    s["jour"] = 1
    tirer_echeance(s)
    assert s["echeance"] is None
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"}, echeance_active=True)
    tirer_echeance(s)  # jour 0
    assert s["echeance"] is None


def test_la_resolution_de_la_nuit_tire_l_echeance(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "villageois"}, echeance_active=True, echeance_min=30, echeance_max=30)
    s["jour"] = 1
    s["votes_loups"] = ["B"]
    resoudre_nuit(s)
    assert s["echeance"]["minutes"] == 30


def test_salvateur_protege_la_victime(faire_partie):
    s = nuit(faire_partie, roles={"A": "loup", "B": "villageois", "C": "salvateur", "D": "villageois"})
    s["protege_nuit"] = "B"
    resoudre_nuit(s)
    assert s["morts_nuit"] == []
    assert s["protege_nuit"] is None and s["protege_precedent"] == "B"


def test_le_poison_echappe_au_soin_et_au_salvateur(faire_partie):
    s = nuit(faire_partie, roles={"A": "loup", "B": "villageois", "C": "sorciere", "D": "salvateur"}, votes=("B",))
    s["soin_sorciere"] = True
    s["cible_poison"] = "D"
    s["protege_nuit"] = "D"
    resoudre_nuit(s)
    assert s["morts_nuit"] == ["D"]
    assert s["cible_poison"] is None


def test_le_festin_du_loup_blanc_echappe_au_soin(faire_partie):
    s = nuit(faire_partie, roles={"A": "loup", "B": "villageois", "C": "loup_blanc", "D": "loup"}, votes=("B",))
    s["soin_sorciere"] = True
    s["cible_loup_blanc"] = "D"
    resoudre_nuit(s)
    assert s["morts_nuit"] == ["D"]
    assert s["cible_loup_blanc"] is None


def test_resoudre_nuit_remet_la_nuit_a_zero(faire_partie):
    s = nuit(faire_partie)
    s["ordre_nuit"] = ["A", "B"]
    s["tour"] = 2
    s["devoile"] = True
    resoudre_nuit(s)
    assert s["ordre_nuit"] == [] and s["tour"] == 0 and s["devoile"] is False
    assert s["votes_loups"] == []


def test_morts_de_la_nuit_pas_de_journal_vide(faire_partie):
    s = nuit(faire_partie, votes=("B", "C"))
    resoudre_nuit(s)
    assert any("Personne ne meurt" in e["texte"] for e in s["journal"])


# --- composition_recommandee ----------------------------------------------

def test_composition_recommandee_un_quart_de_loups():
    loups, speciaux = composition_recommandee(12)
    assert loups == 3
    assert set(speciaux) == {r.key for r in ROLES_SPECIAUX}


def test_composition_recommandee_ne_depasse_pas_la_table():
    for nb in range(4, 20):
        loups, speciaux = composition_recommandee(nb)
        assert loups >= 1
        assert loups + sum(speciaux.values()) <= nb


def test_composition_recommandee_exclut_les_roles_non_recommandes():
    _, speciaux = composition_recommandee(14)
    for role in ROLES_SPECIAUX:
        if not role.recommande:
            assert speciaux[role.key] == 0
    assert speciaux["voyante"] == 1


# --- Louveteau ---------------------------------------------------------------

def test_victimes_loups_prend_les_plus_designes():
    assert victimes_loups(["B", "B", "C"], 1) == ["B"]
    assert victimes_loups(["B", "C"], 1) == []
    assert victimes_loups(["B", "C"], 2) == ["B", "C"]
    assert victimes_loups(["A", "A", "B", "C"], 2) == ["A"]
    assert victimes_loups(["A", "A", "B", "B", "C"], 2) == ["A", "B"]
    assert victimes_loups([], 2) == []


def test_la_mort_du_louveteau_prepare_une_double_victime(faire_partie):
    s = faire_partie({"A": "loup", "B": "louveteau", "C": "villageois", "D": "villageois", "E": "villageois"})
    assert camp(s, "B") == "loups"
    tuer(s, "B")
    assert s["double_victime"] is True


def test_la_nuit_suivante_la_meute_devore_deux_victimes(faire_partie):
    s = faire_partie({"A": "loup", "B": "louveteau", "C": "villageois", "D": "villageois", "E": "villageois"})
    tuer(s, "B")
    s["jour"] = 1
    s["votes_loups"] = ["C", "D"]
    resoudre_nuit(s)
    assert sorted(s["morts_nuit"]) == ["C", "D"]
    assert s["double_victime"] is False


def test_la_potion_ne_sauve_que_la_victime_la_plus_designee(faire_partie):
    s = faire_partie({"A": "loup", "B": "louveteau", "C": "villageois", "D": "villageois", "E": "villageois"})
    tuer(s, "B")
    s["jour"] = 1
    s["votes_loups"] = ["C", "C", "D"]
    s["soin_sorciere"] = True
    resoudre_nuit(s)
    assert s["morts_nuit"] == ["D"]


def test_le_louveteau_tue_cette_nuit_ne_double_que_la_suivante(faire_partie):
    s = faire_partie({"A": "loup", "B": "louveteau", "C": "villageois", "D": "villageois", "E": "villageois"})
    s["jour"] = 1
    s["votes_loups"] = ["D"]
    s["cible_poison"] = "B"
    resoudre_nuit(s)
    assert sorted(s["morts_nuit"]) == ["B", "D"]
    assert s["double_victime"] is True


# --- Servante dévouée --------------------------------------------------------

def test_la_servante_reprend_le_role_d_un_loup(faire_partie):
    s = faire_partie({"A": "loup", "B": "loup", "C": "servante", "D": "villageois", "E": "villageois"})
    tuer(s, "B", "est éliminé par le village")
    servante_prend_role(s, "C", "B")
    assert s["joueurs"]["C"]["role"] == "loup" and camp(s, "C") == "loups"
    assert "C" in s["loups"]
    assert s["servante_nuit"] == {"servante": "C", "mort": "B"}
    assert any("servante dévouée C prend le rôle de B (Loup-Garou)" in e["texte"] for e in s["journal"])


def test_les_condamnes_de_la_veille(faire_partie):
    s = faire_partie({"A": "loup", "B": "villageois", "C": "servante", "D": "villageois"})
    assert condamnes_de_la_veille(s) == []
    s["jour"] = 1
    enregistrer_condamne(s, "B")
    enregistrer_condamne(s, "D")
    assert condamnes_de_la_veille(s) == []  # même jour : la nuit n'est pas encore tombée
    s["jour"] = 2
    assert condamnes_de_la_veille(s) == ["B", "D"]
    s["jour"] = 3
    assert condamnes_de_la_veille(s) == []


# --- Sœurs et Frères ---------------------------------------------------------

def test_les_soeurs_se_reconnaissent_dans_le_journal():
    s = nouvelle_partie(list("ABCDE"), {"loup": 1, "soeur": 2, "villageois": 2})
    assert sum("se reconnaissent" in e["texte"] for e in s["journal"]) == 1


# --- Montreur d'ours, Petite Fille, Idiot, Bouc émissaire -----------------------------------------

def test_les_voisins_sautent_les_morts(faire_partie):
    s = faire_partie({"A": "villageois", "B": "villageois", "C": "villageois", "D": "villageois", "E": "villageois"})
    assert voisins_vivants(s, "A") == ["E", "B"]
    s["joueurs"]["B"]["vivant"] = False
    assert voisins_vivants(s, "A") == ["E", "C"]


def test_l_ours_grogne_quand_un_voisin_est_un_loup(faire_partie):
    s = faire_partie({"A": "montreur_ours", "B": "loup", "C": "villageois", "D": "villageois", "E": "villageois"})
    assert ours_grogne(s) == ("A", ["E", "B"])


def test_l_ours_se_tait_sans_loup_voisin(faire_partie):
    s = faire_partie({"A": "montreur_ours", "B": "villageois", "C": "loup", "D": "villageois", "E": "villageois"})
    assert ours_grogne(s) is None


def test_l_ours_grogne_apres_la_mort_du_voisin_qui_cachait_un_loup(faire_partie):
    s = faire_partie({"A": "montreur_ours", "B": "villageois", "C": "loup", "D": "villageois", "E": "villageois"})
    tuer(s, "B")
    assert ours_grogne(s) == ("A", ["E", "C"])


def test_pas_d_ours_si_le_montreur_est_mort(faire_partie):
    s = faire_partie({"A": "montreur_ours", "B": "loup", "C": "villageois", "D": "villageois"})
    tuer(s, "A")
    assert ours_grogne(s) is None


def test_l_idiot_est_epargne_une_seule_fois(faire_partie):
    s = faire_partie({"A": "idiot", "B": "loup", "C": "villageois"})
    assert epargner_idiot(s, "A") is True
    assert s["joueurs"]["A"]["vote_perdu"] and s["joueurs"]["A"]["vivant"]
    assert epargner_idiot(s, "A") is False
    assert epargner_idiot(s, "C") is False


def test_le_bouc_emissaire_vivant(faire_partie):
    s = faire_partie({"A": "bouc_emissaire", "B": "loup", "C": "villageois"})
    assert bouc_emissaire(s) == "A"
    tuer(s, "A")
    assert bouc_emissaire(s) is None


def test_la_petite_fille_surprise_est_devoree_malgre_les_protections(faire_partie):
    s = faire_partie({"A": "loup", "B": "petite_fille", "C": "salvateur", "D": "villageois", "E": "villageois"})
    s["jour"] = 1
    s["votes_loups"] = ["D"]
    s["petite_fille_surprise"] = "B"
    s["protege_nuit"] = "B"
    s["soin_sorciere"] = True
    resoudre_nuit(s)
    assert "B" in s["morts_nuit"]
    assert s["petite_fille_surprise"] is None
