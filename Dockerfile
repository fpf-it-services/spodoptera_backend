FROM python:3.13-alpine

# Étape 1 - Configuration de base
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Étape 2 - Installation des dépendances système (couche séparée)
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev

# Étape 3 - Installation des dépendances Python (optimisation cache)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# Étape 4 - Nettoyage (couche séparée)
RUN apk del .build-deps

# Étape 5 - Copie du code applicatif
WORKDIR /usr/src/app
COPY . .

# Étape 6 - Configuration Gunicorn
ENV GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_MAX_REQUESTS=1000

EXPOSE 8000

CMD ["sh", "-c", \
    "gunicorn --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS} \
    --threads ${GUNICORN_THREADS} \
    --timeout ${GUNICORN_TIMEOUT} \
    --max-requests ${GUNICORN_MAX_REQUESTS} \
    --access-logfile - \
    --error-logfile - \
    spodoptera_backend.wsgi:application"]