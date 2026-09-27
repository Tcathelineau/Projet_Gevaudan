# 🐺 Loup-Garou — édition Streamlit

Une application web légère pour jouer au Loup-Garou (Les Loups-Garous de Thiercelieux) à plusieurs, sur un seul appareil qu'on se passe autour de la table ("hotseat"). Pas besoin de cartes physiques ni de maître du jeu : l'app gère la composition de la partie, la distribution des rôles, les nuits, les votes et les fins de partie.

## Fonctionnalités

- **Composition personnalisable** : nombre de joueurs et répartition des rôles (Loups-Garous, Sorcière, Voyante, Cupidon, Villageois) réglables avant chaque partie.
- **Écran de passage sécurisé** entre chaque joueur, en deux étapes, pour éviter qu'un rôle soit vu par la mauvaise personne.
- **Cartes de rôle stylisées**, façon vraie carte de jeu.
- **Sauvegarde automatique** (`save.json`) : la partie reprend automatiquement là où elle s'est arrêtée, même après avoir fermé le serveur.
- **Journal de partie** : résumé nuit par nuit affiché à la fin.
- **Musique de fond** optionnelle, en boucle.
- **Thème sombre** et mise en page compacte.

## Prérequis

- macOS avec Python 3.10 ou supérieur (Python 3.9 ou antérieur peut poser des problèmes d'installation de dépendances).
- Le Terminal.
- Une connexion Internet au premier lancement (pour charger les polices Google Fonts utilisées par les cartes).

## Installation et lancement

### Option 1 — avec uv (le plus rapide)

```bash
# Installe uv si ce n'est pas déjà fait
brew install uv

# Lance directement l'app (uv installe Streamlit et le bon Python à la volée)
uv run --python 3.12 --with streamlit streamlit run src/loup_garou_app.py
```

Une seule commande, à chaque fois : pas de venv à créer ni à activer.

### Option 2 — avec venv + pip (méthode classique)

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
├── musique.mp3              # (optionnel) musique de fond, à ajouter toi-même
├── save.json                 # Sauvegarde de la partie en cours (générée à la racine, automatiquement)
└── .streamlit/
    └── config.toml           # Configuration du thème sombre
```

> 💡 `save.json` contient l'état complet d'une partie en cours, y compris les rôles des joueurs. Si tu partages ce dépôt publiquement, pense à l'ajouter à un `.gitignore` pour ne pas exposer une sauvegarde en cours :
> ```
> save.json
> ```
