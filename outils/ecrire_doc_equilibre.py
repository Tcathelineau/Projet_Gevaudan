"""Écrit docs/equilibre-roles.md à partir de src/loup_garou/assets/equilibre.json (produit par simuler_equilibre.py).

Usage : python3 outils/ecrire_doc_equilibre.py
"""

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

from loup_garou.equilibre import bilan  # noqa: E402
from loup_garou.moteur.partie import composition_recommandee  # noqa: E402
from loup_garou.roles import ROLES  # noqa: E402

d = json.loads((RACINE / "src/loup_garou/assets/equilibre.json").read_text(encoding="utf-8"))

# Barème Ultimate Werewolf (Bezier Games), pour les rôles qui ont un équivalent.
UW = {
    "loup": "Werewolf -6", "voyante": "Seer +7", "sorciere": "Witch +4", "chasseur": "Hunter +3",
    "salvateur": "Bodyguard +3", "cupidon": "Cupid -3", "loup_blanc": "Lone Wolf -5", "louveteau": "Wolf Cub -8",
    "frere": "Mason +2", "soeur": "Mason +2", "renard": "P.I. +3", "villageois": "Villager +1",
    "idiot": "Village Idiot +2", "corbeau": "Troublemaker +2",
}
UW_VALEURS = {"loup": -6, "voyante": 7, "sorciere": 4, "chasseur": 3, "salvateur": 3, "cupidon": -3, "loup_blanc": -5,
              "louveteau": -8, "frere": 2, "soeur": 2, "renard": 3, "idiot": 2, "corbeau": 2}

REMARQUES = {
    "loup": "Référence des loups : un loup de plus fait chuter la victoire du village.",
    "louveteau": "Un loup de plus, et sa mort double les victimes de la nuit suivante.",
    "loup_blanc": "Il dévore ses frères en fin de partie (dès qu'il reste 4 villageois ou moins) : il affaiblit la meute plus qu'il ne gêne le village.",
    "chien_loup": "Camp tiré au hasard dans la simulation : environ un loup une fois sur deux.",
    "enfant_sauvage": "Devient loup si son mentor meurt.",
    "renard": "Son groupe suspect concentre les votes du village, mais la simulation le suppose bien suivi (voir les limites).",
    "voyante": "Une vision une nuit sur deux (réglage par défaut).",
    "voleur": "Effet dû aux deux cartes laissées au milieu : un loup peut y rester, ce qui retire un loup de la table.",
    "chasseur": "Sa balle touche un loup plus souvent que le hasard quand le village a des pistes.",
    "sorciere": "Soin à l'aveugle, une potion.",
    "juge_begue": "Un second vote élimine un joueur de plus, en moyenne plus souvent un loup qu'un innocent.",
    "cupidon": "Le couple est tiré au hasard : un couple mixte peut gêner les loups autant que le village.",
    "salvateur": "Protection au hasard : il sauve surtout par chance.",
    "frere": "Par carte. Les frères se savent innocents, se blanchissent en public et votent en bloc.",
    "soeur": "Par carte. Les sœurs se savent innocentes, se blanchissent en public et votent en bloc.",
    "servante": "Ne reprend que le rôle d'un condamné du village : elle ne change presque rien.",
    "montreur_ours": "Une information chaque matin, sans risque pour lui : l'ours désigne les deux voisins suspects.",
    "petite_fille": "Information forte (un loup parmi deux silhouettes) payée d'une chance sur trois d'être dévorée.",
    "corbeau": "Deux voix de plus, désignées au hasard ou sur un suspect : un coup de pouce, pas une arme.",
    "idiot": "Survit à une condamnation : il gaspille un vote du village sans l'éclairer.",
    "bouc_emissaire": "Handicap pour le village : une égalité des voix sacrifie un innocent.",
}

lignes = []
for c in sorted(d["roles"], key=lambda c: -d["roles"][c]["impact_pts"]):
    r, role = d["roles"][c], ROLES[c]
    ensemble = f" ({r['impact_pts'] * role.lot:+.0f} les {role.lot})" if role.lot > 1 else ""
    lignes.append(
        f"| {role.emoji} {role.nom}{' (par carte)' if role.lot > 1 else ''} | {'Loups' if role.camp == 'loups' else 'Village'} "
        f"| **{r['impact_pts']:+.0f}**{ensemble} | {r['marge_pts']:+.0f} | {r['info']} % | {r['chaos']} % | {UW.get(c, '-')} "
        f"| {REMARQUES.get(c, '')} |"
    )

communs = [c for c in UW_VALEURS if c in d["roles"]]


def rangs(valeurs):
    ordre = sorted(valeurs, key=valeurs.get)
    return {k: ordre.index(k) + 1 for k in valeurs}


a, b = rangs({c: UW_VALEURS[c] for c in communs}), rangs({c: d["roles"][c]["impact_pts"] for c in communs})
n = len(communs)
rho = 1 - 6 * sum((a[c] - b[c]) ** 2 for c in communs) / (n * (n * n - 1))

o = d["options"]
tables = []
for nb in (8, 10, 12, 14, 16):
    loups, speciaux = composition_recommandee(nb)
    compo = {"loup": loups, **{k: v for k, v in speciaux.items() if v}}
    compo["villageois"] = nb - sum(compo.values())
    tables.append((nb, loups, 100 * bilan(compo, nb).chance))
ligne_tables = "\n".join(
    f"| {nb} joueurs | {loups} | {p:.0f} % |" for nb, loups, p in tables
)

doc = f"""# Équilibre des rôles : méthode et mesures

Les jauges de l'écran de composition et les dalles de la page Documentation viennent de ce fichier. Les valeurs sont **mesurées par simulation** avec le vrai moteur du jeu (fichier généré par `outils/ecrire_doc_equilibre.py` à partir de `assets/equilibre.json`).

**Deuxième passe** : les sœurs et les frères étaient sous-évalués (la première simulation ne leur faisait que s'éviter entre eux) ; ils se blanchissent maintenant en public et votent en bloc. Les nouveaux rôles (Montreur d'ours, Petite Fille, Corbeau, Idiot du village, Bouc émissaire) sont mesurés dans la même simulation. Pour les rôles à plusieurs cartes, l'impact est donné par carte, avec le total pour l'ensemble.

## Ce que dit la littérature (et ce qu'elle ne dit pas)

- **Ultimate Werewolf (Bezier Games)** : seul barème chiffré que j'ai trouvé, en entiers (Seer +7, Witch +4, Hunter, Bodyguard, Priest, P.I. et Prince tous à +3, Cupid -3, Lone Wolf -5, Werewolf -6, Wolf Cub -8). Le regroupement à +3 vient de la source elle-même. Il ne couvre qu'une partie des rôles de l'app, avec leurs règles à lui.
- **Forums français (forum Thiercelieux, lu ; Trictrac, vu seulement par un résumé de recherche)** : des principes sans chiffres par rôle (un quart de loups, ne pas doubler les rôles de même puissance, le Chien-Loup équilibre la partie).
- **Andrew Plotkin (eblong.com, statistiques du loup-garou)** : probabilités de victoire du village sous jeu entièrement aléatoire, par nombre de joueurs et de loups. Les tables impaires favorisent nettement le village (10 à 15 points de plus que les paires voisines) ; l'auteur vise 23 à 29 % de victoire humaine à 2 loups. Il précise que ces valeurs ne sont pas représentatives de vraies parties.
- **Aucune source publique** ne donne le poids de la plupart des rôles de l'app (Louveteau, Sœurs et Frères, Servante, Juge bègue, Petite Fille...) ni de statistiques de victoire par rôle.

Conclusion : pour différencier les rôles, il fallait mesurer soi-même. C'est ce que fait `outils/simuler_equilibre.py`.

## Méthode

1. **Simulation** : des joueurs automatiques jouent des parties complètes avec le moteur du jeu (`nouvelle_partie`, `tuer`, `resoudre_nuit`, `vainqueur`). Hypothèses : les loups dévorent et votent au hasard parmi les non-loups ; le village vote au hasard, avec une part `flair` ({d['meta']['flair']}) de votants qui devinent un loup, et suit les informations publiques (loup démasqué, groupes suspects, joueurs blanchis) avec une probabilité de {int(d['meta']['croyance'] * 100)} % par jour ; les informations d'une nuit ne sont publiées que si leur détenteur est encore en vie au matin ; la sorcière utilise son soin au hasard et le salvateur protège au hasard. Sœurs et frères : s'ils sont au moins deux en vie, ils se blanchissent en public et votent ensemble. Montreur d'ours : si l'ours grogne, ses deux voisins deviennent suspects, sinon ils sont blanchis. Petite Fille : un loup et un innocent désignés comme suspects, une chance sur trois d'être dévorée. Corbeau : deux voix de plus sur un suspect, sinon au hasard. Idiot : épargné une fois, il ne vote plus. Bouc émissaire : condamné en cas d'égalité.
2. **Calibrage du `flair`** : choisi pour que les compositions recommandées par l'app (un loup pour quatre joueurs, 8 à 16 joueurs) donnent en moyenne 50 % de victoire au village. C'est une hypothèse : elle suppose que la règle « un quart de loups » est équilibrée en moyenne.
3. **Impact** : régression logistique de la victoire du village sur la taille de la table et le nombre de cartes de chaque rôle, ajustée sur {d['validation']['compositions']} compositions aléatoires de 7 à 18 joueurs ({d['validation']['parties_par_composition']} parties chacune). L'impact affiché est la variation de chance de victoire du village, en points de %, autour d'une table équilibrée (50 %). Validation sur 20 % de compositions mises de côté : pente de calibration {d['validation']['pente_calibration']:.2f} (1 = parfait), erreur quadratique {d['validation']['brier']:.4f} (le bruit à {d['validation']['parties_par_composition']} parties par composition est de l'ordre de 0,01).
4. **Marge** : le même effet mesuré directement, un rôle seul à la place d'un villageois à {d['meta']['table_reference']} ({d['meta']['parties_par_mesure']} parties par rôle, village à {100 * d['meta']['reference_village']:.0f} % sans rôle spécial).
5. **Information** (0 à 100 %) : hausse de la part des votes du village qui condamnent un loup quand le rôle est présent, ramenée au rôle le plus informatif. Réservée aux rôles du village ; sous 8 %, considérée comme du bruit.
6. **Chaos** (0 à 100 %) : nombre moyen d'événements imprévus par partie (morts hors loups et vote, changements de camp, second vote, victoire d'un camp à part, idiot épargné, bouc émissaire, petite fille surprise), ramené au rôle le plus chaotique.

## Résultats

| Rôle | Camp | Impact (pts) | Marge à 14 j. (pts) | Information | Chaos | Référence UW | Remarque |
|---|---|---:|---:|---:|---:|---|---|
{chr(10).join(lignes)}

Accord avec le barème Ultimate Werewolf sur les {n} rôles communs : corrélation de rang de Spearman = **{rho:.2f}**.

### Effets des options (log-cotes, par rapport au réglage par défaut)

| Option | Effet |
|---|---|
| Voyante : chaque nuit / une nuit sur 3 (défaut : une nuit sur 2) | {o['cadence_voyante']['1']:+.2f} / {o['cadence_voyante']['3']:+.2f} |
| Loup Blanc : chaque nuit / une nuit sur 3 | {o['cadence_loup_blanc']['1']:+.2f} / {o['cadence_loup_blanc']['3']:+.2f} |
| Potion de soin en plus (par potion) | {o['potions_sorciere']:+.2f} |
| Potion de mort (par potion) | {o['potions_mort']:+.2f} |
| Égalité : les loups gagnent (au lieu du maire qui départage) | {o['maire_depart_faux']:+.2f} |
| Couple tiré au sort | {o['couple_hasard']:+.2f} |
| Trouple (en plus du couple tiré au sort) | {o['trouple']:+.2f} |

Une log-cote de +0,2 vaut environ +5 points de chance de victoire du village autour de 50 %.

## Ce que les compositions recommandées donnent

| Table | Loups | Chance de victoire du village |
|---|---:|---:|
{ligne_tables}

La parité compte beaucoup (comme l'observe eblong) : les tables paires sont plus dures pour le village, et la règle « un loup pour quatre » gagnerait à être ajustée pour les grandes tables.

## Limites

- **Joueurs automatiques, pas des humains** : aucune stratégie fine, pas de bluff, pas de rôles annoncés. Les rôles d'information sont les plus dépendants de l'hypothèse de croyance (60 %) : si le village suit mal ses informations, le Renard, la Voyante, le Montreur d'ours et les fratries valent moins ; s'il les suit bien, davantage. Le classement des rôles est plus fiable que les valeurs absolues.
- **Fratries** : leur force vient d'une hypothèse (se blanchir en public et voter en bloc, sans que les loups les prennent pour cibles). Si les loups les éliminent en priorité, elles valent moins.
- **Les loups simulés ne se votent jamais entre eux** (dans le jeu, la meute peut désigner l'un des siens) : un sacrifice ou un bluff de la meute n'est pas mesuré.
- **Rôles stratégiques sous-évalués** : Salvateur, Sorcière et Juge bègue sont joués au hasard, un humain en tirerait plus.
- **Voleur** : son effet positif vient d'un artefact de règle (deux cartes laissées au milieu, qui peuvent contenir un loup), pas de son pouvoir.
- **Calibrage** : il pose que les compositions recommandées sont équilibrées en moyenne ; changer ce choix décale toutes les jauges.
- **Incertitude** : l'écart-type d'une mesure de marge est d'environ 0,8 point ({d['meta']['parties_par_mesure']} parties). Les écarts de 1 à 2 points entre rôles ne sont pas significatifs.

Pour refaire les mesures : `uv run --python 3.12 --with numpy python outils/simuler_equilibre.py` (environ 5 minutes), puis `python3 outils/ecrire_doc_equilibre.py`.

## Sources

- [Roles, The Ultimate Werewolf Games](https://ultimatewerewolfgames.tumblr.com/roles) (barème de force, lu directement)
- [Werewolf Statistics, E BLONG](https://www.eblong.com/zarf/werewolf-stats.html) (probabilités sous jeu aléatoire)
- [Règles d'équilibrage, forum Thiercelieux](https://thiercelieux.forumpro.fr/t4366-regles-d-equilibrage-a-l-attention-de-tous-les-mj) (principes d'équilibrage)
"""
(RACINE / "docs" / "equilibre-roles.md").write_text(doc, encoding="utf-8")
print("docs/equilibre-roles.md écrit")
