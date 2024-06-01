FROM python:3.12-alpine as builder

WORKDIR /usr/src/app

RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
      build-base \
      libffi-dev \
    ; \
    pip install --no-cache-dir --quiet --progress-bar off poetry; \
    apk del .build-deps

COPY poetry.lock pyproject.toml ./
COPY kasa_exporter ./kasa_exporter/
RUN poetry build

FROM python:3.12-alpine as application
LABEL maintainer="Tom Helander <thomas.helander@gmail.com>"

RUN set -eux; \
    apk update; \
    apk upgrade --no-cache -v; \
    apk cache purge

RUN set -eux; \
    addgroup -S uvicorn; \
    adduser -S -s /sbin/nologin -G uvicorn -H uvicorn

RUN apk add --no-cache \
      bash \
      su-exec

COPY --from=builder /usr/src/app/dist/*.whl /tmp/
RUN pip install --quiet --no-cache-dir --progress-bar off /tmp/*.whl

COPY entrypoint.sh /usr/local/bin
EXPOSE 9907
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
