"""Mesure le poids de chaque rôle par simulation de parties complètes avec le vrai moteur du jeu.

Des joueurs automatiques (aucune stratégie fine) jouent des milliers de parties ; une régression logistique
donne, pour chaque rôle, son effet sur la chance de victoire du village. Résultat : src/loup_garou/assets/equilibre.json.

Usage : uv run --python 3.12 --with numpy python outils/simuler_equilibre.py [--parties 2000] [--croyance 0.6]

Hypothèses du joueur automatique (limites : voir docs/equilibre-roles.md) :
- les loups dévorent au hasard parmi les non-loups, et votent au hasard parmi les non-loups ;
- le village vote au hasard, sauf que, avec une probabilité `croyance` par jour, il suit les informations
  publiques (loup démasqué par la voyante, groupe suspect du renard) et épargne les joueurs blanchis ;
- les informations d'une nuit ne deviennent publiques que si leur détenteur est encore en vie au matin ;
- sorcière à l'aveugle : elle utilise sa potion de soin une nuit au hasard ; salvateur : protège au hasard.
"""

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from loup_garou.moteur.partie import (  # noqa: E402
    bouc_emissaire, camp, condamnes_de_la_veille, enregistrer_condamne, epargner_idiot, nouvelle_partie, ours_grogne,
    resoudre_nuit, servante_prend_role, tuer, vainqueur, vivants,
)
from loup_garou.options import nuit_active, opt  # noqa: E402
from loup_garou.roles import ROLES  # noqa: E402

SORTIE = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets" / "equilibre.json"
NUITS_MAX = 40


class Bots:
    def __init__(self, s, rng, croyance, flair):
        self.s, self.rng, self.croyance, self.flair = s, rng, croyance, flair
        self.loups_connus, self.blanchis, self.groupe_suspect = set(), set(), set()
        self.prive = {}  # nom -> joueurs que ce joueur sait innocents (fratrie)
        self.en_attente = []  # informations de la nuit, publiées le matin si leur détenteur vit encore
        self.votes = self.touches = 0
        self.fratries = []  # groupes de sœurs ou de frères : ils se savent innocents et votent en bloc
        self.extra = 0  # événements imprévus propres aux rôles de vote (idiot, bouc émissaire, petite fille surprise)

    # --- choix de cible ---------------------------------------------------------------------------
    def cible_village(self, votant, croit):
        s, rng = self.s, self.rng
        autres = [n for n in vivants(s) if n != votant]
        if camp(s, votant) == "loups":
            return rng.choice([n for n in autres if camp(s, n) != "loups"] or autres)
        if croit:
            connus = [n for n in self.loups_connus if s["joueurs"][n]["vivant"] and n != votant]
            if connus:
                return rng.choice(connus)
            suspects = [n for n in self.groupe_suspect if s["joueurs"][n]["vivant"] and n != votant]
            if suspects:
                return rng.choice(suspects)
        loups_vivants = [n for n in autres if camp(s, n) == "loups"]
        if loups_vivants and rng.random() < self.flair:
            return rng.choice(loups_vivants)  # intuition : une partie des joueurs devine un loup
        exclus = set(self.prive.get(votant, ())) | (self.blanchis if croit else set())
        return rng.choice([n for n in autres if n not in exclus] or autres)

    def voter(self):
        s, rng = self.s, self.rng
        croit = rng.random() < self.croyance
        votants = [v for v in vivants(s) if not s["joueurs"][v].get("vote_perdu")]
        # Une fratrie encore en vie vote en bloc : un seul choix, fait par l'un d'eux.
        choix_fratrie = {}
        for fratrie in self.fratries:
            vivante = [m for m in fratrie if s["joueurs"][m]["vivant"] and m in votants]
            if len(vivante) > 1:
                cible = self.cible_village(vivante[0], croit)
                for m in vivante:
                    choix_fratrie[m] = cible if cible != m else self.cible_village(m, croit)
        urne = Counter(choix_fratrie.get(v) or self.cible_village(v, croit) for v in votants)
        corbeau = s.get("corbeau_cible")
        if corbeau and s["joueurs"][corbeau]["vivant"]:
            urne[corbeau] += 2
        maxi = max(urne.values())
        ex_aequo = [n for n, c in urne.items() if c == maxi]
        bouc = bouc_emissaire(s)
        if len(ex_aequo) > 1 and bouc:
            condamne = bouc
            self.extra += 1
        else:
            condamne = rng.choice(ex_aequo)
        self.votes += 1
        self.touches += camp(s, condamne) == "loups"
        return condamne

    def tirs(self):
        s, rng = self.s, self.rng
        while s["tirs_en_attente"]:
            chasseur = s["tirs_en_attente"].pop(0)
            if len(vivants(s)) > 0:
                cible = self.cible_village(chasseur, rng.random() < self.croyance)
                s["morts_tir"] += tuer(s, cible, "est abattu par le chasseur", "tir")

    # --- nuit ---------------------------------------------------------------------------------
    def nuit_0(self):
        s, rng = self.s, self.rng
        noms = list(s["joueurs"])
        for nom in noms:
            role = s["joueurs"][nom]["role"]
            if role == "cupidon" and not s["amoureux"]:
                couple = rng.sample(noms, 3 if opt(s, "trouple") else 2)
                s["amoureux"] = couple
                for n in couple:
                    s["joueurs"][n]["amoureux"] = True
            elif role == "chien_loup":
                s["joueurs"][nom]["camp_choisi"] = rng.choice(["village", "loups"])
                if s["joueurs"][nom]["camp_choisi"] == "loups":
                    s["loups"].append(nom)
            elif role == "voleur":
                choix = rng.choice(s["cartes_milieu"] + ["villageois"]) if s["cartes_milieu"] else "villageois"
                s["joueurs"][nom]["role"] = choix
                if ROLES[choix].camp == "loups":
                    s["loups"].append(nom)
                s["cartes_milieu"] = []
            elif role == "enfant_sauvage":
                s["mentor_enfant"] = rng.choice([n for n in noms if n != nom])
        for cle in ("soeur", "frere"):
            fratrie = [n for n in noms if s["joueurs"][n]["role"] == cle]
            for n in fratrie:
                self.prive[n] = set(fratrie) - {n}
            if len(fratrie) > 1:
                self.fratries.append(fratrie)

    def nuit(self):
        s, rng = self.s, self.rng
        en_vie = vivants(s)
        # servante : reprend le rôle du condamné de la veille
        for n in en_vie:
            if s["joueurs"][n]["role"] == "servante" and condamnes_de_la_veille(s):
                village = [c for c in condamnes_de_la_veille(s) if camp(s, c) != "loups"]
                if village:
                    servante_prend_role(s, n, village[0])
        # juge bègue : exige un second vote dès qu'il reste assez de monde
        for n in vivants(s):
            if s["joueurs"][n]["role"] == "juge_begue" and not s.get("juge_utilise") and len(vivants(s)) >= 5:
                s["juge_utilise"], s["second_vote"] = True, s["jour"]
        loups = [n for n in vivants(s) if camp(s, n) == "loups"]
        cibles = [n for n in vivants(s) if camp(s, n) != "loups"]
        if loups and cibles:
            k = min(2, len(cibles)) if s.get("double_victime") else 1
            s["votes_loups"] = rng.sample(cibles, k)
        for n in vivants(s):
            role = s["joueurs"][n]["role"]
            if role == "loup_blanc" and nuit_active(s, opt(s, "cadence_loup_blanc")):
                freres = [m for m in vivants(s) if m != n and camp(s, m) == "loups"]
                if freres and len(cibles) <= 4:
                    s["cible_loup_blanc"] = rng.choice(freres)
            elif role == "salvateur":
                choix = [m for m in vivants(s) if m != s.get("protege_precedent")]
                s["protege_nuit"] = rng.choice(choix)
            elif role == "sorciere" and s["potions_sorciere"] > 0 and not s["soin_sorciere"] and rng.random() < .35:
                s["soin_sorciere"] = True
                s["potions_sorciere"] -= 1
            elif role == "sorciere" and s.get("potions_mort_sorciere", 0) > 0 and not s.get("cible_poison") and rng.random() < .3:
                s["cible_poison"] = rng.choice([m for m in vivants(s) if m != n])
                s["potions_mort_sorciere"] -= 1
            elif role == "voyante" and nuit_active(s, opt(s, "cadence_voyante")):
                vu = rng.choice([m for m in vivants(s) if m != n])
                self.en_attente.append((n, "loup" if camp(s, vu) == "loups" else "blanc", vu))
            elif role == "renard" and s["jour"] > 0:
                groupe = rng.sample([m for m in vivants(s) if m != n], min(3, len(vivants(s)) - 1))
                if any(camp(s, m) == "loups" for m in groupe):
                    self.en_attente.append((n, "groupe", groupe))
                else:
                    self.en_attente.append((n, "clair", groupe))
                    s["joueurs"][n]["role"] = "villageois"
            elif role == "petite_fille" and s["jour"] > 0:
                if rng.random() < 1 / 3:
                    s["petite_fille_surprise"] = n
                    self.extra += 1
                else:
                    meute = [m for m in vivants(s) if m != n and camp(s, m) == "loups"]
                    innocents = [m for m in vivants(s) if m != n and camp(s, m) != "loups"]
                    if meute:  # deux silhouettes : un loup et un innocent
                        self.en_attente.append((n, "groupe", [rng.choice(meute)] + ([rng.choice(innocents)] if innocents else [])))
            elif role == "corbeau" and s["jour"] > 0:
                pistes = [m for m in vivants(s) if m != n]
                suspects = [m for m in pistes if m in self.loups_connus or m in self.groupe_suspect]
                s["corbeau_cible"] = rng.choice(suspects or pistes)
        resoudre_nuit(s)
        # L'ours du Montreur grogne en public : un voisin loup désigne ces deux voisins comme suspects.
        grognement = ours_grogne(s)
        for montreur in [n for n in vivants(s) if s["joueurs"][n]["role"] == "montreur_ours"]:
            voisins = set(grognement[1]) if grognement and grognement[0] == montreur else None
            if voisins:
                self.groupe_suspect = voisins
            else:
                from loup_garou.moteur.partie import voisins_vivants
                self.blanchis |= set(voisins_vivants(s, montreur))

    def publier(self):
        s = self.s
        for fratrie in self.fratries:  # deux sœurs ou plus se vouent mutuellement : elles se blanchissent en public
            vivantes = [m for m in fratrie if s["joueurs"][m]["vivant"]]
            if len(vivantes) > 1:
                self.blanchis |= set(vivantes)
        for detenteur, genre, valeur in self.en_attente:
            if not s["joueurs"][detenteur]["vivant"] and genre in ("loup", "blanc"):
                continue
            if genre == "loup":
                self.loups_connus.add(valeur)
            elif genre == "blanc":
                self.blanchis.add(valeur)
            elif genre == "groupe":
                self.groupe_suspect = set(valeur)
            else:
                self.blanchis |= set(valeur)
        self.en_attente = []


def evenements(s, issue):
    """Événements imprévus d'une partie : morts hors loups et vote, changements de camp, votes en plus, victoire à part."""
    n = sum(m["genre"] in ("tir", "poison", "chagrin", "loup_blanc") for m in s["morts"])
    for d in s["joueurs"].values():
        n += bool(d.get("enfant_sauvage")) + (d.get("camp_choisi") == "loups") + bool(d.get("servante"))
        n += bool(d.get("voleur") and ROLES[d["role"]].camp == "loups")
    n += bool(s.get("juge_utilise")) + any(m["role"] == "louveteau" for m in s["morts"]) + (issue == "autre")
    return n


def jouer(composition, options, rng, croyance, flair):
    """Une partie complète ; renvoie (issue, votes, votes sur un loup, événements imprévus)."""
    nb = sum(composition.values()) - sum(ROLES[c].cartes_en_plus * n for c, n in composition.items())
    s = nouvelle_partie([f"J{i}" for i in range(nb)], composition, options)
    bots = Bots(s, rng, croyance, flair)
    bots.nuit_0()
    s["jour"] = 1
    gagnant = None
    for _ in range(NUITS_MAX):
        s["phase"] = "nuit"
        bots.nuit()
        bots.tirs()
        gagnant = vainqueur(s)
        if gagnant:
            break
        bots.publier()
        s["phase"] = "conseil"
        if s.get("maire") is None:
            s["maire"] = rng.choice(vivants(s))
        for rang in (1, 2):
            if rang == 2 and s.get("second_vote") != s["jour"]:
                break
            condamne = bots.voter()
            if epargner_idiot(s, condamne):
                bots.extra += 1
            else:
                tuer(s, condamne, "est éliminé par le village", "village")
                enregistrer_condamne(s, condamne)
            bots.tirs()
            gagnant = vainqueur(s)
            if gagnant:
                break
            if s.get("maire") is None and vivants(s):
                s["maire"] = rng.choice(vivants(s))
        if gagnant:
            break
        s["corbeau_cible"] = None
        s["jour"] += 1
    issue = "autre" if not gagnant else ("village" if gagnant.startswith("Le village") else "loups" if gagnant.startswith("Les loups") else "autre")
    return issue, bots.votes, bots.touches, evenements(s, issue) + bots.extra


# --- compositions et mesures --------------------------------------------------------------------

REF_JOUEURS, REF_LOUPS = 14, 3


def composer(nb, loups, extras):
    """Paquet d'une table de `nb` joueurs : `extras` = {rôle: nombre de cartes}, le reste en villageois."""
    composition = {"loup": loups, **extras}
    total = nb + sum(ROLES[c].cartes_en_plus * n for c, n in composition.items())
    composition["villageois"] = total - sum(composition.values())
    return composition if composition["villageois"] >= 0 else None


def serie(composition, options, parties, graine, croyance, flair):
    rng = random.Random(graine)
    random.seed(graine)
    res = [jouer(composition, options, rng, croyance, flair) for _ in range(parties)]
    votes = sum(r[1] for r in res)
    return {
        "p": sum(r[0] == "village" for r in res) / parties,
        "precision": sum(r[2] for r in res) / max(votes, 1),
        "evenements": sum(r[3] for r in res) / parties,
    }


def logit(p):
    p = min(max(p, 1e-3), 1 - 1e-3)
    return math.log(p / (1 - p))


def recommandee(nb):
    from loup_garou.moteur.partie import composition_recommandee

    loups, speciaux = composition_recommandee(nb)
    return composer(nb, loups, {k: v for k, v in speciaux.items() if v})


def calibrer(parties, croyance):
    """Dichotomie sur le flair : la victoire moyenne du village sur les compositions recommandées vaut 50 %."""
    bas, haut = 0.0, 0.8
    for _ in range(8):
        flair = (bas + haut) / 2
        moyenne = np.mean([serie(recommandee(nb), None, parties, 3, croyance, flair)["p"] for nb in (8, 10, 12, 14, 16)])
        print(f"flair={flair:.3f} -> victoire moyenne du village {moyenne:.3f}", file=sys.stderr)
        bas, haut = (flair, haut) if moyenne < .5 else (bas, flair)
    print(f"flair retenu : {(bas + haut) / 2:.3f}", file=sys.stderr)


def marges(parties, croyance, flair):
    """Effet de chaque rôle, seul à la place de villageois, sur une table de référence."""
    ref = serie(composer(REF_JOUEURS, REF_LOUPS, {}), None, parties, 1, croyance, flair)
    sortie = {"_reference": ref}
    for cle, role in ROLES.items():
        if cle == "villageois":
            continue
        compo = composer(REF_JOUEURS, REF_LOUPS + 1, {}) if cle == "loup" else composer(REF_JOUEURS, REF_LOUPS, {cle: role.lot})
        r = serie(compo, None, parties, 2, croyance, flair)
        lot = 1 if cle == "loup" else role.lot
        sortie[cle] = {
            "delta_pts": 100 * (r["p"] - ref["p"]) / lot,
            "delta_logit": (logit(r["p"]) - logit(ref["p"])) / lot,
            "delta_precision": (r["precision"] - ref["precision"]) / lot,
            "delta_evenements": (r["evenements"] - ref["evenements"]) / lot,
        }
        print(f"{cle:15s} {100 * r['p']:5.1f} %  delta {sortie[cle]['delta_pts']:+6.1f} pts  "
              f"précision {sortie[cle]['delta_precision']:+.3f}  événements {sortie[cle]['delta_evenements']:+.2f}", file=sys.stderr)
    return sortie


def regression(compositions, parties, croyance, flair, ridge=1e-2):
    """Régression logistique de la victoire du village sur les effectifs de chaque rôle et la taille de la table."""
    cles = [c for c in ROLES if c not in ("villageois",)]
    lignes, essais, reussites = [], [], []
    for k, (nb, compo) in enumerate(compositions):
        r = serie(compo, None, parties, 100 + k, croyance, flair)
        x = [1.0, nb / 10, (nb / 10) ** 2] + [float(compo.get(c, 0)) for c in cles]
        lignes.append(x)
        essais.append(parties)
        reussites.append(round(r["p"] * parties))
    X, n, y = np.array(lignes), np.array(essais, float), np.array(reussites, float)
    cut = int(len(X) * .8)
    beta = ajuster(X[:cut], n[:cut], y[:cut], ridge)
    p_test = 1 / (1 + np.exp(-X[cut:] @ beta))
    obs = y[cut:] / n[cut:]
    brier = float(np.mean((p_test - obs) ** 2))
    pente = float(np.polyfit(p_test, obs, 1)[0])
    beta = ajuster(X, n, y, ridge)
    return cles, beta, {"brier": brier, "pente_calibration": pente, "compositions": len(X), "parties_par_composition": parties}


def ajuster(X, n, y, ridge):
    beta = np.zeros(X.shape[1])
    pen = np.eye(X.shape[1]) * ridge
    pen[0, 0] = 0
    for _ in range(40):
        p = 1 / (1 + np.exp(-X @ beta))
        w = n * p * (1 - p) + 1e-9
        grad = X.T @ (y - n * p) - pen @ beta
        beta = beta + np.linalg.solve(X.T @ (X * w[:, None]) + pen, grad)
    return beta


def compositions_aleatoires(nombre, graine=5):
    rng = random.Random(graine)
    sortie = []
    cles = [c for c in ROLES if c not in ("loup", "villageois")]
    while len(sortie) < nombre:
        nb = rng.randint(7, 18)
        loups = max(1, round(nb * rng.uniform(.17, .32)))
        extras = {c: ROLES[c].lot for c in cles if rng.random() < .3}
        compo = composer(nb, loups, extras)
        if compo:
            sortie.append((nb, compo))
    return sortie


def effets_options(parties, croyance, flair):
    """Effet (en log-cotes) de chaque option sur la victoire du village, par rapport au réglage par défaut."""
    base = composer(REF_JOUEURS, REF_LOUPS, {})
    avec = lambda **extras: composer(REF_JOUEURS, REF_LOUPS, extras)  # noqa: E731

    def delta(compo, options, defaut=None):
        a = serie(compo, options, parties, 7, croyance, flair)["p"]
        b = serie(compo, defaut, parties, 7, croyance, flair)["p"]
        return logit(a) - logit(b)

    sortie = {
        "cadence_voyante": {str(c): delta(avec(voyante=1), {"cadence_voyante": c}) for c in (1, 3)},
        "cadence_loup_blanc": {str(c): delta(avec(loup_blanc=1), {"cadence_loup_blanc": c}) for c in (1, 3)},
        "potions_sorciere": delta(avec(sorciere=1), {"potions_sorciere": 2}),
        "potions_mort": delta(avec(sorciere=1), {"potions_mort": 1}),
        "maire_depart_faux": delta(base, {"maire_depart": False}),
        "couple_hasard": delta(base, {"couple_hasard": True}),
        "trouple": delta(base, {"couple_hasard": True, "trouple": True}, {"couple_hasard": True}),
    }
    for cle, v in sortie.items():
        print(f"option {cle}: {v}", file=sys.stderr)
    return sortie


def mise_a_l_echelle(valeurs, positif=True):
    """Ramène les valeurs à 0..100 par rapport au maximum (les valeurs négatives comptent pour 0)."""
    maxi = max(max(valeurs.values()), 1e-9)
    return {k: round(100 * max(v, 0) / maxi) for k, v in valeurs.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parties", type=int, default=5000, help="parties par mesure de rôle ou d'option")
    ap.add_argument("--compositions", type=int, default=2400, help="compositions aléatoires pour la régression")
    ap.add_argument("--croyance", type=float, default=.6)
    ap.add_argument("--flair", type=float, default=.092, help="part des votants du village qui devinent un loup")
    ap.add_argument("--calibrer", action="store_true", help="cherche le flair qui équilibre les compositions recommandées")
    ap.add_argument("--rapide", action="store_true", help="affiche l'effet de chaque rôle sans écrire le fichier")
    args = ap.parse_args()
    if args.calibrer:
        return calibrer(args.parties, args.croyance)
    m = marges(args.parties, args.croyance, args.flair)
    if args.rapide:
        return
    cles, beta, validation = regression(compositions_aleatoires(args.compositions), 25, args.croyance, args.flair)
    print(f"validation : {validation}", file=sys.stderr)
    roles = {c: v for c, v in m.items() if c != "_reference"}
    info = mise_a_l_echelle({c: v["delta_precision"] if ROLES[c].camp == "village" else 0 for c, v in roles.items()})
    info = {c: (v if v >= 8 else 0) for c, v in info.items()}  # sous 8 : bruit de simulation
    chaos = mise_a_l_echelle({c: v["delta_evenements"] for c, v in roles.items()})
    sortie = {
        "meta": {"parties_par_mesure": args.parties, "croyance": args.croyance, "flair": args.flair,
                 "table_reference": f"{REF_JOUEURS} joueurs, {REF_LOUPS} loups", "reference_village": m["_reference"]["p"]},
        "modele": {"intercept": beta[0], "joueurs": beta[1], "joueurs2": beta[2],
                   "roles": {c: float(b) for c, b in zip(cles, beta[3:])}},
        "roles": {c: {"impact_pts": round(float(b) * 25, 1), "info": info.get(c, 0), "chaos": chaos.get(c, 0),
                      "marge_pts": round(roles[c]["delta_pts"], 1)}
                  for c, b in zip(cles, beta[3:])},
        "options": effets_options(args.parties, args.croyance, args.flair),
        "validation": validation,
    }
    SORTIE.write_text(json.dumps(sortie, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print("écrit", SORTIE, file=sys.stderr)


if __name__ == "__main__":
    main()
