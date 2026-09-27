# 🐺 Loup-Garou — édition Streamlit

Une application web légère pour jouer au Loup-Garou (Les Loups-Garous de Thiercelieux) à plusieurs, sur un seul appareil qu'on se passe autour de la table ("hotseat"). Pas besoin de cartes physiques ni de maître du jeu : l'app gère la distribution des rôles, les nuits, les votes et les fins de partie.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Lancer le jeu](#lancer-le-jeu)
- [Personnalisation](#personnalisation)
- [Dépannage](#dépannage)
- [Structure du projet](#structure-du-projet)

## Fonctionnalités

- **7 joueurs, 5 rôles** : 2 Loups-Garous, 1 Sorcière, 1 Voyante, 1 Cupidon, 2 Villageois.
- **Écran de passage sécurisé** entre chaque joueur, en deux étapes, pour éviter qu'un rôle soit vu par la mauvaise personne.
- **Cartes de rôle stylisées**, façon vraie carte de jeu.
- **Sauvegarde automatique** (`save.json`) : la partie reprend automatiquement là où elle s'est arrêtée, même après avoir fermé le serveur.
- **Journal de partie** : résumé nuit par nuit affiché à la fin (qui a été tué, sauvé, observé, éliminé…).
- **Musique de fond** optionnelle, en boucle.
- **Thème sombre** et mise en page compacte, pensée pour un usage sur téléphone ou ordinateur portable.

## Prérequis

- **Python 3.10 ou supérieur** (Python 3.9 ou antérieur peut poser des problèmes d'installation de dépendances).
- Un terminal (Terminal sur Mac/Linux, PowerShell ou Invite de commandes sur Windows).
- Une connexion Internet au premier lancement (pour charger les polices Google Fonts utilisées par les cartes).

## Installation

Commence par cloner ou télécharger le dépôt :

```bash
git clone https://github.com/<ton-compte>/<ton-repo>.git
cd <ton-repo>
```

Puis suis les instructions de ton système.

### macOS

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
```

### Windows

Dans PowerShell :

```powershell
# Vérifie ta version de Python (3.10+ recommandé)
python --version

# Crée et active un environnement virtuel
python -m venv .venv
.venv\Scripts\Activate.ps1

# Installe les dépendances
pip install --upgrade pip
pip install streamlit
```

> Si `python` n'est pas reconnu, installe Python depuis [python.org](https://www.python.org/downloads/) en cochant bien la case **"Add Python to PATH"** pendant l'installation.

> Si PowerShell refuse d'exécuter le script d'activation (erreur de policy d'exécution), lance une fois :
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Linux

```bash
# Vérifie ta version de Python (3.10+ recommandé)
python3 --version

# Installe python3-venv si nécessaire (Debian/Ubuntu)
sudo apt install python3-venv

# Crée et active un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installe les dépendances
pip install --upgrade pip
pip install streamlit
```

## Lancer le jeu

Une fois l'environnement virtuel activé et Streamlit installé :

```bash
streamlit run loup_garou_app.py
```

Ton navigateur s'ouvre automatiquement sur `http://localhost:8501`. Si ce n'est pas le cas, ouvre ce lien manuellement.

Pour arrêter le serveur : `Ctrl+C` dans le terminal.

**À chaque nouvelle session**, pense à réactiver l'environnement virtuel avant de relancer :

```bash
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\Activate.ps1     # Windows (PowerShell)

streamlit run loup_garou_app.py
```

## Personnalisation

- **Thème sombre forcé** : configuré dans `.streamlit/config.toml`, déjà inclus dans le dépôt.
- **Musique de fond** : ajoute un fichier nommé `musique.mp3` à la racine du projet (même dossier que `loup_garou_app.py`). Il sera détecté automatiquement au lancement, avec une case à cocher pour l'activer/désactiver dans la barre latérale.
- **Nouvelle partie** : le bouton "🚪 Abandonner la partie" dans la barre latérale supprime la sauvegarde en cours et repart de zéro.

## Dépannage

| Problème | Cause probable | Solution |
|---|---|---|
| `Failed building wheel for pyarrow` à l'installation | Version de Python trop ancienne ou trop récente | Utilise Python 3.10 à 3.13 pour ton environnement virtuel |
| `TypeError: container() got an unexpected keyword argument 'height'` | Version de Streamlit trop ancienne | `pip install --upgrade streamlit` |
| Le bouton de confirmation ne devient pas vert / bouton mal placé | Version de Streamlit trop ancienne (fonctionnalité de classes CSS par clé de widget) | `pip install --upgrade streamlit` (≥ 1.36 recommandé) |
| Pas de son au lancement | Politique de lecture automatique du navigateur | Clique une fois manuellement sur le bouton ▶️ du lecteur dans la barre latérale |
| `musique.mp3 introuvable` alors que le fichier existe | Le fichier n'est pas au bon endroit | Vérifie qu'il est bien à la racine du projet, au même niveau que `loup_garou_app.py` |

## Structure du projet

```
.
├── loup_garou_app.py      # L'application Streamlit
├── musique.mp3             # (optionnel) musique de fond, à ajouter toi-même
├── save.json                # Sauvegarde de la partie en cours (générée automatiquement)
└── .streamlit/
    └── config.toml          # Configuration du thème sombre
```

> 💡 `save.json` contient l'état complet d'une partie en cours, y compris les rôles des joueurs. Si tu partages ce dépôt publiquement, pense à l'ajouter à un `.gitignore` pour ne pas exposer une sauvegarde en cours :
> ```
> save.json
> ```
