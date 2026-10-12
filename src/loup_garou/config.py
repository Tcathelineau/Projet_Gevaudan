"""Chemins des fichiers et réglages d'hébergement de l'application."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo


SAVE_FILE = "save.json"
HISTORIQUE_DIR = "historique"
MUSIQUE_FILE = "musique.mp3"
PREFERENCES_FILE = "preferences.json"  # réglages du son et dernière composition, gardés d'une session à l'autre
JOUEURS_FILE = "joueurs.json"  # derniers noms de joueurs, préremplis à la partie suivante

# Hébergement : DATABASE_URL (ex. postgres://... ou sqlite:///loup_garou.db) range les parties en base, plusieurs en parallèle,
# chacune reprise par son code. Sans elle, l'application garde les fichiers ci-dessus (une partie, usage local).
PARTIES_CONSERVEES_JOURS = 30  # base : une partie jamais rouverte depuis ce délai est supprimée
ARCHIVES_CONSERVEES_JOURS = 365  # base : les archives de parties terminées contiennent des pseudos


def database_url():
    """URL de la base si l'hébergement en fournit une, sinon None (lu à chaque appel : les tests la changent)."""
    return os.environ.get("DATABASE_URL") or None


def fuseau():
    """Fuseau d'affichage des heures (un conteneur est en UTC) : variable FUSEAU, Europe/Paris par défaut."""
    try:
        return ZoneInfo(os.environ.get("FUSEAU") or "Europe/Paris")
    except Exception:
        return ZoneInfo("UTC")


def maintenant():
    """Heure actuelle, avec fuseau."""
    return datetime.now(fuseau())
