<p align="center">
  <img src="docs/banniere.svg" alt="Projet Gévaudan : un village endormi sous la pleine lune" width="100%">
</p>

<p align="center">
  <strong>Un loup-garou grandeur nature, mené par une application.</strong><br>
  Pas de cartes physiques, pas de maître du jeu : l'application distribue les rôles, mène les nuits, compte les morts et proclame le vainqueur.
</p>

---

## 🌙 Le jeu

Un village est hanté par des loups-garous. Chaque nuit, ils dévorent un villageois ; à chaque conseil, le village vote pour éliminer un suspect. Les villageois gagnent s'ils débusquent tous les loups, les loups gagnent s'ils deviennent plus nombreux que les autres (ou aussi nombreux, si l'un d'eux est maire).

Le jeu se vit **grandeur nature**, sur plusieurs heures ou plusieurs jours : l'application gère les rôles, les nuits et les votes, mais l'essentiel se passe entre les joueurs.

- **Le rythme des conseils est libre** : les joueurs conviennent ensemble de leur fréquence (tous les jours, toutes les 12 h, toutes les 6 h…). L'application lance un conseil quand le groupe le décide.
- **Le jeu se joue en dehors des conseils** : on discute, on forme des alliances, on cherche à démasquer les loups.
- **Les morts deviennent des esprits frappeurs** : ils continuent de discuter avec les autres et de glaner des informations, mais ne votent pas et ne parlent pas au conseil.
- **Les esprits ne vont jamais vers les vivants** pour parler du jeu : ce sont les vivants qui viennent les interroger.

À chaque tour de nuit, l'application demande de passer l'appareil au joueur concerné, en deux étapes, pour que personne ne voie la carte d'un autre.

### Une partie en un coup d'œil

1. **Composition** : on saisit les pseudos et on règle le nombre de loups et de rôles spéciaux. Le reste de la table est complété en villageois.
2. **La nuit tombe** : chaque joueur, à son tour, découvre sa carte et agit en secret (dévorer, sonder, protéger, soigner…).
3. **Le village se réveille** : un panneau d'affichage annonce les morts de la nuit et le camp qu'ils avaient.
4. **Élection du maire** (au premier jour) puis **conseil du village** : on débat, l'app enregistre le vote et révèle si l'éliminé était loup ou non.
5. Retour à la nuit, jusqu'à la victoire d'un camp.

## 🃏 Les rôles

| | Rôle | Camp | Pouvoir |
|---|---|---|---|
| 🐺 | **Loup-Garou** | Loups | Se retrouve avec la meute et vote chaque nuit (dès la deuxième) pour dévorer un villageois. |
| 🧑‍🌾 | **Villageois** | Village | Aucun pouvoir : il dort, débat et vote le jour. |
| 🔮 | **Voyante** | Village | Une nuit sur deux par défaut, sonde un joueur et découvre son rôle. |
| 🧪 | **Sorcière** | Village | Dispose de potions de soin (une par défaut) pour sauver la victime des loups, sans savoir qui a été désigné : elle choisit à l'aveugle de l'utiliser ou non. En option, elle a aussi des potions de mort pour empoisonner un joueur (ni le salvateur ni le soin ne l'en protègent). |
| 🏹 | **Cupidon** | Village | La première nuit, lie deux joueurs par l'amour (lui compris). |
| 🔫 | **Chasseur** | Village | À sa mort, tire une dernière balle sur le joueur de son choix. |
| 🛡️ | **Salvateur** | Village | Protège un joueur chaque nuit, jamais le même deux nuits de suite. |
| 🧒 | **Enfant sauvage** | Village | Choisit un mentor ; si celui-ci meurt, il devient loup-garou. |
| 🃏 | **Voleur** | Village | Deux cartes restent au milieu de la table : il peut prendre le rôle de l'une d'elles. |
| 🦊 | **Renard** | Village | Dès la deuxième nuit, flaire trois joueurs et apprend si un loup s'y cache ; sans loup, il perd son flair. |
| 🌕 | **Loup Blanc** | Loups, solitaire | Une nuit sur deux, peut dévorer l'un de ses frères ; il gagne seul. |
| 🐕 | **Chien-Loup** | Au choix | Choisit son camp en secret la première nuit : villageois ou loup-garou. |
| 🐶 | **Louveteau** | Loups | Loup comme les autres ; s'il meurt, la meute dévore deux victimes la nuit suivante. |
| 👭 | **Sœurs** (2 cartes) | Village | Elles se connaissent dès la première nuit. |
| 👬 | **Frères** (3 cartes) | Village | Ils se connaissent dès la première nuit. |
| 🧹 | **Servante dévouée** | Village | La nuit qui suit un vote, elle peut reprendre en secret le rôle du condamné ; le panneau d'affichage annonce le lendemain qu'elle est intervenue. |
| ⚖️ | **Juge bègue** | Village | Une fois par partie, exige (de nuit, en secret) un second vote du village au conseil suivant. |

## 📜 Les règles gérées par l'app

- **Première nuit sans mort** : les loups se découvrent, mais personne n'est dévoré, et il n'y a pas de vote le premier jour.
- **Le maire** est élu au premier jour ; s'il meurt, il choisit lui-même son successeur.
- **Égalité loups / villageois** : la partie continue tant que le maire n'est pas un loup ; elle s'arrête dès que les loups sont plus nombreux, ou aussi nombreux avec un loup pour maire.
- **Loups en désaccord** : si les loups ne se mettent pas d'accord sur une victime, personne n'est dévoré cette nuit-là.
- **Les amoureux** (Cupidon, ou tirés au sort si l'option est activée) meurent ensemble et gagnent s'ils sont les derniers survivants (deux, ou trois en mode trouple). Si le couple mêle un loup et un villageois, il forme un camp à part : tant qu'il vit, ni le village ni la meute ne peuvent gagner, et le couple doit éliminer tous les autres.
- **Le chasseur** peut emporter quelqu'un avec lui en mourant, ou renoncer à tirer.
- **Les solitaires** (Loup Blanc) ne gagnent qu'en éliminant tout le monde : tant qu'ils vivent, ni le village ni la meute ne peut conclure.
- **Camp secret** : à la mort du Chien-Loup, son camp n'est pas dévoilé avant la fin de la partie.
- **Louveteau** : sa mort double les victimes des loups la nuit suivante. La meute désigne alors deux joueurs ; en cas d'égalité à la limite des deux, seuls les joueurs strictement plus désignés meurent. La potion de la sorcière ne sauve que la victime la plus désignée.
- **Servante dévouée** : la nuit qui suit un vote, elle choisit (ou non) de reprendre le rôle d'un joueur condamné la veille ; elle découvre sa nouvelle carte tout de suite et la joue dès la nuit suivante. Le panneau du lendemain annonce qu'elle est intervenue (son nom et le condamné dont elle a pris le rôle), sans dire quel rôle elle a pris. Le camp du condamné a été révélé normalement au vote.
- **Juge bègue** : adaptation à l'app, il active son pouvoir pendant son tour de nuit (le second vote suit immédiatement le premier au conseil du lendemain, sauf si la partie est déjà finie ou s'il reste un tir de chasseur à résoudre).
- **Ordre de nuit** : le Voleur agit avant tout le monde, puis le Chien-Loup, puis les autres rôles.

## ✨ Fonctionnalités

- **Menu d'accueil** : un village qui défile (jour, nuit, loups, victoire) avec deux boutons, « Nouvelle partie » et « Historique ». L'écran Historique affiche chaque partie archivée sous forme de carte (date, joueurs, rôles, camp vainqueur, bordure colorée selon le vainqueur) avec le journal détaillé en cases nuit/jour.
- **Documentation** : depuis le menu d'accueil, un onglet « Comment jouer » (principe, déroulement, victoire, maire, passage de l'appareil) et un onglet « Les rôles » avec une dalle par rôle (résumé, force loups / village, information, chaos).
- **Rappel des règles en partie** : un volet de la barre latérale rappelle le déroulement, les conditions de victoire et les rôles du paquet.
- **Bilan de fin de partie** : chiffres clés (nuits, morts, loups démasqués, innocents condamnés...), distinctions (première victime, erreur judiciaire, loup le plus discret...), frise des disparitions, puis « Rejouer avec les mêmes joueurs » ou retour au menu.
- **Noms mémorisés** : les noms de la dernière partie sont préremplis (fichier `joueurs.json`, ignoré par git).
- **Composition personnalisable** : nombre de joueurs et répartition des rôles, réglables avant chaque partie.
- **Jauges d'équilibre** : l'écran de composition affiche un rapport de force loups / village, un niveau d'information et un niveau de chaos, recalculés à chaque changement de rôle ou d'option (indicateur approximatif, voir `docs/equilibre-roles.md`).
- **Options avancées** (menu de composition, « ⚙️ Options avancées ») : potions de soin (1 à 5) et de mort (0 à 5) de la sorcière, couple tiré au sort sans Cupidon (Cupidon est alors remplacé par un villageois), mode fun « trouple » (l'amour lie trois joueurs au lieu de deux), fréquence des visions de la voyante et des festins du Loup Blanc (chaque nuit, une nuit sur 2 ou sur 3), et égalité loups / village (le maire départage, ou les loups gagnent dès l'égalité). Les options ne s'affichent que pour les rôles présents.
- **Écrans de passage sécurisés** entre chaque joueur pour éviter qu'un rôle soit vu par la mauvaise personne.
- **Chronologie et rechargement** : une frise nuit/jour dans la barre latérale montre où en est la partie, et le menu Option permet de revenir au début d'une nuit ou à l'annonce d'un jour (plantage, erreur de clic).
- **Historique de partie** : chaque action (votes des loups, visions, protections, morts, tirs, élection du maire…) est journalisée, affichée nuit par nuit à la fin, archivée à la fin de la partie dans `historique/partie_AAAAMMJJ_HHMMSS.json` (les parties abandonnées ne sont pas conservées) et téléchargeable en JSON.
- **Sauvegarde automatique** (`save.json`) : la partie reprend là où elle s'est arrêtée, même après avoir fermé le serveur.

<p align="center">
  <img src="docs/banniere-jour.svg" alt="Un village sous le soleil : bon jeu et que le meilleur gagne" width="100%">
</p>

---

# 🛠️ Partie technique

## Prérequis

- macOS avec Python 3.10 ou supérieur (Python 3.9 ou antérieur peut poser des problèmes d'installation de dépendances).
- Le Terminal.
- Une connexion Internet au premier lancement (pour charger les polices Google Fonts utilisées par les cartes).

## Installation et lancement

### Option 1 : avec uv (le plus rapide)

```bash
# Installe uv si ce n'est pas déjà fait
brew install uv

# Lance directement l'app (uv installe Streamlit et le bon Python à la volée)
uv run --python 3.12 --with streamlit streamlit run src/loup_garou_app.py
```

Une seule commande, à chaque fois : pas de venv à créer ni à activer.

### Option 2 : avec venv + pip (méthode classique)

```bash
# Vérifie ta version de Python (3.10+ recommandé)
python3 --version

# Si besoin, installe une version récente via Homebrew
brew install python@3.12

# Crée et active un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installe les dépendances
pip install --upgrade pip
pip install streamlit

# Lance l'app
streamlit run src/loup_garou_app.py
```

**À chaque nouvelle session**, réactive l'environnement virtuel avant de relancer :

```bash
source .venv/bin/activate
streamlit run src/loup_garou_app.py
```

---

Dans les deux cas, ton navigateur s'ouvre automatiquement sur `http://localhost:8501`. Pour arrêter le serveur : `Ctrl+C` dans le terminal.

## Structure du projet

```
.
├── src/
│   ├── loup_garou_app.py        # Point d'entrée Streamlit (quelques lignes)
│   └── loup_garou/
│       ├── app.py               # main() : page, barre latérale, aiguillage selon la phase
│       ├── config.py            # Chemins (save.json, historique/, musique.mp3)
│       ├── options.py           # Options avancées et leurs valeurs par défaut
│       ├── equilibre.py         # Jauges d'équilibre (force, information, chaos) d'une composition
│       ├── roles.py             # Registre ROLES (données des rôles, sans interface)
│       ├── moteur/              # Règles du jeu, sans dépendance à l'interface
│       │   ├── partie.py        #   nouvelle partie, morts, résolution de la nuit, victoire
│       │   ├── bilan.py         #   bilan de fin de partie (chiffres, distinctions, frise)
│       │   ├── journal.py       #   journal et instantanés de la chronologie
│       │   └── persistance.py   #   sauvegarde, archives et lecture de l'historique
│       └── ui/                  # Interface Streamlit
│           ├── styles.py        #   CSS et décors SVG
│           ├── composants.py    #   cartes, bandeaux, dalles de sélection...
│           ├── nuit_roles.py    #   tour de nuit de chaque rôle (NUIT_ROLES)
│           ├── regles.py        #   texte des règles (tutoriel et rappel en partie)
│           ├── barre_laterale.py#   rechargement d'étape, barre ouverte
│           └── ecrans/          #   accueil, installation, nuit, jour, fin, documentation
├── .claude/skills/projet-gevaudan/SKILL.md  # Guide du projet pour Claude Code (architecture, règles, conventions)
├── docs/
│   ├── equilibre-roles.md       # Force, information et chaos de chaque rôle (proposition)
│   ├── banniere.svg             # Bannière de nuit du README
│   └── banniere-jour.svg        # Bannière de jour du README
├── musique.mp3                  # (optionnel) musique de fond, à ajouter toi-même
├── save.json                    # Sauvegarde de la partie en cours (générée automatiquement)
├── historique/                  # Archives JSON des parties terminées (versionnées dans le dépôt)
└── .streamlit/
    └── config.toml              # Configuration du thème sombre
```

Le dossier `moteur/` ne dépend ni de Streamlit ni de `ui/` : les règles se lisent et se testent sans interface. Les dépendances vont toujours dans le même sens : `ui` -> `moteur` -> `roles` / `options` -> `config`.

> 💡 `save.json` contient l'état complet d'une partie en cours, y compris les rôles des joueurs : il est listé dans le `.gitignore`. Le dossier `historique/`, lui, est poussé sur le dépôt : chaque partie terminée y ajoute un fichier avec les rôles et le journal complet.

## Tests

```bash
uv run --python 3.12 --with pytest --with streamlit python -m pytest
```

- `tests/test_partie.py`, `test_options.py`, `test_roles.py`, `test_journal.py`, `test_persistance.py` : tests unitaires du moteur, sans Streamlit. Chaque test tourne dans un dossier temporaire (`save.json` et `historique/` du dépôt ne sont jamais touchés).
- `tests/test_ui_smoke.py` : joue une partie complète au hasard (graine fixe) avec le banc d'essai `streamlit.testing`, pour repérer une exception d'affichage ou un écran sans issue. Il est ignoré si Streamlit n'est pas installé.
- La CI (`.gitlab-ci.yml` et `.github/workflows/tests.yml`) lance cette suite sur chaque merge request / pull request.

## Ajouter un rôle

1. Déclarer le rôle dans le registre `ROLES` de `src/loup_garou/roles.py` (dataclass `Role`) : nom, emoji, dégradé de la carte, camp, état de départ, priorité de nuit, description (une ou deux phrases, affichées en infobulle dans l'écran de composition). Pour les jauges d'équilibre, ajouter aussi ses notes dans `src/loup_garou/equilibre.py`.
2. Écrire sa fonction de tour de nuit dans `src/loup_garou/ui/nuit_roles.py` et l'inscrire dans le dictionnaire `NUIT_ROLES`. Un rôle absent de `NUIT_ROLES` dort comme un villageois. Un rôle qui se joue à plusieurs cartes (Sœurs, Frères) renseigne `lot` : cocher la case en ajoute `lot` cartes.

Les règles (`moteur/`) lisent le registre : elles n'ont pas à changer pour un rôle sans effet particulier sur la victoire ou les morts.
