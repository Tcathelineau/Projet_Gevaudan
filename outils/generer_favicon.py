"""Compose l'icône de l'application (loup hurlant, or sur nuit bleue) : src/loup_garou/assets/favicon.png.

Usage : uv run --python 3.12 --with cairosvg python outils/generer_favicon.py
"""

import re
from pathlib import Path

import cairosvg

ASSETS = Path(__file__).resolve().parent.parent / "src" / "loup_garou" / "assets"

loup = (ASSETS / "roles" / "logo.svg").read_text(encoding="utf-8")
chemins = re.search(r"<svg[^>]*>(.*)</svg>", loup, re.S).group(1).replace("currentColor", "#e2c274")
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><radialGradient id="g" cx=".5" cy=".3" r=".85"><stop offset="0" stop-color="#2d3370"/><stop offset="1" stop-color="#090a1c"/></radialGradient></defs>
<rect width="512" height="512" rx="104" fill="url(#g)"/>
<rect x="14" y="14" width="484" height="484" rx="92" fill="none" stroke="#c9a44c" stroke-width="10"/>
<g transform="translate(76 76) scale(0.7)">{chemins}</g></svg>"""
cairosvg.svg2png(bytestring=svg.encode(), write_to=str(ASSETS / "favicon.png"), output_width=256, output_height=256)
print("favicon.png écrit")
