FROM python:3.14-slim AS builder

WORKDIR /usr/src/app

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV MISE_DATA_DIR="/mise" \
    MISE_CONFIG_DIR="/mise" \
    MISE_CACHE_DIR="/mise/cache" \
    MISE_INSTALL_PATH="/usr/local/bin/mise" \
    MISE_VERSION="2026.8.2" \
    PATH="/mise/shims:$PATH"

RUN set -eux; \
    apt update; \
    apt install -y --no-install-recommends \
        curl \
    ; \
    apt clean all; \
    rm -rf /var/lib/apt/lists/*

RUN curl https://mise.run | sh

COPY .mise.toml .mise.lock ./
RUN set -eux; \
    mise trust -a; \
    mise install

COPY uv.lock pyproject.toml ./
COPY src/ ./src/

RUN uv build

FROM python:3.14-alpine AS application
LABEL maintainer="Tom Helander <thomas.helander@gmail.com>"

RUN set -eux; \
    apk update; \
    apk upgrade --no-cache -v; \
    apk cache purge

RUN set -eux; \
    addgroup -g 1000 uvicorn; \
    adduser -u 1000 -s /sbin/nologin -G uvicorn -D -H uvicorn

RUN apk add --no-cache \
    bash \
    su-exec

COPY --from=builder /usr/src/app/dist/*.whl /tmp/
RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
        build-base \
        libffi-dev \
    ; \
    pip install --quiet --no-cache-dir --progress-bar off /tmp/*.whl; \
    apk del .build-deps

COPY entrypoint.sh /usr/local/bin
EXPOSE 9907
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
