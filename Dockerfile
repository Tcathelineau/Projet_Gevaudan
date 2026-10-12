# Image de production : Streamlit + dépendances épinglées par uv.lock, sans les outils de développement.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Les dépendances d'abord : cette couche ne se reconstruit que si pyproject.toml ou uv.lock changent.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY .streamlit ./.streamlit
COPY src ./src

# Utilisateur sans droits ; le dossier de travail reste inscriptible (mode fichiers : save.json, historique/).
RUN useradd --create-home --uid 10001 gevaudan && chown -R gevaudan /app
USER gevaudan

# Les hébergeurs fournissent souvent PORT ; la valeur par défaut convient en local.
ENV PORT=8501
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/_stcore/health', timeout=4)"

CMD ["sh", "-c", "exec streamlit run src/loup_garou_app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
