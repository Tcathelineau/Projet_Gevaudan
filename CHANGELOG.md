# Journal des changements

Ce fichier est la mémoire du projet : **chaque pull request y ajoute une entrée** (c'est vérifié par la CI, voir `CLAUDE.md`). Il dit ce qui a changé, pourquoi, et ce qu'il faut savoir pour ne pas casser la suite (décisions, pièges, pistes écartées).

## Comment ajouter une entrée

1. Ouvrir la section du jour (`## AAAA-MM-JJ`, la créer en tête si elle manque ; les plus récentes en haut).
2. Ajouter une puce `- **Titre court** : ...` avec : ce qui change pour le joueur ou le code, la décision et sa raison, le piège éventuel, les fichiers repères entre accents graves.
3. Si le changement touche aussi une règle, une option, un rôle ou l'architecture, mettre à jour `README.md` et `.claude/skills/projet-gevaudan/SKILL.md` dans la même PR.
4. Une PR purement mécanique (typo, CI) peut porter le label `sans-changelog` pour passer le contrôle.

---

## 2026-10-12

- **Hébergement : image Docker neutre** : `Dockerfile` (python 3.12 slim, `uv sync --locked --no-dev`, utilisateur sans droits, `HEALTHCHECK` sur `/_stcore/health`, écoute sur `$PORT`), `.dockerignore`, `docker-compose.yml` (application + Postgres 16), `docs/deploiement.md` (variables, points d'attention : base persistante, WebSocket, une seule instance, RGPD ; tableau de choix de plateforme à revérifier), `gatherUsageStats = false` dans `.streamlit/config.toml`. CI : job `image` qui construit l'image, la lance et sonde le point de santé. Décision : aucune plateforme choisie (demande de l'utilisateur), Community Cloud est américain non configurable (doc officielle Streamlit). Vérifié en local sans Docker (démon éteint) : lancement avec la ligne de commande de l'image sur un environnement `--no-dev`, point de santé OK. Jamais lancé : `docker build`, `docker compose up`.

- **Stockage SQL et plusieurs parties** : `moteur/stockage.py` (fichiers en local, base SQL via `DATABASE_URL`, SQLite ou Postgres par SQLAlchemy), `moteur/codes.py`, état de partie en version 2 (`code`, migration v2). Chaque partie a un code de 8 caractères (`K7M2-QX9P`), mis dans l'adresse (`?partie=`), affiché dans le menu Option, saisissable sur l'accueil ; plusieurs groupes peuvent jouer en même temps. Décisions : en base, les archives ne se listent qu'avec le code (sinon un groupe verrait les pseudos des autres) ; préférences et derniers noms ne sont pas gardés (ils seraient communs à tous) ; ménage à 30 jours (parties) et 1 an (archives) pour limiter les pseudos conservés ; le code est un lien secret car la sauvegarde contient les rôles en clair. Heures passées au fuseau `FUSEAU` (Europe/Paris) via `config.maintenant()` : un conteneur est en UTC. CI : service Postgres 16 pour rejouer les tests de stockage sur la vraie base (non exécutable en local, Docker éteint). Les usages en fichiers (local) ne changent pas.

- **Packaging** : `pyproject.toml` (dépendances, groupes `dev` et `outils`, réglages pytest et ruff, remplace `pytest.ini`), `uv.lock` épinglé, `.python-version`, CI GitHub et GitLab passées sur `uv sync --locked` + `ruff check` + `pytest` (corrige l'erreur « No file matched requirements.txt or pyproject.toml » de `setup-python`), `.pre-commit-config.yaml` facultatif. Commandes de lancement simplifiées : `uv run streamlit run src/loup_garou_app.py`. Streamlit borné à `>=1.58,<2` (versions testées 1.58 et 1.65). Pas de mypy : état en dictionnaire et interface Streamlit, peu de bénéfice pour un coût élevé.

- **Mémoire du projet** : ce journal, `CLAUDE.md`, le modèle de PR et le contrôle CI `outils/verifier_changelog.py` (une PR qui touche `src/` ou `tests/` doit modifier `CHANGELOG.md`). README et skill remis à jour (documentation à 3 onglets, options, fenêtres couple et meute, chantiers connus). Ajout au skill d'une feuille de route vers une app « pro » (§8 : stockage, hébergement, packaging, données personnelles, multi-appareils, accessibilité). `docs/accessibilite.md` et `docs/equilibre-roles.md` signalent les fenêtres non vérifiées et les options non simulées.

## 2026-10-08

- **Fenêtre de découverte de la meute** (#96) : un loup qui découvre sa carte pour la première fois voit « Vous êtes la meute » (ou « Tu es le dernier loup »), en rouge sombre, calquée sur celle du couple (`fenetre_meute`, drapeau `meute_vue` sur le joueur). Streamlit n'ouvre qu'une fenêtre à la fois : si celle du couple doit s'ouvrir au même tour, la meute attend la nuit suivante.
- **Trouple, bonus voyante, doc des options, jauge** (#95) : le trouple est proposé même sans couple tiré au sort ; « BONUS : la voyante peut découvrir le couple » s'affiche sous le couple tiré au sort (conteneur `bonus_voyante_couple`) ; onglet « Les options » de la documentation (`OPTIONS_DOC`, un test exige que chaque option y figure) ; jauge loups/village agrandie (`.jauge-equilibre`) ; « Le déroulement » retiré du rappel en partie (`SECTIONS_RAPPEL`). **Le couple tiré au sort n'apprend son amour qu'à la nuit 1** (`jour > 0`), comme avec Cupidon.
- **Quatre nouvelles options** (#94) : la sorcière apprend qui elle a sauvé la nuit suivante (`sorciere_sait_sauve`, mémoire `s["sauve_par_sorciere"]`) ; ce que révèle une mort, camp / rôle / rien (`revelation_mort` ; « rien » masque aussi le gong, la couleur des avis et les effectifs par camp du menu de gauche, sinon ils trahiraient le camp) ; composition secrète (le rappel ne liste pas le paquet) ; échéance de conseil tirée au hasard entre deux bornes (`echeance_*`, `tirer_echeance`, bandeau rafraîchi toutes les 30 s, indicatif : rien ne force le vote). **Réglages sans objet masqués, jamais grisés** (rôle absent, couple non tiré au sort). Idée écartée : montrer la victime à la sorcière (dépend de l'ordre de passage et donne trop d'information).

## 2026-10-07

- **Étape Options en cartes** (#93) : cartes centrées (`carte_option`), potions de soin et de mort 0 à 5, option `voyante_couple`.
- **Corrections** (#92) : le bouton « Compris » d'une fenêtre doit appeler `st.rerun()` (un bouton dans `st.dialog` ne relance que le fragment) ; bulles loup/villageois seulement à l'étape Table ; annonce de la servante sans son nom.
- **Retouches UX** (#91) : étape Table, réglages à cocher, fenêtre du couple rose, carte fantôme masquée pendant les relances (CSS sur `data-stale`).
- **UX** (#90) : reprise visible de la partie sauvegardée, composition en 4 étapes avec bandeau fixe, widgets sur mesure (`compteur`, `choix_segmente`), dalles sans clignotement (fragments), préférences durables (`preferences.json`). Piège : un widget non affiché perd son état, d'où `_conserver()`.
- **Menu de gauche épuré** (#89), **compteurs de composition** (#86, #87), **composition épurée et fenêtre du couple** (#85).
- **Cinq nouveaux rôles** (#88) : Montreur d'ours, Petite Fille, Corbeau, Idiot du village, Bouc émissaire ; équilibre recalculé ; meute dans le menu de gauche.
- **Remarques de jeu** (#84) : les loups peuvent se voter entre eux, couple et voyante, coulisses (journal détaillé), sons retravaillés.
- **Solidité** (#83) : sauvegarde versionnée (`moteur/migrations.py`, toute clé obligatoire exige une migration et un test), écriture atomique, abandon confirmé, accessibilité (`docs/accessibilite.md`, `tests/test_accessibilite.py`) et mobile.

## 2026-10-06

- **Finition** (#81) : retournement de carte, statistiques, vraies musiques (CC0 FreePD), **son désactivé par défaut** (l'utilisateur travaille en open space ; ne jamais en jouer pendant les tests).
- **Composition par catégories** (#80), **chauves-souris et feuilles** (#79), **musiques par phase, hurlement, pondération mesurée** (#77).
- **Bilan de fin, prise en main, cartes illustrées, sons, identité** (#76).
- **Servante dévouée** (#73) : elle reprend le rôle d'un condamné la nuit suivante, annoncée au panneau sans nom.

## 2026-10-05 et avant

- **Nouveaux rôles** (#72) : Louveteau, Sœurs / Frères, Servante dévouée, Juge bègue.
- **Documentation des rôles** (#71), **rôles à cocher 4 par ligne** (#70), **infobulles** (#69).
- **Jauges d'équilibre** (#66 à #68) : coefficients mesurés par simulation (`outils/simuler_equilibre.py`, `assets/equilibre.json`, `docs/equilibre-roles.md`). Les jauges donnent des ordres de grandeur, pas des vérités.

## 2026-10-01

- **Refactoring en trois temps** (#63 à #65) : éclatement du code en `moteur/` (sans Streamlit) et `ui/`, skill `projet-gevaudan`, tests unitaires et CI (GitHub Actions et GitLab).
- **Options avancées** (#60, #61) : potion de mort, couple aléatoire, trouple.

## 2026-09-30

- **Historique des parties** (#53, #54) : journal archivé dans `historique/`, écran Historique.
- **Interface de jeu** (#25 à #59) : dalles sans scroll, maire et vote en dalles, chronologie et rechargement d'étape, menu Option, scènes jour/nuit animées, panneau d'affichage des morts, bandeaux de victoire, égalité loups/village (le maire départage), couple mixte (camp à part).

## 2026-09-27 à 2026-09-29

- **Première version jouable** (#4 à #24) : registre des rôles, écran de composition, rôles Chasseur, Salvateur, Enfant sauvage, Voleur, Renard, Loup Blanc, Chien-Loup, premier historique de partie.
