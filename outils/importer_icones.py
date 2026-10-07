"""Télécharge les icônes de rôles depuis game-icons.net (dépôt GitHub game-icons/icons, licence CC BY 3.0).

Usage : python3 outils/importer_icones.py
Les SVG sont recolorés (fond retiré, `currentColor`) et écrits dans src/loup_garou/assets/roles/,
avec le fichier de crédits exigé par la licence.
"""

import re
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets"
URL = "https://raw.githubusercontent.com/game-icons/icons/master/{auteur}/{icone}.svg"
AUTEURS = {"lorc": "Lorc", "delapouite": "Delapouite"}

# clé de rôle (ou "logo", "dos") -> (dossier auteur, nom de l'icône)
ICONES = {
    "loup": ("lorc", "wolf-head"),
    "villageois": ("delapouite", "farmer"),
    "sorciere": ("lorc", "potion-ball"),
    "voyante": ("lorc", "crystal-ball"),
    "cupidon": ("lorc", "cupidon-arrow"),
    "chasseur": ("lorc", "blunderbuss"),
    "salvateur": ("lorc", "shield-reflect"),
    "enfant_sauvage": ("delapouite", "caveman"),
    "voleur": ("delapouite", "robber"),
    "renard": ("lorc", "fox-head"),
    "loup_blanc": ("lorc", "werewolf"),
    "chien_loup": ("delapouite", "sitting-dog"),
    "louveteau": ("lorc", "paw-print"),
    "soeur": ("delapouite", "shaking-hands"),
    "frere": ("delapouite", "three-friends"),
    "servante": ("delapouite", "broom"),
    "juge_begue": ("lorc", "gavel"),
    "logo": ("lorc", "wolf-howl"),
}


def recolorer(svg):
    svg = re.sub(r'<path d="M0 0h512v512H0z"/>', "", svg, count=1)
    svg = svg.replace('fill="#fff"', 'fill="currentColor"')
    return svg.strip() + "\n"


def main():
    (RACINE / "roles").mkdir(parents=True, exist_ok=True)
    credits = []
    for cle, (auteur, icone) in ICONES.items():
        with urllib.request.urlopen(URL.format(auteur=auteur, icone=icone)) as r:
            svg = r.read().decode("utf-8")
        assert "currentColor" in recolorer(svg), (cle, "icône inattendue")
        (RACINE / "roles" / f"{cle}.svg").write_text(recolorer(svg), encoding="utf-8")
        credits.append(f"- `{cle}` : « {icone} » par {AUTEURS[auteur]}, https://game-icons.net/1x1/{auteur}/{icone}.html")
    (RACINE / "CREDITS.md").write_text(
        "# Crédits des illustrations\n\n"
        "Les icônes des rôles viennent de [game-icons.net](https://game-icons.net), "
        "sous licence [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/). "
        "Elles ont été recolorées (fond retiré). Auteurs : Lorc (lorcblog.blogspot.com) et "
        "Delapouite (delapouite.com).\n\n" + "\n".join(credits) + "\n"
        "\n## Musiques\n\n"
        "Les trois musiques viennent de [FreePD](https://freepd.com), morceaux en domaine public "
        "([CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), aucune attribution requise ; remerciements "
        "à leurs auteurs), récupérés via le miroir GitHub [0lhi/FreePD](https://github.com/0lhi/FreePD) :\n\n"
        "- nuit : « Creepy Hallow » (Horror)\n- jour : « Nostalgic Piano » (Romance)\n"
        "- conseil : « Find Them » (Scoring)\n\n"
        "Préparées (mono, volume commun, fondus, MP3) par `outils/importer_musiques.py`.\n\n"
        "## Bruitages\n\nLe hurlement et les sons de victoire sont synthétisés par `outils/generer_sons.py` "
        "(aucun échantillon tiers).\n\nRégénérer les icônes : `python3 outils/importer_icones.py`.\n",
        encoding="utf-8",
    )
    print(f"{len(credits)} icônes importées")


if __name__ == "__main__":
    main()
