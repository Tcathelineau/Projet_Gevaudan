import wave

import pytest

from loup_garou.roles import ROLES
from loup_garou.ui.illustrations import ASSETS, svg_role


@pytest.mark.parametrize("cle", list(ROLES) + ["logo"])
def test_chaque_role_a_son_illustration(cle):
    svg = svg_role(cle)
    assert svg.startswith("<svg") and 'class="art"' in svg
    assert "currentColor" in svg
    assert 'd="M0 0h512v512H0z"' not in svg  # fond noir retiré


def test_role_sans_illustration_retombe_sur_le_repli():
    assert svg_role("inconnu", repli="🐺") == "🐺"


def test_les_credits_citent_chaque_illustration():
    credits = (ASSETS / "CREDITS.md").read_text(encoding="utf-8")
    for cle in ROLES:
        assert f"`{cle}`" in credits
    assert "Creative Commons Attribution 3.0" in credits
    assert "FreePD" in credits and "Creepy Hallow" in credits


@pytest.mark.parametrize("nom", ["hurlement", "victoire_village", "victoire_loups"])
def test_les_bruitages_sont_des_wav_mono_16_bits(nom):
    with wave.open(str(ASSETS / "sons" / f"{nom}.wav")) as f:
        assert f.getnchannels() == 1 and f.getsampwidth() == 2
        assert 2 < f.getnframes() / f.getframerate() < 10


@pytest.mark.parametrize("nom", ["musique_nuit", "musique_jour", "musique_conseil"])
def test_les_musiques_durent_plus_d_une_minute(nom):
    # MP3 mono à 64 kbit/s : 8 ko par seconde, donc plus de 60 s dépasse 480 ko (les pistes durent 2 minutes ou plus).
    assert (ASSETS / "sons" / f"{nom}.mp3").stat().st_size > 480_000


def test_le_favicon_existe():
    assert (ASSETS / "favicon.png").stat().st_size > 1000
