# Équilibre des rôles : méthode et mesures

Les jauges de l'écran de composition et les dalles de la page Documentation viennent de ce fichier. Les valeurs sont **mesurées par simulation** avec le vrai moteur du jeu (fichier généré par `outils/ecrire_doc_equilibre.py` à partir de `assets/equilibre.json`).

**Deuxième passe** : les sœurs et les frères étaient sous-évalués (la première simulation ne leur faisait que s'éviter entre eux) ; ils se blanchissent maintenant en public et votent en bloc. Les nouveaux rôles (Montreur d'ours, Petite Fille, Corbeau, Idiot du village, Bouc émissaire) sont mesurés dans la même simulation. Pour les rôles à plusieurs cartes, l'impact est donné par carte, avec le total pour l'ensemble.

## Ce que dit la littérature (et ce qu'elle ne dit pas)

- **Ultimate Werewolf (Bezier Games)** : seul barème chiffré que j'ai trouvé, en entiers (Seer +7, Witch +4, Hunter, Bodyguard, Priest, P.I. et Prince tous à +3, Cupid -3, Lone Wolf -5, Werewolf -6, Wolf Cub -8). Le regroupement à +3 vient de la source elle-même. Il ne couvre qu'une partie des rôles de l'app, avec leurs règles à lui.
- **Forums français (forum Thiercelieux, lu ; Trictrac, vu seulement par un résumé de recherche)** : des principes sans chiffres par rôle (un quart de loups, ne pas doubler les rôles de même puissance, le Chien-Loup équilibre la partie).
- **Andrew Plotkin (eblong.com, statistiques du loup-garou)** : probabilités de victoire du village sous jeu entièrement aléatoire, par nombre de joueurs et de loups. Les tables impaires favorisent nettement le village (10 à 15 points de plus que les paires voisines) ; l'auteur vise 23 à 29 % de victoire humaine à 2 loups. Il précise que ces valeurs ne sont pas représentatives de vraies parties.
- **Aucune source publique** ne donne le poids de la plupart des rôles de l'app (Louveteau, Sœurs et Frères, Servante, Juge bègue, Petite Fille...) ni de statistiques de victoire par rôle.

Conclusion : pour différencier les rôles, il fallait mesurer soi-même. C'est ce que fait `outils/simuler_equilibre.py`.

## Méthode

1. **Simulation** : des joueurs automatiques jouent des parties complètes avec le moteur du jeu (`nouvelle_partie`, `tuer`, `resoudre_nuit`, `vainqueur`). Hypothèses : les loups dévorent et votent au hasard parmi les non-loups ; le village vote au hasard, avec une part `flair` (0.092) de votants qui devinent un loup, et suit les informations publiques (loup démasqué, groupes suspects, joueurs blanchis) avec une probabilité de 60 % par jour ; les informations d'une nuit ne sont publiées que si leur détenteur est encore en vie au matin ; la sorcière utilise son soin au hasard et le salvateur protège au hasard. Sœurs et frères : s'ils sont au moins deux en vie, ils se blanchissent en public et votent ensemble. Montreur d'ours : si l'ours grogne, ses deux voisins deviennent suspects, sinon ils sont blanchis. Petite Fille : un loup et un innocent désignés comme suspects, une chance sur trois d'être dévorée. Corbeau : deux voix de plus sur un suspect, sinon au hasard. Idiot : épargné une fois, il ne vote plus. Bouc émissaire : condamné en cas d'égalité.
2. **Calibrage du `flair`** : choisi pour que les compositions recommandées par l'app (un loup pour quatre joueurs, 8 à 16 joueurs) donnent en moyenne 50 % de victoire au village. C'est une hypothèse : elle suppose que la règle « un quart de loups » est équilibrée en moyenne.
3. **Impact** : régression logistique de la victoire du village sur la taille de la table et le nombre de cartes de chaque rôle, ajustée sur 3000 compositions aléatoires de 7 à 18 joueurs (25 parties chacune). L'impact affiché est la variation de chance de victoire du village, en points de %, autour d'une table équilibrée (50 %). Validation sur 20 % de compositions mises de côté : pente de calibration 1.00 (1 = parfait), erreur quadratique 0.0073 (le bruit à 25 parties par composition est de l'ordre de 0,01).
4. **Marge** : le même effet mesuré directement, un rôle seul à la place d'un villageois à 14 joueurs, 3 loups (6000 parties par rôle, village à 22 % sans rôle spécial).
5. **Information** (0 à 100 %) : hausse de la part des votes du village qui condamnent un loup quand le rôle est présent, ramenée au rôle le plus informatif. Réservée aux rôles du village ; sous 8 %, considérée comme du bruit.
6. **Chaos** (0 à 100 %) : nombre moyen d'événements imprévus par partie (morts hors loups et vote, changements de camp, second vote, victoire d'un camp à part, idiot épargné, bouc émissaire, petite fille surprise), ramené au rôle le plus chaotique.

## Résultats

| Rôle | Camp | Impact (pts) | Marge à 14 j. (pts) | Information | Chaos | Référence UW | Remarque |
|---|---|---:|---:|---:|---:|---|---|
| 🃏 Voleur | Village | **+10** | +9 | 0 % | 0 % | - | Effet dû aux deux cartes laissées au milieu : un loup peut y rester, ce qui retire un loup de la table. |
| 🐻 Montreur d'ours | Village | **+10** | +18 | 91 % | 0 % | - | Une information chaque matin, sans risque pour lui : l'ours désigne les deux voisins suspects. |
| 🔮 Voyante | Village | **+10** | +13 | 70 % | 0 % | Seer +7 | Une vision une nuit sur deux (réglage par défaut). |
| 🔫 Chasseur | Village | **+10** | +10 | 0 % | 53 % | Hunter +3 | Sa balle touche un loup plus souvent que le hasard quand le village a des pistes. |
| 🦊 Renard | Village | **+7** | +18 | 91 % | 0 % | P.I. +3 | Son groupe suspect concentre les votes du village, mais la simulation le suppose bien suivi (voir les limites). |
| 👬 Frère (par carte) | Village | **+6** (+18 les 3) | +7 | 32 % | 0 % | Mason +2 | Par carte. Les frères se savent innocents, se blanchissent en public et votent en bloc. |
| ⚖️ Juge bègue | Village | **+6** | +8 | 0 % | 66 % | - | Un second vote élimine un joueur de plus, en moyenne plus souvent un loup qu'un innocent. |
| 👧 Petite Fille | Village | **+6** | +15 | 100 % | 47 % | - | Information forte (un loup parmi deux silhouettes) payée d'une chance sur trois d'être dévorée. |
| 🧪 Sorcière | Village | **+5** | +6 | 0 % | 0 % | Witch +4 | Soin à l'aveugle, une potion. |
| 👭 Sœur (par carte) | Village | **+4** (+8 les 2) | +5 | 22 % | 0 % | Mason +2 | Par carte. Les sœurs se savent innocentes, se blanchissent en public et votent en bloc. |
| 🏹 Cupidon | Village | **+4** | +7 | 0 % | 63 % | Cupid -3 | Le couple est tiré au hasard : un couple mixte peut gêner les loups autant que le village. |
| 🐦 Corbeau | Village | **+2** | +2 | 11 % | 0 % | Troublemaker +2 | Deux voix de plus, désignées au hasard ou sur un suspect : un coup de pouce, pas une arme. |
| 🛡️ Salvateur | Village | **+2** | +3 | 0 % | 0 % | Bodyguard +3 | Protection au hasard : il sauve surtout par chance. |
| 🤡 Idiot du village | Village | **+0** | +2 | 0 % | 21 % | Village Idiot +2 | Survit à une condamnation : il gaspille un vote du village sans l'éclairer. |
| 🧹 Servante dévouée | Village | **+0** | +0 | 0 % | 51 % | - | Ne reprend que le rôle d'un condamné du village : elle ne change presque rien. |
| 🐐 Bouc émissaire | Village | **-6** | -6 | 0 % | 46 % | - | Handicap pour le village : une égalité des voix sacrifie un innocent. |
| 🧒 Enfant sauvage | Village | **-13** | -8 | 0 % | 28 % | - | Devient loup si son mentor meurt. |
| 🐕 Chien-Loup | Village | **-14** | -9 | 0 % | 33 % | - | Camp tiré au hasard dans la simulation : environ un loup une fois sur deux. |
| 🌕 Loup Blanc | Loups | **-20** | -10 | 0 % | 100 % | Lone Wolf -5 | Il dévore ses frères en fin de partie (dès qu'il reste 4 villageois ou moins) : il affaiblit la meute plus qu'il ne gêne le village. |
| 🐺 Loup-Garou | Loups | **-31** | -18 | 0 % | 0 % | Werewolf -6 | Référence des loups : un loup de plus fait chuter la victoire du village. |
| 🐶 Louveteau | Loups | **-37** | -18 | 0 % | 14 % | Wolf Cub -8 | Un loup de plus, et sa mort double les victimes de la nuit suivante. |

Accord avec le barème Ultimate Werewolf sur les 13 rôles communs : corrélation de rang de Spearman = **0.74**.

### Effets des options (log-cotes, par rapport au réglage par défaut)

| Option | Effet |
|---|---|
| Voyante : chaque nuit / une nuit sur 3 (défaut : une nuit sur 2) | +0.32 / -0.22 |
| Loup Blanc : chaque nuit / une nuit sur 3 | +0.22 / -0.83 |
| Potion de soin en plus (par potion) | +0.05 |
| Potion de mort (par potion) | +0.08 |
| Égalité : les loups gagnent (au lieu du maire qui départage) | +0.04 |
| Couple tiré au sort | +0.35 |
| Trouple (en plus du couple tiré au sort) | +0.06 |

Une log-cote de +0,2 vaut environ +5 points de chance de victoire du village autour de 50 %.

## Ce que les compositions recommandées donnent

| Table | Loups | Chance de victoire du village |
|---|---:|---:|
| 8 joueurs | 2 | 56 % |
| 10 joueurs | 2 | 65 % |
| 12 joueurs | 3 | 44 % |
| 14 joueurs | 3 | 54 % |
| 16 joueurs | 4 | 33 % |

La parité compte beaucoup (comme l'observe eblong) : les tables paires sont plus dures pour le village, et la règle « un loup pour quatre » gagnerait à être ajustée pour les grandes tables.

## Limites

- **Joueurs automatiques, pas des humains** : aucune stratégie fine, pas de bluff, pas de rôles annoncés. Les rôles d'information sont les plus dépendants de l'hypothèse de croyance (60 %) : si le village suit mal ses informations, le Renard, la Voyante, le Montreur d'ours et les fratries valent moins ; s'il les suit bien, davantage. Le classement des rôles est plus fiable que les valeurs absolues.
- **Fratries** : leur force vient d'une hypothèse (se blanchir en public et voter en bloc, sans que les loups les prennent pour cibles). Si les loups les éliminent en priorité, elles valent moins.
- **Les loups simulés ne se votent jamais entre eux** (dans le jeu, la meute peut désigner l'un des siens) : un sacrifice ou un bluff de la meute n'est pas mesuré.
- **Rôles stratégiques sous-évalués** : Salvateur, Sorcière et Juge bègue sont joués au hasard, un humain en tirerait plus.
- **Voleur** : son effet positif vient d'un artefact de règle (deux cartes laissées au milieu, qui peuvent contenir un loup), pas de son pouvoir.
- **Calibrage** : il pose que les compositions recommandées sont équilibrées en moyenne ; changer ce choix décale toutes les jauges.
- **Incertitude** : l'écart-type d'une mesure de marge est d'environ 0,8 point (6000 parties). Les écarts de 1 à 2 points entre rôles ne sont pas significatifs.

Pour refaire les mesures : `uv run --python 3.12 --with numpy python outils/simuler_equilibre.py` (environ 5 minutes), puis `python3 outils/ecrire_doc_equilibre.py`.

## Sources

- [Roles, The Ultimate Werewolf Games](https://ultimatewerewolfgames.tumblr.com/roles) (barème de force, lu directement)
- [Werewolf Statistics, E BLONG](https://www.eblong.com/zarf/werewolf-stats.html) (probabilités sous jeu aléatoire)
- [Règles d'équilibrage, forum Thiercelieux](https://thiercelieux.forumpro.fr/t4366-regles-d-equilibrage-a-l-attention-de-tous-les-mj) (principes d'équilibrage)
