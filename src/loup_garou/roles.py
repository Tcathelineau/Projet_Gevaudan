"""Registre des rôles : un rôle = une entrée de `ROLES` (données seulement, sans interface)."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Role:
    key: str
    nom: str
    emoji: str
    degrade: str  # dégradé CSS de fond pour la carte de rôle
    camp: str = "village"  # "village" ou "loups" : détermine les conditions de victoire
    unique: bool = True  # au plus un exemplaire proposé par défaut à la composition
    etat_initial: dict = field(default_factory=dict)  # clés d'état de partie propres à ce rôle
    cartes_en_plus: int = 0  # cartes ajoutées au paquet et laissées au milieu de la table
    recommande: bool = True  # coché par défaut dans la composition suggérée
    tir_a_la_mort: bool = False  # à sa mort, ce rôle peut emporter un autre joueur avec lui
    solitaire: bool = False  # gagne seul, en éliminant tout le monde (village et loups compris)
    camp_secret: bool = False  # son camp n'est pas révélé à sa mort (le joueur a choisi le sien)
    priorite_nuit: int = 2  # plus petit = joue plus tôt dans la nuit (à égalité : ordre des joueurs)


ROLES = {
    "loup": Role(
        key="loup",
        nom="Loup-Garou",
        emoji="🐺",
        degrade="radial-gradient(circle at 50% 30%, #6b1f22, #2a0a0c 75%)",
        camp="loups",
        unique=False,
    ),
    "sorciere": Role(
        key="sorciere",
        nom="Sorcière",
        emoji="🧪",
        degrade="radial-gradient(circle at 50% 30%, #3d1f5c, #170a29 75%)",
        etat_initial={"potions_sorciere": 1, "potions_mort_sorciere": 0, "soin_sorciere": False, "cible_poison": None},
    ),
    "voyante": Role(
        key="voyante",
        nom="Voyante",
        emoji="🔮",
        degrade="radial-gradient(circle at 50% 30%, #1c2b5c, #090f29 75%)",
    ),
    "cupidon": Role(
        key="cupidon",
        nom="Cupidon",
        emoji="🏹",
        degrade="radial-gradient(circle at 50% 30%, #6b2748, #29101f 75%)",
    ),
    "chasseur": Role(
        key="chasseur",
        nom="Chasseur",
        emoji="🔫",
        degrade="radial-gradient(circle at 50% 30%, #6b4a1f, #291b0a 75%)",
        tir_a_la_mort=True,
    ),
    "salvateur": Role(
        key="salvateur",
        nom="Salvateur",
        emoji="🛡️",
        degrade="radial-gradient(circle at 50% 30%, #1f5c55, #0a2925 75%)",
        etat_initial={"protege_nuit": None, "protege_precedent": None},
        recommande=False,
    ),
    "enfant_sauvage": Role(
        key="enfant_sauvage",
        nom="Enfant sauvage",
        emoji="🧒",
        degrade="radial-gradient(circle at 50% 30%, #4a5c1f, #1c260a 75%)",
        etat_initial={"mentor_enfant": None},
        recommande=False,
    ),
    "voleur": Role(
        key="voleur",
        nom="Voleur",
        emoji="🃏",
        degrade="radial-gradient(circle at 50% 30%, #5c4a1f, #261d0a 75%)",
        cartes_en_plus=2,
        recommande=False,
        priorite_nuit=0,
    ),
    "renard": Role(
        key="renard",
        nom="Renard",
        emoji="🦊",
        degrade="radial-gradient(circle at 50% 30%, #8a3f12, #33150a 75%)",
        recommande=False,
    ),
    "loup_blanc": Role(
        key="loup_blanc",
        nom="Loup Blanc",
        emoji="🌕",
        degrade="radial-gradient(circle at 50% 30%, #6e6e78, #24242b 75%)",
        camp="loups",
        etat_initial={"cible_loup_blanc": None, "vote_loup_blanc": None},
        recommande=False,
        solitaire=True,
    ),
    "chien_loup": Role(
        key="chien_loup",
        nom="Chien-Loup",
        emoji="🐕",
        degrade="radial-gradient(circle at 50% 30%, #5a4632, #1e1710 75%)",
        recommande=False,
        camp_secret=True,
        priorite_nuit=1,
    ),
    "villageois": Role(
        key="villageois",
        nom="Villageois",
        emoji="🧑‍🌾",
        degrade="radial-gradient(circle at 50% 30%, #35431f, #141a0d 75%)",
        unique=False,
    ),
}


# Rôles proposés (avec un nombre à régler) dans l'écran de composition : tous
# sauf le loup (obligatoire, quantité libre, traité à part) et le villageois
# (calculé automatiquement en reste de table).
ROLES_SPECIAUX = [r for cle, r in ROLES.items() if cle not in ("loup", "villageois")]
