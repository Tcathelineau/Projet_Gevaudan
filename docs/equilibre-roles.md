# Équilibre des rôles : méthode et mesures

Les jauges de l'écran de composition et les dalles de la page Documentation viennent de ce fichier. Elles ont été **recalculées** : la première version reposait sur le barème d'*Ultimate Werewolf* complété par mes estimations, ce qui regroupait beaucoup de rôles autour de +3. Les valeurs sont maintenant **mesurées par simulation** avec le vrai moteur du jeu.

## Ce que dit la littérature (et ce qu'elle ne dit pas)

- **Ultimate Werewolf (Bezier Games)** : seul barème chiffré que j'ai trouvé, en entiers (Seer +7, Witch +4, Hunter, Bodyguard, Priest, P.I. et Prince tous à +3, Cupid -3, Lone Wolf -5, Werewolf -6, Wolf Cub -8). Le regroupement à +3 vient donc de la source elle-même, pas seulement de mes estimations. Il ne couvre qu'une partie des rôles de l'app, avec leurs règles à lui.
- **Forums français (forum Thiercelieux, lu ; Trictrac, vu seulement par un résumé de recherche)** : des principes sans chiffres par rôle (un quart de loups, ne pas doubler les rôles de même puissance, le Chien-Loup équilibre la partie).
- **Andrew Plotkin (eblong.com, statistiques du loup-garou)** : probabilités de victoire du village sous jeu entièrement aléatoire, par nombre de joueurs et de loups. Les tables impaires favorisent nettement le village (10 à 15 points de plus que les paires voisines) ; l'auteur vise 23 à 29 % de victoire humaine à 2 loups. Il précise que ces valeurs ne sont pas représentatives de vraies parties.
- **Aucune source publique** ne donne le poids de la plupart des rôles de l'app (Louveteau, Sœurs et Frères, Servante, Juge bègue...) ni de statistiques de victoire par rôle.

Conclusion : pour différencier les rôles, il fallait mesurer soi-même. C'est ce que fait `outils/simuler_equilibre.py`.

## Méthode

1. **Simulation** : des joueurs automatiques jouent des parties complètes avec le moteur du jeu (`nouvelle_partie`, `tuer`, `resoudre_nuit`, `vainqueur`). Hypothèses : les loups dévorent et votent au hasard parmi les non-loups ; le village vote au hasard, avec une part `flair` (0.092) de votants qui devinent un loup, et suit les informations publiques (loup démasqué, groupe du renard, joueurs blanchis) avec une probabilité de 60 % par jour ; les informations d'une nuit ne sont publiées que si leur détenteur est encore en vie au matin ; la sorcière utilise son soin au hasard et le salvateur protège au hasard.
2. **Calibrage du `flair`** : choisi pour que les compositions recommandées par l'app (un loup pour quatre joueurs, 8 à 16 joueurs) donnent en moyenne 50 % de victoire au village. C'est une hypothèse : elle suppose que la règle « un quart de loups » est équilibrée en moyenne.
3. **Impact** : régression logistique de la victoire du village sur la taille de la table et le nombre de cartes de chaque rôle, ajustée sur 2400 compositions aléatoires de 7 à 18 joueurs (25 parties chacune). L'impact affiché est la variation de chance de victoire du village, en points de %, autour d'une table équilibrée (50 %). Validation sur 20 % de compositions mises de côté : pente de calibration 1.02 (1 = parfait), erreur quadratique 0.0068 (le bruit à 25 parties par composition est de l'ordre de 0,01).
4. **Marge** : le même effet mesuré directement, un rôle seul à la place d'un villageois à 14 joueurs, 3 loups (5000 parties par rôle, village à 23 % sans rôle spécial).
5. **Information** (0 à 100 %) : hausse de la part des votes du village qui condamnent un loup quand le rôle est présent, ramenée au rôle le plus informatif (le Renard = 100 %). Réservée aux rôles du village ; sous 8 %, considérée comme du bruit.
6. **Chaos** (0 à 100 %) : nombre moyen d'événements imprévus par partie (morts hors loups et vote, changements de camp, second vote, victoire d'un camp à part), ramené au rôle le plus chaotique (le Loup Blanc = 100 %).

## Résultats

| Rôle | Camp | Impact (pts) | Marge à 14 j. (pts) | Information | Chaos | Référence UW | Remarque |
|---|---|---:|---:|---:|---:|---|---|
| 🦊 Renard | Village | **+15** | +18 | 100 % | 0 % | P.I. +3 | Son groupe suspect concentre les votes du village, mais la simulation le suppose bien suivi (voir les limites). |
| 🔮 Voyante | Village | **+12** | +12 | 69 % | 0 % | Seer +7 | Une vision une nuit sur deux (réglage par défaut). |
| 🃏 Voleur | Village | **+12** | +8 | 0 % | 0 % | - | Effet dû aux deux cartes laissées au milieu : un loup peut y rester, ce qui retire un loup de la table. |
| 🔫 Chasseur | Village | **+9** | +10 | 0 % | 53 % | Hunter +3 | Sa balle touche un loup plus souvent que le hasard quand le village a des pistes. |
| 🧪 Sorcière | Village | **+5** | +6 | 0 % | 0 % | Witch +4 | Soin à l'aveugle, une potion. |
| ⚖️ Juge bègue | Village | **+5** | +8 | 0 % | 66 % | - | Un second vote élimine un joueur de plus, en moyenne plus souvent un loup qu'un innocent. |
| 🏹 Cupidon | Village | **+4** | +8 | 0 % | 63 % | Cupid -3 | Le couple est tiré au hasard : un couple mixte peut gêner les loups autant que le village. |
| 🛡️ Salvateur | Village | **+3** | +4 | 0 % | 0 % | Bodyguard +3 | Protection au hasard : il sauve surtout par chance. |
| 👬 Frère (par carte) | Village | **+2** | +2 | 8 % | 0 % | Mason +2 | Par carte. Les trois frères se savent innocents. |
| 👭 Sœur (par carte) | Village | **+0** | +1 | 0 % | 0 % | Mason +2 | Par carte. Deux innocents qui se connaissent : très peu d'effet mesurable. |
| 🧹 Servante dévouée | Village | **+0** | +0 | 0 % | 51 % | - | Ne reprend que le rôle d'un condamné du village : elle ne change presque rien. |
| 🧒 Enfant sauvage | Village | **-13** | -8 | 0 % | 28 % | - | Devient loup si son mentor meurt. |
| 🐕 Chien-Loup | Village | **-15** | -9 | 0 % | 33 % | - | Camp tiré au hasard dans la simulation : environ un loup une fois sur deux. |
| 🌕 Loup Blanc | Loups | **-22** | -11 | 0 % | 100 % | Lone Wolf -5 | Il dévore ses frères en fin de partie (dès qu'il reste 4 villageois ou moins) : il affaiblit la meute plus qu'il ne gêne le village. |
| 🐺 Loup-Garou | Loups | **-33** | -18 | 0 % | 0 % | Werewolf -6 | Référence des loups : un loup de plus fait chuter la victoire du village. |
| 🐶 Louveteau | Loups | **-38** | -18 | 0 % | 14 % | Wolf Cub -8 | Un loup de plus, et sa mort double les victimes de la nuit suivante. |

Accord avec le barème Ultimate Werewolf sur les 10 rôles communs : corrélation de rang de Spearman = **0,87**. Écarts notables : le Cupidon (UW -3, ici +4) et le Renard (UW +3, ici +15, le plus fort du village) ; le Chasseur ressort plus haut que son +3.

### Effets des options (log-cotes, par rapport au réglage par défaut)

| Option | Effet |
|---|---|
| Voyante : chaque nuit / une nuit sur 3 (défaut : une nuit sur 2) | +0.33 / -0.19 |
| Loup Blanc : chaque nuit / une nuit sur 3 | +0.25 / -0.84 |
| Potion de soin en plus (par potion) | +0.05 |
| Potion de mort (par potion) | +0.08 |
| Égalité : les loups gagnent (au lieu du maire qui départage) | +0.03 |
| Couple tiré au sort | +0.35 |
| Trouple (en plus du couple tiré au sort) | +0.05 |

Une log-cote de +0,2 vaut environ +5 points de chance de victoire du village autour de 50 %.

## Ce que les compositions recommandées donnent

La parité compte beaucoup : à 16 joueurs, la règle « un loup pour quatre » en met 4, et le village tombe à 30 %. À 8 et 10 joueurs il est à 56 et 65 %, à 12 joueurs à 42 %. Les tables paires sont plus dures pour le village (comme l'observe eblong), et la règle du quart gagnerait à être ajustée pour les grandes tables.

## Limites

- **Joueurs automatiques, pas des humains** : aucune stratégie fine, pas de bluff, pas de rôles annoncés. Les rôles d'information sont les plus dépendants de l'hypothèse de croyance (60 %) : si le village suit mal ses informations, le Renard et la Voyante valent moins ; s'il les suit bien, davantage. Le classement des rôles est plus fiable que les valeurs absolues.
- **Les loups simulés ne se votent jamais entre eux** (dans le jeu, la meute peut désigner l'un des siens) : un sacrifice ou un bluff de la meute n'est pas mesuré.
- **Rôles stratégiques sous-évalués** : Salvateur, Sorcière et Juge bègue sont joués au hasard, un humain en tirerait plus.
- **Voleur** : son effet positif vient d'un artefact de règle (deux cartes laissées au milieu, qui peuvent contenir un loup), pas de son pouvoir.
- **Calibrage** : il pose que les compositions recommandées sont équilibrées en moyenne ; changer ce choix décale toutes les jauges.
- **Incertitude** : l'écart-type d'une mesure de marge est d'environ 0,8 point (5 000 parties). Les écarts de 1 à 2 points entre rôles ne sont pas significatifs.

Pour refaire les mesures : `uv run --python 3.12 --with numpy python outils/simuler_equilibre.py` (environ 3 minutes). Le fichier `src/loup_garou/assets/equilibre.json` est alors réécrit.

## Sources

- [Roles, The Ultimate Werewolf Games](https://ultimatewerewolfgames.tumblr.com/roles) (barème de force, lu directement)
- [Werewolf Statistics, E BLONG](https://www.eblong.com/zarf/werewolf-stats.html) (probabilités sous jeu aléatoire)
- [Règles d'équilibrage, forum Thiercelieux](https://thiercelieux.forumpro.fr/t4366-regles-d-equilibrage-a-l-attention-de-tous-les-mj) (principes d'équilibrage)
