# Déploiement

Le dépôt livre une image Docker neutre : n'importe quel hébergeur de conteneurs peut la faire tourner. Rien ici n'engage une plateforme.

## Construire et lancer

```bash
docker build -t gevaudan .
docker run --rm -p 8501:8501 gevaudan                                     # mode fichiers : une seule partie, perdue si le conteneur est recréé
docker run --rm -p 8501:8501 -e DATABASE_URL=postgres://... gevaudan      # mode base : plusieurs parties, reprise par code
docker compose up --build                                                 # l'application et un Postgres local, prêts à l'emploi
```

L'application écoute sur `$PORT` (8501 par défaut) et répond à `GET /_stcore/health` (c'est le `HEALTHCHECK` de l'image).

## Réglages (variables d'environnement)

| Variable | Rôle | Défaut |
|---|---|---|
| `DATABASE_URL` | Base SQL : `postgres://utilisateur:motdepasse@hote:5432/base` ou `sqlite:///fichier.db`. Active le mode « plusieurs parties ». Tables créées au démarrage. | absente : fichiers |
| `PORT` | Port d'écoute. | `8501` |
| `FUSEAU` | Fuseau d'affichage des heures (échéance du conseil, dates). | `Europe/Paris` |

## À prévoir côté hébergeur

- **Base persistante** : sans `DATABASE_URL`, `save.json` vit dans le conteneur et disparaît à chaque redéploiement. En production, toujours une base.
- **WebSocket** : Streamlit en a besoin, le reverse proxy doit les laisser passer (la plupart des plateformes le font).
- **Une seule instance** : l'état d'écran de chaque session vit en mémoire du processus. Avec plusieurs instances, un joueur qui retombe sur une autre perd son écran en cours (la partie, elle, se reprend par son code). Rester à une instance, ou activer l'affinité de session.
- **HTTPS** : fourni par la plateforme ou un proxy ; l'application ne le gère pas.
- **Sauvegardes** : celles de la base managée. Les données en base sont des parties en cours (30 jours) et des archives (1 an), voir README.
- **RGPD** : les archives contiennent des pseudos et des rôles. Choisir une région de l'UE pour l'application et la base, mentionner la conservation, prévoir une suppression sur demande (`DELETE FROM archives WHERE code = '...'`).
- **Le code de partie est un lien secret** : la sauvegarde contient les rôles en clair.

## Choisir une plateforme (état au 2026-10-12, à revérifier avant de décider)

| Option | Ce qui est établi | À vérifier |
|---|---|---|
| Streamlit Community Cloud | Prend `uv.lock` en charge ; héberge toutes les applications aux États-Unis, non configurable (documentation officielle de Streamlit). Il faut une base externe : le disque n'y est pas fait pour durer. | Région hors UE : à peser pour des pseudos. Pas de conteneur : `Dockerfile` inutilisé. |
| Conteneur en Europe (par exemple Scaleway Serverless Containers) | Facturation à la consommation avec un quota gratuit mensuel selon la page tarifaire de Scaleway ; base Postgres managée sans palier gratuit (environ 11 € par mois pour la plus petite formule, source secondaire). | Tarifs actuels, comportement du « scale to zero » avec les WebSocket de Streamlit (fixer au moins une instance). |
| Fly.io, Render, Cloud Run | Acceptent un conteneur. | Régions UE, tarifs actuels (des comparatifs récents évoquent la fin des paliers gratuits pour Fly.io, source secondaire non vérifiée), WebSocket. |

Une base Postgres managée en UE (chez l'hébergeur ou un service dédié) se branche par `DATABASE_URL`.

## Vérifié et non vérifié

- Vérifié : lancement de Streamlit avec la ligne de commande de l'image sur un environnement installé par `uv sync --locked --no-dev`, réponse du point de santé, tests de stockage sur SQLite.
- Vérifié par la CI GitHub à chaque PR : construction de l'image, démarrage du conteneur et réponse du point de santé ; tests de stockage sur Postgres 16.
- Non vérifié : `docker compose up` (jamais lancé), un vrai hébergeur, plusieurs joueurs simultanés.
