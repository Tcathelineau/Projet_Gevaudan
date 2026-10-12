"""Code de partie : identifiant court qui permet de reprendre une partie parmi plusieurs sur le même serveur."""

import secrets

# Sans 0, O, 1, I, L : on recopie ce code à la main.
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGUEUR = 8  # 31 ** 8, environ 8,5 * 10 ** 11 codes : le code fait office de lien secret


def nouveau_code():
    return "".join(secrets.choice(ALPHABET) for _ in range(LONGUEUR))


def normaliser_code(texte):
    """Code saisi ou lu dans une adresse (« k7m2-qx9p » devient « K7M2QX9P »), ou None s'il est invalide."""
    if not isinstance(texte, str):
        return None
    code = "".join(c for c in texte.upper() if c.isalnum())
    if len(code) != LONGUEUR or any(c not in ALPHABET for c in code):
        return None
    return code


def afficher_code(code):
    """« K7M2QX9P » s'affiche « K7M2-QX9P »."""
    return f"{code[:LONGUEUR // 2]}-{code[LONGUEUR // 2:]}" if code else ""
