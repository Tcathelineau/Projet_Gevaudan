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
    categorie: str = "pouvoir"  # rangement dans l'écran de composition (clés de CATEGORIES)
    lot: int = 1  # nombre de cartes ajoutées ensemble quand le rôle est coché (Sœurs, Frères)
    description: str = ""  # une ou deux phrases affichées en infobulle à la composition
    priorite_nuit: int = 2  # plus petit = joue plus tôt dans la nuit (à égalité : ordre des joueurs)


ROLES = {
    "loup": Role(
        key="loup",
        description="Dès la deuxième nuit, se concerte avec la meute pour dévorer un villageois. Les loups gagnent quand ils sont plus nombreux que les autres.",
        nom="Loup-Garou",
        emoji="🐺",
        degrade="radial-gradient(circle at 50% 30%, #6b1f22, #2a0a0c 75%)",
        camp="loups",
        unique=False,
    ),
    "sorciere": Role(
        key="sorciere",
        description="Détient une potion de soin pour sauver la victime des loups (sans savoir qui c'est). En option, des potions de mort pour empoisonner un joueur.",
        nom="Sorcière",
        emoji="🧪",
        degrade="radial-gradient(circle at 50% 30%, #3d1f5c, #170a29 75%)",
        etat_initial={"potions_sorciere": 1, "potions_mort_sorciere": 0, "soin_sorciere": False, "cible_poison": None},
    ),
    "voyante": Role(
        key="voyante",
        categorie="info",
        description="Sonde un joueur lors de ses nuits de vision et découvre son rôle.",
        nom="Voyante",
        emoji="🔮",
        degrade="radial-gradient(circle at 50% 30%, #1c2b5c, #090f29 75%)",
    ),
    "cupidon": Role(
        key="cupidon",
        categorie="chaos",
        description="La première nuit, lie deux joueurs par l'amour (lui compris) : si l'un meurt, l'autre le suit.",
        nom="Cupidon",
        emoji="🏹",
        degrade="radial-gradient(circle at 50% 30%, #6b2748, #29101f 75%)",
    ),
    "chasseur": Role(
        key="chasseur",
        description="À sa mort, tire une dernière balle sur le joueur de son choix, ou renonce.",
        nom="Chasseur",
        emoji="🔫",
        degrade="radial-gradient(circle at 50% 30%, #6b4a1f, #291b0a 75%)",
        tir_a_la_mort=True,
    ),
    "salvateur": Role(
        key="salvateur",
        description="Protège un joueur chaque nuit contre les loups, jamais le même deux nuits de suite.",
        nom="Salvateur",
        emoji="🛡️",
        degrade="radial-gradient(circle at 50% 30%, #1f5c55, #0a2925 75%)",
        etat_initial={"protege_nuit": None, "protege_precedent": None},
        recommande=False,
    ),
    "enfant_sauvage": Role(
        key="enfant_sauvage",
        categorie="chaos",
        description="Choisit un mentor la première nuit ; si celui-ci meurt, il devient loup-garou.",
        nom="Enfant sauvage",
        emoji="🧒",
        degrade="radial-gradient(circle at 50% 30%, #4a5c1f, #1c260a 75%)",
        etat_initial={"mentor_enfant": None},
        recommande=False,
    ),
    "voleur": Role(
        key="voleur",
        categorie="chaos",
        description="Deux cartes restent au milieu de la table : la première nuit, il peut prendre le rôle de l'une d'elles.",
        nom="Voleur",
        emoji="🃏",
        degrade="radial-gradient(circle at 50% 30%, #5c4a1f, #261d0a 75%)",
        cartes_en_plus=2,
        recommande=False,
        priorite_nuit=0,
    ),
    "renard": Role(
        key="renard",
        categorie="info",
        description="Dès la deuxième nuit, flaire un groupe de trois joueurs et apprend si un loup s'y cache ; sans loup, il perd son flair.",
        nom="Renard",
        emoji="🦊",
        degrade="radial-gradient(circle at 50% 30%, #8a3f12, #33150a 75%)",
        recommande=False,
    ),
    "loup_blanc": Role(
        key="loup_blanc",
        categorie="loups",
        description="Loup solitaire : une nuit sur deux, il peut dévorer l'un de ses frères. Il gagne seul, en éliminant tout le monde.",
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
        categorie="chaos",
        description="Choisit son camp en secret la première nuit : villageois ou loup-garou. Son camp n'est pas dévoilé à sa mort.",
        nom="Chien-Loup",
        emoji="🐕",
        degrade="radial-gradient(circle at 50% 30%, #5a4632, #1e1710 75%)",
        recommande=False,
        camp_secret=True,
        priorite_nuit=1,
    ),
    "louveteau": Role(
        key="louveteau",
        categorie="loups",
        nom="Louveteau",
        emoji="🐶",
        degrade="radial-gradient(circle at 50% 30%, #7a3a2e, #2e130e 75%)",
        description="Loup comme les autres, mais s'il meurt, la meute dévore deux victimes la nuit suivante.",
        camp="loups",
        etat_initial={"double_victime": False},
        recommande=False,
    ),
    "soeur": Role(
        key="soeur",
        categorie="info",
        nom="Sœur",
        emoji="👭",
        degrade="radial-gradient(circle at 50% 30%, #6b3d6b, #261426 75%)",
        description="Deux cartes jouées ensemble : les sœurs se connaissent dès la première nuit et peuvent compter l'une sur l'autre.",
        lot=2,
        recommande=False,
    ),
    "frere": Role(
        key="frere",
        categorie="info",
        nom="Frère",
        emoji="👬",
        degrade="radial-gradient(circle at 50% 30%, #2f4f7a, #0f1b2e 75%)",
        description="Trois cartes jouées ensemble : les frères se connaissent dès la première nuit et peuvent compter les uns sur les autres.",
        lot=3,
        recommande=False,
    ),
    "servante": Role(
        key="servante",
        categorie="chaos",
        nom="Servante dévouée",
        emoji="🧹",
        degrade="radial-gradient(circle at 50% 30%, #5c5c2f, #25250f 75%)",
        description="La nuit qui suit un vote, elle peut reprendre en secret le rôle du joueur condamné ; le village apprend le lendemain qu'elle est intervenue.",
        recommande=False,
    ),
    "juge_begue": Role(
        key="juge_begue",
        categorie="chaos",
        nom="Juge bègue",
        emoji="⚖️",
        degrade="radial-gradient(circle at 50% 30%, #4a4a6b, #17172a 75%)",
        description="Une seule fois dans la partie, il exige un second vote du village juste après le premier.",
        etat_initial={"juge_utilise": False, "second_vote": None},
        recommande=False,
    ),
    "villageois": Role(
        key="villageois",
        description="Aucun pouvoir : il dort, débat et vote le jour pour démasquer les loups.",
        nom="Villageois",
        emoji="🧑‍🌾",
        degrade="radial-gradient(circle at 50% 30%, #35431f, #141a0d 75%)",
        unique=False,
    ),
}


# Catégories de l'écran de composition, dans l'ordre d'affichage : clé -> (emoji, titre).
CATEGORIES = {
    "info": ("🔮", "Information"),
    "pouvoir": ("🛡️", "Protection et pouvoirs de mort"),
    "chaos": ("🌀", "Chaos"),
    "loups": ("🐺", "Loups spéciaux"),
}


# Rôles proposés (avec un nombre à régler) dans l'écran de composition : tous
# sauf le loup (obligatoire, quantité libre, traité à part) et le villageois
# (calculé automatiquement en reste de table).
ROLES_SPECIAUX = [r for cle, r in ROLES.items() if cle not in ("loup", "villageois")]
