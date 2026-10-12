# Projet Gévaudan : règles pour Claude Code

Avant toute modification, charger le skill `projet-gevaudan` (`.claude/skills/projet-gevaudan/SKILL.md`) : architecture, règles de jeu décidées, conventions.

## Mémoire du projet : une PR = une entrée de journal

**À chaque pull request**, avant de l'ouvrir :

1. Ajouter une entrée dans `CHANGELOG.md` (section du jour, puce `- **Titre court** : ...`) : ce qui change, la décision et sa raison, les pièges, les idées écartées, les fichiers repères.
2. Mettre à jour dans la même PR ce que le changement rend faux ou incomplet :
   - `README.md` : tableau des rôles, règles gérées par l'app, fonctionnalités, structure du projet ;
   - `.claude/skills/projet-gevaudan/SKILL.md` : architecture, clés de l'état `s`, règles décidées, options, chantiers connus ;
   - `docs/accessibilite.md` si l'interface change (nouveau composant, nouvelle couleur) ;
   - `docs/equilibre-roles.md` seulement via `outils/ecrire_doc_equilibre.py` (fichier généré).
3. Une nouvelle option s'ajoute aussi à `OPTIONS_DOC` (`ui/regles.py`) ; un nouveau rôle exige icône et mesures d'équilibre (voir README, « Ajouter un rôle »).
4. Renseigner la case correspondante du modèle de PR (`.github/pull_request_template.md`).

La CI (`outils/verifier_changelog.py`) refuse une PR qui modifie `src/` ou `tests/` sans toucher à `CHANGELOG.md`. Pour une PR purement mécanique, poser le label `sans-changelog`.

## Avant d'ouvrir une PR

`uv run ruff check` puis `uv run pytest` doivent passer. Une dépendance se change avec `uv add` / `uv remove` : committer `pyproject.toml` et `uv.lock` ensemble.

## Façon de travailler (rappel)

- Une branche et une PR par changement ; titre explicite ; corps avec « Résumé », « À savoir », « À tester ». L'utilisateur fusionne.
- Pousser uniquement avec le compte personnel **Tcathelineau**.
- Ajouter les fichiers par nom ; jamais `.DS_Store` ni les `historique/partie_*.json` des parties de test.
- Son désactivé pendant les tests ; pas de test navigateur systématique (l'utilisateur teste lui-même).
- Réponses en français, concises, sans tiret cadratin ni flèche.
