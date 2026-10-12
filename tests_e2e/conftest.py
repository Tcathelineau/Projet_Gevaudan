"""Test de bout en bout : un vrai serveur Streamlit, un vrai navigateur (Playwright).

Lancement : uv sync --group e2e && uv run playwright install chromium && uv run pytest tests_e2e
En local, E2E_CHANNEL=chrome utilise le Chrome installé (rien à télécharger). Le son reste désactivé (défaut de l'app).
Les captures d'écran vont dans tests_e2e/captures/ (conservées comme artefacts par la CI).
"""

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CAPTURES = Path(__file__).resolve().parent / "captures"


def _port_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def serveur(tmp_path):
    """Serveur Streamlit isolé : dossier de travail vide (save.json, historique/ et préférences y atterrissent), sans base."""
    port = _port_libre()
    shutil.copytree(RACINE / ".streamlit", tmp_path / ".streamlit")  # le thème sombre est lu depuis le dossier de travail
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(RACINE / "src" / "loup_garou_app.py"), "--server.port", str(port),
         "--server.headless", "true", "--browser.gatherUsageStats", "false"],
        cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(120):
        try:
            if urllib.request.urlopen(f"{url}/_stcore/health", timeout=1).status == 200:
                break
        except OSError:
            time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("le serveur Streamlit ne démarre pas :\n" + (process.stdout.read() if process.stdout else ""))
    yield url
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def navigateur():
    with sync_playwright() as p:
        canal = os.environ.get("E2E_CHANNEL") or None
        navigateur = p.chromium.launch(channel=canal, headless=True)
        yield navigateur
        navigateur.close()


@pytest.fixture
def page(navigateur, request):
    CAPTURES.mkdir(exist_ok=True)
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 900}, locale="fr-FR")
    page = contexte.new_page()
    page.set_default_timeout(20_000)
    erreurs = []
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    yield page
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        page.screenshot(path=str(CAPTURES / f"echec_{request.node.name}.png"), full_page=True)
    assert not erreurs, f"erreurs JavaScript : {erreurs}"
    contexte.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultat = yield
    setattr(item, "rep_" + resultat.get_result().when, resultat.get_result())
