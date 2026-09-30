<p align="center">
  <img src="docs/banniere.svg" alt="Projet Gévaudan : un village endormi sous la pleine lune" width="100%">
</p>

<p align="center">
  <strong>Les Loups-Garous de Thiercelieux, sur un seul écran qu'on se passe autour de la table.</strong><br>
  Pas de cartes physiques, pas de maître du jeu : l'application distribue les rôles, mène les nuits, compte les morts et proclame le vainqueur.
</p>

---

## 🌙 Le jeu

Un village est hanté par des loups-garous. Chaque nuit, ils dévorent un villageois ; chaque jour, le village vote pour éliminer un suspect. Les villageois gagnent s'ils débusquent tous les loups, les loups gagnent s'ils deviennent aussi nombreux que les autres.

Tout le monde joue sur **le même appareil** ("hotseat") : à chaque tour de nuit, l'écran demande de le passer au joueur suivant, en deux étapes, pour que personne ne voie la carte d'un autre.

### Une partie en un coup d'œil

1. **Composition** : on saisit les pseudos et on règle le nombre de loups et de rôles spéciaux. Le reste de la table est complété en villageois.
2. **La nuit tombe** : chaque joueur, à son tour, découvre sa carte et agit en secret (dévorer, sonder, protéger, soigner…).
3. **Le village se réveille** : un panneau d'affichage annonce les morts de la nuit et le camp qu'ils avaient.
4. **Élection du maire** (au premier jour) puis **conseil du village** : on débat à voix haute, l'app enregistre le vote et révèle si l'éliminé était loup ou non.
5. Retour à la nuit, jusqu'à la victoire d'un camp.

### Les règles gérées par l'app

- **Première nuit sans mort** : les loups se découvrent, mais personne n'est dévoré, et il n'y a pas de vote le premier jour.
- **Le maire** est élu au premier jour ; s'il meurt, le village élit son successeur.
- **Les amoureux** (Cupidon) meurent ensemble et gagnent s'ils sont les deux derniers survivants, même s'ils viennent de camps opposés.
- **Le chasseur** peut emporter quelqu'un avec lui en mourant, ou renoncer à tirer.
- **Les solitaires** (Loup Blanc) ne gagnent qu'en éliminant tout le monde : tant qu'ils vivent, ni le village ni la meute ne peut conclure.
- **Camp secret** : à la mort du Chien-Loup, son camp n'est pas dévoilé avant la fin de la partie.
- **Ordre de nuit** : le Voleur agit avant tout le monde, puis le Chien-Loup, puis les autres rôles.

## 🃏 Les rôles

| | Rôle | Camp | Pouvoir |
|---|---|---|---|
| 🐺 | **Loup-Garou** | Loups | Se retrouve avec la meute et vote chaque nuit (dès la deuxième) pour dévorer un villageois. |
| 🧑‍🌾 | **Villageois** | Village | Aucun pouvoir : il dort, débat et vote le jour. |
| 🔮 | **Voyante** | Village | Une nuit sur deux, sonde un joueur et découvre son rôle. |
| 🧪 | **Sorcière** | Village | Dispose d'une potion de soin pour sauver la victime des loups. |
| 🏹 | **Cupidon** | Village | La première nuit, lie deux joueurs par l'amour (lui compris). |
| 🔫 | **Chasseur** | Village | À sa mort, tire une dernière balle sur le joueur de son choix. |
| 🛡️ | **Salvateur** | Village | Protège un joueur chaque nuit, jamais le même deux nuits de suite. |
| 🧒 | **Enfant sauvage** | Village | Choisit un mentor ; si celui-ci meurt, il devient loup-garou. |
| 🃏 | **Voleur** | Village | Deux cartes restent au milieu de la table : il peut prendre le rôle de l'une d'elles. |
| 🦊 | **Renard** | Village | Flaire trois joueurs et apprend si un loup s'y cache ; sans loup, il perd son flair. |
| 🌕 | **Loup Blanc** | Loups, solitaire | Une nuit sur deux, peut dévorer l'un de ses frères ; il gagne seul. |
| 🐕 | **Chien-Loup** | Au choix | Choisit son camp en secret la première nuit : villageois ou loup-garou. |

## ✨ Fonctionnalités

- **Composition personnalisable** : nombre de joueurs et répartition des rôles, réglables avant chaque partie.
- **Écrans de passage sécurisés** entre chaque joueur pour éviter qu'un rôle soit vu par la mauvaise personne.
- **Cartes de rôle** stylisées, façon vraie carte de jeu.
- **Ambiance** : bandeaux animés (nuit qui tombe, lever de soleil, victoire du village ou des loups) et panneau d'affichage pour l'annonce des morts. Les animations sont coupées si le système demande de réduire les mouvements.
- **Chronologie et rechargement** : une frise nuit/jour dans la barre latérale montre où en est la partie, et le menu Option permet de revenir au début d'une nuit ou à l'annonce d'un jour (plantage, erreur de clic).
- **Historique de partie** : chaque action (votes des loups, visions, protections, morts, tirs, élection du maire…) est journalisée, affichée nuit par nuit à la fin, archivée dans `parties/partie_AAAAMMJJ_HHMMSS.json` et téléchargeable en JSON.
- **Sauvegarde automatique** (`save.json`) : la partie reprend là où elle s'est arrêtée, même après avoir fermé le serveur.
- **Musique de fond** optionnelle, en boucle.
- **Thème sombre** et mise en page compacte.

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
│   └── loup_garou_app.py   # L'application Streamlit
├── docs/
│   └── banniere.svg         # Bannière du README
├── musique.mp3              # (optionnel) musique de fond, à ajouter toi-même
├── save.json                # Sauvegarde de la partie en cours (générée automatiquement)
├── parties/                 # Archives JSON des parties terminées ou abandonnées
└── .streamlit/
    └── config.toml          # Configuration du thème sombre
```

> 💡 `save.json` contient l'état complet d'une partie en cours, y compris les rôles des joueurs, et `parties/` les archives des parties passées. Les deux sont listés dans le `.gitignore` : ne les retire pas si tu partages le dépôt publiquement.

## Ajouter un rôle

Chaque rôle est déclaré dans le registre `ROLES` de `src/loup_garou_app.py` (dataclass `Role`) : nom, emoji, dégradé de la carte, camp, état de départ et fonction de tour de nuit. Un nouveau rôle se déclare à cet endroit, sans toucher au reste de la logique.
