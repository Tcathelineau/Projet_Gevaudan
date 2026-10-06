# Équilibre des rôles : classement proposé

Ce fichier attribue à chaque rôle trois notes. Elles serviront à afficher, dans l'écran de composition, trois compteurs qui donnent une idée de l'équilibre de la partie avant de la lancer. **Valeurs à relire et à ajuster** après quelques parties : les compteurs sont déjà branchés dans l'écran de composition (`src/loup_garou/equilibre.py`).

## Les trois notes

| Note | Échelle | Ce qu'elle mesure |
|---|---|---|
| **Force** | entier, positif = avantage village, négatif = avantage loups | Poids du rôle dans le rapport de force. Le compteur d'équilibre est la somme des forces de toute la table. |
| **Information** | 0 à 5 | Quantité d'information fiable que le rôle produit (pour son camp). 0 = aucune, 5 = une vision chaque nuit. |
| **Chaos** | 0 à 5 | Imprévisibilité que le rôle ajoute : changement de camp, camp à part, mort qui en entraîne une autre, victoire inattendue. 0 = aucun effet. |

La force est volontairement distincte de l'information : la Voyante est forte *parce qu'*elle informe, mais le Chasseur est fort sans informer. Le chaos n'a pas de camp : un rôle chaotique rend la partie moins lisible pour tout le monde.

## D'où viennent les chiffres

- **Force, rôles marqués ●** : valeurs du système de points d'*Ultimate Werewolf* (Bezier Games), l'échelle la plus répandue pour équilibrer un paquet : on additionne les valeurs, un total proche de 0 donne une partie équilibrée. J'ai retrouvé les mêmes valeurs dans deux pages indépendantes (fil BoardGameGeek sur les valeurs de rôles, via un résumé de recherche, et la page Rôles de The Ultimate Werewolf Games). Seule la page Rôles a été lue directement ; la page BoardGameGeek était inaccessible.
- **Force, rôles marqués ○** : **estimation de ma part**, par analogie avec le rôle le plus proche d'*Ultimate Werewolf*. Aucune source ne les chiffre (le wiki français des Loups-garous de Thiercelieux décrit les rôles mais ne les pondère pas, et il ne m'a pas été accessible en détail). À corriger après quelques parties.
- **Information et chaos** : toujours des estimations de ma part, pour tous les rôles. Aucune source ne les mesure.

## Rôles présents dans l'app

| Rôle | Camp | Force | Info | Chaos | Origine | Remarque |
|---|---|---:|---:|---:|---|---|
| 🐺 Loup-Garou | Loups | **-6** | 1 | 0 | ● Werewolf -6 | Connaît la meute, tue chaque nuit (dès la deuxième). |
| 🧑‍🌾 Villageois | Village | **+1** | 0 | 0 | ● Villager +1 | Référence de la table. |
| 🔮 Voyante | Village | **+7** | 5 | 0 | ● Seer +7 | Valeur pour une vision chaque nuit. Par défaut l'app la limite à une nuit sur deux : voir « Ajustements ». |
| 🧪 Sorcière | Village | **+3** | 1 | 2 | ○ Witch +4, retranché 1 | Dans l'app elle soigne à l'aveugle (elle ignore la victime), donc un cran sous la référence. Chaos 2 car elle peut tuer avec les potions de mort optionnelles. |
| 🏹 Cupidon | Village | **-3** | 0 | 4 | ● Cupid -3 | Le couple peut mêler les camps et devenir un camp à part. |
| 🔫 Chasseur | Village | **+3** | 0 | 1 | ● Hunter +3 | Menace dissuasive pour les loups. |
| 🛡️ Salvateur | Village | **+3** | 0 | 1 | ● Bodyguard +3 | Ne protège jamais le même joueur deux nuits de suite. |
| 🦊 Renard | Village | **+3** | 3 | 0 | ○ P.I. +3 | Flaire un groupe de trois joueurs. Perd son flair sans loup dans le groupe, ce qui est déjà une information. |
| 🧒 Enfant sauvage | Village | **-1** | 0 | 3 | ○ proche de Doppelgänger -2 | Devient loup si son mentor meurt : un loup potentiel que le village ne maîtrise pas. |
| 🃏 Voleur | Village | **-2** | 0 | 4 | ○ proche de Doppelgänger -2 / Drunk -3 | Peut devenir loup ; ajoute deux cartes inconnues au milieu. |
| 🌕 Loup Blanc | Loups, solitaire | **-5** | 1 | 4 | ● Lone Wolf -5 | Gagne seul, tue aussi des loups : il fragilise la meute autant que le village. |
| 🐕 Chien-Loup | Au choix | **0** | 0 | 2 | ○ estimé | Choisit son camp en secret : il s'équilibre de lui-même, mais compte comme un loup caché s'il choisit la meute. |
| 🐶 Louveteau | Loups | **-8** | 1 | 2 | ● Wolf Cub -8 | Sa mort double les victimes de la meute la nuit suivante. |
| 👭 Sœur (×2 cartes) | Village | **+2** par carte | 2 | 0 | ● Mason +2 | Les deux sœurs se connaissent : +4 au total. |
| 👬 Frère (×3 cartes) | Village | **+2** par carte | 2 | 0 | ● Mason +2 | Les trois frères se connaissent : +6 au total, ce qui pèse autant qu'une Voyante. À surveiller en jouant. |
| 🧹 Servante dévouée | Village | **+2** | 0 | 3 | ○ estimé | Reprend en secret, la nuit suivante, le rôle d'un condamné ; le panneau annonce son intervention. |
| ⚖️ Juge bègue | Village | **+2** | 0 | 3 | ○ estimé | Un second vote, une fois par partie : arme à double tranchant pour le village. |

## Rôles à venir (import prévu)

Les pouvoirs ci-dessous sont **ma compréhension générale de ces rôles, non vérifiée** : à confirmer au moment de l'import avec les règles que tu retiens.

| Rôle | Camp | Force | Info | Chaos | Origine | Remarque |
|---|---|---:|---:|---:|---|---|
| 👧 Petite Fille | Village | **+3** | 4 | 1 | ○ estimé | Espionne les loups la nuit, au risque de se faire repérer et dévorer. |
| 🐻 Montreur d'ours | Village | **+2** | 3 | 0 | ○ estimé (P.I. +3 en moins fort) | Info gratuite mais limitée aux voisins. |
| 🐦‍⬛ Corbeau | Village | **+2** | 0 | 3 | ○ estimé (Mayor +2) | Pèse sur le vote en désignant un suspect. |
| 🕵️ Détective | Village | **+3** | 4 | 1 | ○ estimé (P.I. +3) | Enquête sur les camps de joueurs. |
| 😇 Ange | Solitaire | **0** | 0 | 4 | ○ estimé (Tanner +1) | Gagne s'il est éliminé tôt, sinon redevient un villageois. |
| 🗡️ Assassin | Solitaire | **-4** | 0 | 5 | ○ estimé (entre Lone Wolf -5 et Vampire -7) | Tueur solitaire : menace les deux camps, plus souvent le village. |
| 🔥 Pyromane | Solitaire | **-4** | 0 | 5 | ○ estimé | Même logique que l'Assassin. |

## Les trois compteurs de l'écran de composition

1. **Équilibre** : somme des forces de la table, affichée par un curseur entre « loups » et « village », sans chiffre ni libellé. L'échelle dépend de la table : la demi-largeur de la jauge vaut 2 points de force par joueur (au moins 10). Une Voyante (+5 à +7) déplace donc le curseur d'environ 25 % de la demi-jauge à 7 joueurs, et d'environ 15 % à 18 joueurs. Échelle à ajuster à l'usage (les archives de `historique/` donnent déjà le vainqueur et la composition).
2. **Information** : somme des notes d'information divisée par le nombre de joueurs : faible sous 0,4, moyenne jusqu'à 0,9, forte au-delà.
3. **Chaos** : même calcul : calme sous 0,3, mouvementée jusqu'à 0,8, imprévisible au-delà.

Ces compteurs sont implémentés dans `src/loup_garou/equilibre.py` (les valeurs y sont recopiées : en cas de changement, modifier les deux). Les seuils d'information et de chaos ont été choisis en regardant des compositions types, sans autre calibrage.

### Vérification sur les compositions recommandées

> Le tableau ci-dessous compte la Voyante à +7 (une vision par nuit). L'app la limite par défaut à une nuit sur deux (+5) : avec ce réglage, chaque colonne perd 2 points (par exemple 12 joueurs : -5, 16 joueurs : -8).

Avec ces valeurs, la composition suggérée par l'app (`composition_recommandee`) donne :

| Joueurs | 6 | 8 | 10 | 12 | 14 | 15 | 16 | 18 | 20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Loups | 1 | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 5 |
| Équilibre | +5 | 0 | +2 | -3 | -1 | 0 | -6 | -4 | -9 |

Entre 8 et 15 joueurs, la suggestion reste dans la zone équilibrée. Elle penche vers les loups chaque fois qu'un loup de plus s'ajoute (16 et 20 joueurs) : c'est un indice que la règle « un loup pour quatre joueurs » est un peu généreuse pour les grandes tables, ou qu'il y faut plus de rôles spéciaux. À petite table (6 à 7), un seul loup donne un avantage net au village.

## Ajustements liés aux options (à décider)

Plusieurs options de partie modifient la force d'un rôle. Proposition, à valider :

| Option | Effet sur la force |
|---|---|
| Cadence de la Voyante : chaque nuit / une nuit sur 2 / une nuit sur 3 | +7 / +5 / +4 (valeurs de ma part) |
| Cadence du Loup Blanc : chaque nuit / une nuit sur 2 / une nuit sur 3 | -6 / -5 / -4 |
| Potions de soin supplémentaires | +1 par potion en plus |
| Potions de mort (0 par défaut) | +1 par potion (arme pour le village, mais chaos +1) |
| Couple tiré au hasard sans Cupidon / trouple | chaos +2 / +3 |
| Égalité : « les loups gagnent » au lieu de « le maire départage » | -2 sur la table |

## Limites

- Une somme proche de 0 ne garantit pas une partie équilibrée : les rôles interagissent (Cupidon et un loup amoureux, Chasseur et Salvateur…) et le niveau des joueurs pèse plus que 2 ou 3 points.
- Les valeurs d'*Ultimate Werewolf* sont pensées pour un jeu avec maître du jeu et une seule soirée. Ici, la partie dure plusieurs jours et les morts restent des esprits frappeurs qui glanent de l'information : le village est probablement un peu plus fort que ces chiffres ne le disent. À vérifier en jouant.

## Sources

- [Ultimate Werewolf Role Values (BoardGameGeek)](https://boardgamegeek.com/thread/879524/ultimate-werewolf-role-values) (page inaccessible, valeurs lues par recoupement)
- [Roles, The Ultimate Werewolf Games](https://ultimatewerewolfgames.tumblr.com/roles) (lue directement)
- [Liste des rôles, wiki Loup-Garou (Fandom)](https://loupgarou.fandom.com/fr/wiki/Liste_des_r%C3%B4les) (descriptions des rôles ; page non lue en détail)
