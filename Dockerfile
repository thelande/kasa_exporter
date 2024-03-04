FROM python:3.10-alpine as builder

WORKDIR /usr/src/app

RUN set -eux; \
    pip install --no-cache-dir --quiet --progress-bar off build

COPY setup.cfg pyproject.toml build.sh ./
COPY kasa_exporter ./kasa_exporter/
RUN set -eux; \
    chmod +x build.sh; \
    ./build.sh

FROM python:3.10-alpine as application

RUN set -eux; \
    apk update; \
    apk upgrade --no-cache -v; \
    apk cache purge

RUN set -eux; \
    addgroup -S uwsgi; \
    adduser -S -s /sbin/nologin -G uwsgi -H uwsgi

RUN set -eux; \
    apk add --no-cache \
      bash \
      iputils \
      pcre \
      su-exec \
    ; \
    apk add --no-cache --virtual .build-deps \
      build-base \
      linux-headers \
      pcre-dev \
    ; \
    pip install --quiet --no-cache-dir --progress-bar off uwsgi; \
    apk del .build-deps

COPY --from=builder /usr/src/app/dist/*.whl /tmp/
RUN set -eux; \
    pip install --quiet --no-cache-dir --progress-bar off /tmp/*.whl

COPY entrypoint.sh /usr/local/bin
COPY uwsgi.ini /usr/local/etc
EXPOSE 9191 9907
CMD ["/usr/local/etc/uwsgi.ini"]
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
