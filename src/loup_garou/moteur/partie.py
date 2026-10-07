"""Règles du jeu : création d'une partie, morts, résolution de la nuit, conditions de victoire."""

import random
from collections import Counter

from loup_garou.moteur.journal import log, prendre_instantane
from loup_garou.moteur.migrations import VERSION
from loup_garou.moteur.persistance import archiver_partie
from loup_garou.options import opt, OPTIONS_DEFAUT, taille_couple
from loup_garou.roles import ROLES, ROLES_SPECIAUX


def nouvelle_partie(noms, composition, options=None):
    """noms : liste de noms de joueurs. composition : dict {role: nombre}. options : cf. OPTIONS_DEFAUT."""
    roles = []
    for role, n in composition.items():
        roles += [role] * n
    random.shuffle(roles)

    joueurs = {
        nom: {"role": role, "vivant": True, "amoureux": False}
        for nom, role in zip(noms, roles)
    }
    cartes_milieu = roles[len(noms):]

    etat = {
        "version": VERSION,
        "nb_joueurs": len(noms),
        "jour": 0,
        "phase": "nuit",
        "joueurs": joueurs,
        "loups": [n for n, d in joueurs.items() if ROLES[d["role"]].camp == "loups"],
        "amoureux": [],
        "votes_loups": [],
        "ordre_nuit": [],
        "tour": 0,
        "devoile": False,
        "transfert": False,
        "morts_nuit": [],
        "cartes_milieu": cartes_milieu,
        "morts_tir": [],
        "tirs_en_attente": [],
        "retour_tir": None,
        "journal": [],
        "morts": [],
        "composition": {cle: n for cle, n in composition.items() if n > 0},
        "maire": None,
        "dernier_maire": None,
    }
    for role in ROLES.values():
        etat.update(role.etat_initial)
    etat["options"] = {**OPTIONS_DEFAUT, **(options or {})}
    etat["potions_sorciere"] = etat["options"]["potions_sorciere"]
    etat["potions_mort_sorciere"] = etat["options"]["potions_mort"]
    paquet = ", ".join(f"{ROLES[cle].nom} ×{n}" for cle, n in composition.items() if n > 0)
    log(etat, f"{len(noms)} joueurs. Paquet : {paquet}.", "debut")
    log(etat, "Distribution : " + ", ".join(
        f"{n} ({ROLES[d['role']].nom})" for n, d in joueurs.items()
    ) + ".", "debut")
    for cle in ("soeur", "frere"):
        fratrie = [n for n, d in joueurs.items() if d["role"] == cle]
        if len(fratrie) > 1:
            log(etat, f"{ROLES[cle].nom}s : {', '.join(fratrie)} se reconnaissent.", "debut")
    if etat["options"]["couple_hasard"]:
        couple = random.sample(list(joueurs), taille_couple(etat))
        etat["amoureux"] = couple
        for n in couple:
            joueurs[n]["amoureux"] = True
        log(etat, f"Le hasard lie {', '.join(couple[:-1])} et {couple[-1]}.", "debut")
    return etat


def vivants(s):
    return [n for n, d in s["joueurs"].items() if d["vivant"]]


def camp(s, nom):
    """Camp effectif d'un joueur : celui qu'il a choisi (Chien-Loup) sinon celui de son rôle."""
    d = s["joueurs"][nom]
    return d.get("camp_choisi") or ROLES[d["role"]].camp


def _convertir_enfant_sauvage(s, morts):
    """Si le mentor de l'enfant sauvage est mort, l'enfant (s'il vit encore) devient loup-garou."""
    mentor = s.get("mentor_enfant")
    if mentor is None or mentor not in morts:
        return
    s["mentor_enfant"] = None
    for n in vivants(s):
        d = s["joueurs"][n]
        if d["role"] == "enfant_sauvage":
            d["role"] = "loup"
            d["enfant_sauvage"] = True
            log(s, f"Le mentor {mentor} est mort : {n} (Enfant sauvage) devient loup-garou.")
            s["loups"].append(n)


def tuer(s, nom, cause="meurt", genre="autre"):
    """Tue un joueur et entraîne son amoureux dans la mort. Renvoie la liste des morts.

    `genre` classe la mort pour le bilan : loups, loup_blanc, poison, village, tir, autre."""
    if nom not in s["joueurs"] or not s["joueurs"][nom]["vivant"]:
        return []
    s["joueurs"][nom]["vivant"] = False
    morts = [nom]
    if s["joueurs"][nom]["amoureux"]:
        for autre in s["amoureux"]:
            if autre != nom and s["joueurs"][autre]["vivant"]:
                s["joueurs"][autre]["vivant"] = False
                morts.append(autre)
    if s.get("maire") in morts:
        s["dernier_maire"] = s["maire"]
        s["maire"] = None
    for i, mort in enumerate(morts):
        raison = cause if i == 0 else "meurt de chagrin (amoureux)"
        log(s, f"{mort} ({ROLES[s['joueurs'][mort]['role']].nom}) {raison}.")
        s.setdefault("morts", []).append({
            "nom": mort, "role": s["joueurs"][mort]["role"], "camp": camp(s, mort),
            "genre": genre if i == 0 else "chagrin", "jour": s["jour"],
            "moment": "nuit" if s["phase"] == "nuit" else "jour",
        })
    _convertir_enfant_sauvage(s, morts)
    for mort in morts:
        if ROLES[s["joueurs"][mort]["role"]].tir_a_la_mort:
            s.setdefault("tirs_en_attente", []).append(mort)
    if any(s["joueurs"][n]["role"] == "louveteau" for n in morts):
        s["double_victime"] = True
        log(s, "Le Louveteau est mort : la meute dévorera deux victimes la nuit prochaine.")
    return morts


def enregistrer_condamne(s, nom):
    """Retient les joueurs éliminés par le village ce jour-là : la servante dévouée peut reprendre leur rôle."""
    condamnes = s.get("condamnes")
    if not condamnes or condamnes["jour"] != s["jour"]:
        condamnes = {"jour": s["jour"], "noms": []}
    condamnes["noms"].append(nom)
    s["condamnes"] = condamnes


def condamnes_de_la_veille(s):
    """Joueurs que le village a éliminés au conseil précédant la nuit en cours."""
    condamnes = s.get("condamnes")
    return condamnes["noms"] if condamnes and condamnes["jour"] == s["jour"] - 1 else []


def servante_prend_role(s, servante, mort):
    """La servante dévouée reprend en secret le rôle de `mort` ; le panneau du lendemain l'annoncera."""
    role = s["joueurs"][mort]["role"]
    s["joueurs"][servante]["role"] = role
    s["joueurs"][servante]["servante"] = mort
    s["servante_nuit"] = {"servante": servante, "mort": mort}
    if ROLES[role].camp == "loups":
        s["loups"].append(servante)
    log(s, f"La servante dévouée {servante} prend le rôle de {mort} ({ROLES[role].nom}).")


def voisins_vivants(s, nom):
    """Les deux voisins vivants d'un joueur autour de la table (ordre des noms saisis à l'installation)."""
    ordre = list(s["joueurs"])
    i = ordre.index(nom)
    n = len(ordre)
    trouves = []
    for sens in (-1, 1):
        for k in range(1, n):
            autre = ordre[(i + sens * k) % n]
            if s["joueurs"][autre]["vivant"]:
                trouves.append(autre)
                break
    return list(dict.fromkeys(trouves))


def ours_grogne(s):
    """Le Montreur d'ours vivant dont l'ours grogne (un voisin vivant est un loup) : (montreur, voisins) ou None."""
    for nom in vivants(s):
        if s["joueurs"][nom]["role"] == "montreur_ours":
            voisins = voisins_vivants(s, nom)
            if any(camp(s, v) == "loups" for v in voisins):
                return nom, voisins
    return None


def epargner_idiot(s, nom):
    """L'Idiot du village condamné par le vote révèle son rôle et survit (une fois), mais ne votera plus."""
    d = s["joueurs"][nom]
    if d["role"] == "idiot" and not d.get("idiot_revele"):
        d["idiot_revele"] = True
        d["vote_perdu"] = True
        log(s, f"{nom} (Idiot du village) est désigné par le village : il révèle son rôle et est épargné, mais ne votera plus.")
        return True
    return False


def bouc_emissaire(s):
    """Le Bouc émissaire vivant (condamné en cas d'égalité des voix), ou None."""
    return next((n for n in vivants(s) if s["joueurs"][n]["role"] == "bouc_emissaire"), None)


def vainqueur(s):
    en_vie = vivants(s)
    loups = [n for n in en_vie if camp(s, n) == "loups"]
    autres = [n for n in en_vie if camp(s, n) != "loups"]
    solitaires = [n for n in en_vie if ROLES[s["joueurs"][n]["role"]].solitaire]

    couple = [n for n in s.get("amoureux", []) if s["joueurs"][n]["vivant"]]
    if len(couple) >= 2 and len(en_vie) == len(couple):
        nombre = "deux" if len(couple) == 2 else "trois"
        return f"Les amoureux l'emportent : ils sont les {nombre} derniers survivants."
    if len(couple) >= 2 and len({camp(s, n) == "loups" for n in couple}) == 2:
        # Couple loup/villageois : camp à part, ni le village ni la meute ne peuvent conclure.
        return None
    if solitaires:
        # Tant qu'il vit, ni le village ni la meute ne peuvent conclure : il doit rester seul.
        if len(en_vie) == 1:
            return f"{solitaires[0]} ({ROLES[s['joueurs'][solitaires[0]]['role']].nom}) l'emporte seul."
        return None
    if not loups:
        return "Le village a gagné : tous les loups sont morts."
    if len(loups) > len(autres):
        return "Les loups ont gagné : ils sont plus nombreux que les villageois."
    if len(loups) == len(autres):
        if not opt(s, "maire_depart"):
            return "Les loups ont gagné : ils sont aussi nombreux que les villageois."
        # À égalité, le village garde sa chance tant que le maire n'est pas un loup.
        if s.get("maire") in loups:
            return "Les loups ont gagné : ils sont aussi nombreux que les villageois et l'un d'eux est maire."
    return None


def fin_de_tour(s):
    """Passe au joueur suivant dans la nuit."""
    s["tour"] += 1
    s["devoile"] = False
    s["transfert"] = False


def terminer_partie(s, message):
    log(s, message, "fin")
    s["phase"] = "fin"
    s["message_fin"] = message
    archiver_partie(s, message)


def victimes_loups(votes, n):
    """Les `n` joueurs les plus désignés ; une égalité à la limite écarte tous les ex æquo."""
    comptes = Counter(votes).most_common()
    if len(comptes) > n and comptes[n - 1][1] == comptes[n][1]:
        seuil = comptes[n - 1][1]
        comptes = [c for c in comptes if c[1] > seuil]
    return [nom for nom, _ in comptes[:n]]


def resoudre_nuit(s):
    morts = []
    # Lu avant tout : une mort de cette nuit (Louveteau) prépare la nuit suivante, pas celle-ci.
    attendues = 2 if s.get("double_victime") else 1
    s["double_victime"] = False
    if s["jour"] > 0:
        victimes = victimes_loups(s["votes_loups"], attendues)
        if not victimes:
            if s["votes_loups"]:
                log(s, "Les loups ne s'accordent pas : personne n'est dévoré.")
        elif len(victimes) < attendues:
            log(s, "Les loups ne s'accordent que sur une victime.")
        for i, victime in enumerate(victimes):
            sauveurs = []
            if i == 0 and s["soin_sorciere"]:
                sauveurs.append("la potion de la sorcière")
            if victime == s.get("protege_nuit"):
                sauveurs.append("le salvateur")
            if sauveurs:
                log(s, f"{victime} était la cible des loups mais est sauvé par {' et '.join(sauveurs)}.")
            else:
                morts += tuer(s, victime, "est dévoré par les loups", "loups")
        # Le festin du Loup Blanc échappe à la sorcière et au salvateur.
        if s.get("cible_loup_blanc"):
            morts += tuer(s, s["cible_loup_blanc"], "est dévoré par le Loup Blanc", "loup_blanc")
        # Le poison échappe à la potion de soin et au salvateur.
        if s.get("cible_poison"):
            morts += tuer(s, s["cible_poison"], "est empoisonné par la sorcière", "poison")
        # La Petite Fille surprise pendant son espionnage est dévorée : ni soin ni protection n'y changent rien.
        if s.get("petite_fille_surprise"):
            morts += tuer(s, s["petite_fille_surprise"], "est surprise par les loups pendant qu'elle les espionnait", "loups")
        if not morts:
            log(s, "Personne ne meurt cette nuit.")

    s["morts_nuit"] = morts
    s["morts_tir"] = []
    s["votes_loups"] = []
    s["cible_loup_blanc"] = None
    s["protege_precedent"] = s.get("protege_nuit")
    s["protege_nuit"] = None
    s["soin_sorciere"] = False
    s["cible_poison"] = None
    s["petite_fille_surprise"] = None
    s["ordre_nuit"] = []
    s["tour"] = 0
    s["devoile"] = False
    s["phase"] = "reveil"
    prendre_instantane(s, "jour")


def composition_recommandee(nb):
    """Suggestion de départ raisonnable pour un nombre de joueurs donné."""
    loups = max(1, nb // 4)
    reste = nb - loups
    speciaux = {}
    for role in ROLES_SPECIAUX:
        n = 1 if (role.unique and role.recommande and reste >= 1) else 0
        speciaux[role.key] = n
        reste -= n
    return loups, speciaux
