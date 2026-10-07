"""Garde-fous d'accessibilité (WCAG 2.2 AA) : contrastes des couleurs de texte et présence des réglages clés.

Ce ne sont pas des preuves de conformité : un audit complet (lecteur d'écran, clavier) reste à faire.
"""

from pathlib import Path

import pytest

from loup_garou.roles import ROLES
from loup_garou.ui import styles
from loup_garou.ui.illustrations import svg_role

FOND_PAGE, FOND_BARRE, FOND_MENU = "#0e1117", "#262730", "#1c1c22"


def luminance(couleur):
    canaux = [int(couleur[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in canaux]
    return .2126 * lin[0] + .7152 * lin[1] + .0722 * lin[2]


def contraste(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + .05) / (lb + .05)


# (texte, fond, usage) : couleurs de texte réellement utilisées dans styles.py, avec leur fond le plus défavorable.
TEXTES = [
    ("#f0d890", FOND_PAGE), ("#ece3d2", FOND_PAGE), ("#f2e9d8", FOND_PAGE), ("#fff4d0", FOND_PAGE),
    ("#c9a44c", FOND_PAGE), ("#b9b09c", FOND_PAGE), ("#b9b09c", FOND_BARRE), ("#e3b8c4", FOND_PAGE),
    ("#d98080", FOND_MENU), ("#e8706b", FOND_PAGE), ("#4caf6a", FOND_PAGE), ("#eceaf4", FOND_PAGE),
    ("#ffffff", "#b3335a"), ("#ffd0e6", "#260b19"), ("#ff9ccf", "#260b19"), ("#ffe3f0", "#260b19"),
    ("#000000", "#d64545"), ("#000000", "#4caf6a"), ("#000000", "#f06fb5"), ("#000000", "#8a8a9a"),
]


@pytest.mark.parametrize("texte, fond", TEXTES)
def test_contraste_du_texte_au_moins_4_5(texte, fond):
    assert contraste(texte, fond) >= 4.5, (texte, fond, round(contraste(texte, fond), 2))


def test_le_rouge_des_loups_en_petit_texte_a_ete_eclairci():
    assert contraste("#d64545", FOND_PAGE) < 4.5  # raison d'être de #e8706b ; si ce test casse, la règle est inutile
    assert ".doc-loups .doc-camp { color: #e8706b; }" in styles.CSS_DOCUMENTATION


def test_le_focus_clavier_est_visible_et_les_animations_se_reduisent():
    source = Path(styles.__file__).read_text(encoding="utf-8")
    assert "button:focus-visible" in source and "outline: 3px solid" in source
    assert source.count("prefers-reduced-motion") >= 3


def test_les_illustrations_sont_decoratives_pour_les_lecteurs_d_ecran():
    for cle in ROLES:
        assert 'aria-hidden="true"' in svg_role(cle)


def test_la_page_declare_sa_langue():
    from loup_garou.ui import barre_laterale

    assert "documentElement.lang = 'fr'" in Path(barre_laterale.__file__).read_text(encoding="utf-8")
