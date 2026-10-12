"""Où vivent les données : des fichiers (usage local, une partie) ou une base SQL (hébergé, plusieurs parties).

Les deux stockages offrent les mêmes opérations ; `persistance.py` s'appuie dessus pour valider, migrer et archiver.
Les parties passent en texte JSON : c'est `persistance.py` qui juge un contenu corrompu ou trop récent.
"""

import glob
import json
import os
import threading
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from loup_garou.config import (
    ARCHIVES_CONSERVEES_JOURS, HISTORIQUE_DIR, JOUEURS_FILE, PARTIES_CONSERVEES_JOURS, PREFERENCES_FILE, SAVE_FILE,
    database_url,
)


def _ecrire_sans_trou(chemin, texte):
    """Écrit puis remplace : jamais de fichier à moitié écrit."""
    provisoire = chemin + ".tmp"
    with open(provisoire, "w", encoding="utf-8") as f:
        f.write(texte)
    os.replace(provisoire, chemin)


class StockageFichiers:
    """Usage local : `save.json` (une seule partie), `historique/`, `preferences.json`, `joueurs.json`.
    Le code de partie est ignoré : la sauvegarde est unique."""

    multi_parties = False
    _REGLAGES = {"preferences": PREFERENCES_FILE, "joueurs": JOUEURS_FILE}

    def lire_partie(self, code):
        if not os.path.exists(SAVE_FILE):
            return None
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return f.read()

    def ecrire_partie(self, code, etat):
        _ecrire_sans_trou(SAVE_FILE, json.dumps(etat, indent=2, ensure_ascii=False))

    def supprimer_partie(self, code):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def mettre_de_cote(self, code, raison):
        """Garde un fichier inutilisable à côté (pour ne rien perdre) et repart d'une page blanche."""
        os.replace(SAVE_FILE, f"{SAVE_FILE}.{raison}")

    def modifie_le(self, code):
        return datetime.fromtimestamp(os.path.getmtime(SAVE_FILE)) if os.path.exists(SAVE_FILE) else None

    def lire_reglage(self, nom):
        try:
            with open(self._REGLAGES[nom], "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None

    def ecrire_reglage(self, nom, texte):
        _ecrire_sans_trou(self._REGLAGES[nom], texte)

    def ajouter_archive(self, code, date, texte):
        os.makedirs(HISTORIQUE_DIR, exist_ok=True)
        fichier = os.path.join(HISTORIQUE_DIR, f"partie_{date:%Y%m%d_%H%M%S}.json")
        with open(fichier, "w", encoding="utf-8") as f:
            f.write(texte)
        return f"le fichier {fichier}"

    def lister_archives(self, code):
        """Toutes les archives du dossier, de la plus récente à la plus ancienne (usage privé : pas de filtre par code)."""
        textes = []
        for fichier in sorted(glob.glob(os.path.join(HISTORIQUE_DIR, "partie_*.json")), reverse=True):
            try:
                with open(fichier, "r", encoding="utf-8") as f:
                    textes.append(f.read())
            except OSError:
                continue
        return textes


class StockageSQL:
    """Hébergé : parties et archives dans une base (SQLite ou Postgres), une ligne par partie, repérée par son code.
    Préférences et derniers noms ne sont pas gardés côté serveur : ils appartiendraient à tous les groupes à la fois."""

    multi_parties = True

    def __init__(self, url):
        from sqlalchemy import Column, Integer, MetaData, String, Table, Text, create_engine

        options = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {"pool_pre_ping": True}
        self.engine = create_engine(self.normaliser_url(url), **options)
        metadonnees = MetaData()
        self.parties = Table(
            "parties", metadonnees,
            Column("code", String(64), primary_key=True), Column("etat", Text, nullable=False), Column("maj", String(32), nullable=False),
        )
        self.archives = Table(
            "archives", metadonnees,
            Column("id", Integer, primary_key=True, autoincrement=True), Column("code", String(64), index=True, nullable=False),
            Column("date", String(40), nullable=False), Column("donnees", Text, nullable=False),
        )
        metadonnees.create_all(self.engine)
        self._verrou = threading.Lock()

    @staticmethod
    def normaliser_url(url):
        """postgres:// et postgresql:// (formes données par les hébergeurs) pilotés par psycopg 3."""
        for prefixe in ("postgres://", "postgresql://"):
            if url.startswith(prefixe):
                return "postgresql+psycopg://" + url[len(prefixe):]
        return url

    @staticmethod
    def _maintenant():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def lire_partie(self, code):
        if not code:
            return None
        with self.engine.connect() as c:
            return self._etat(c, code)

    def _etat(self, connexion, code):
        ligne = connexion.execute(self.parties.select().where(self.parties.c.code == code)).first()
        return ligne.etat if ligne else None

    def ecrire_partie(self, code, etat):
        if not code:
            raise ValueError("Une partie sans code ne peut pas être rangée en base.")
        texte = json.dumps(etat, ensure_ascii=False, separators=(",", ":"))
        valeurs = {"etat": texte, "maj": self._maintenant()}
        with self._verrou, self.engine.begin() as c:
            modifiees = c.execute(self.parties.update().where(self.parties.c.code == code).values(**valeurs)).rowcount
            if not modifiees:
                self._purger(c)  # une partie qui naît est l'occasion de faire le ménage
                c.execute(self.parties.insert().values(code=code, **valeurs))

    def _purger(self, connexion):
        limite = datetime.now(timezone.utc)
        connexion.execute(self.parties.delete().where(
            self.parties.c.maj < (limite - timedelta(days=PARTIES_CONSERVEES_JOURS)).isoformat(timespec="seconds")))
        connexion.execute(self.archives.delete().where(
            self.archives.c.date < (limite - timedelta(days=ARCHIVES_CONSERVEES_JOURS)).isoformat(timespec="seconds")))

    def supprimer_partie(self, code):
        if code:
            with self.engine.begin() as c:
                c.execute(self.parties.delete().where(self.parties.c.code == code))

    def mettre_de_cote(self, code, raison):
        """Une partie inutilisable change de code (`CODE.raison`) : elle reste en base pour examen, sans gêner."""
        with self.engine.begin() as c:
            c.execute(self.parties.update().where(self.parties.c.code == code).values(code=f"{code}.{raison}"))

    def modifie_le(self, code):
        with self.engine.connect() as c:
            ligne = c.execute(self.parties.select().where(self.parties.c.code == code)).first()
        return datetime.fromisoformat(ligne.maj) if ligne else None

    def lire_reglage(self, nom):
        return None

    def ecrire_reglage(self, nom, texte):
        pass

    def ajouter_archive(self, code, date, texte):
        with self.engine.begin() as c:
            c.execute(self.archives.insert().values(code=code or "", date=date.astimezone(timezone.utc).isoformat(timespec="seconds"), donnees=texte))
        return "la base de données"

    def lister_archives(self, code):
        """Archives de ce code seulement : celles des autres groupes ne sont pas à voir."""
        if not code:
            return []
        with self.engine.connect() as c:
            lignes = c.execute(self.archives.select().where(self.archives.c.code == code).order_by(self.archives.c.date.desc())).all()
        return [ligne.donnees for ligne in lignes]


@lru_cache(maxsize=4)
def _stockage_sql(url):
    return StockageSQL(url)


def stockage():
    """Le stockage courant : la base si DATABASE_URL est définie, sinon les fichiers."""
    url = database_url()
    return _stockage_sql(url) if url else StockageFichiers()
