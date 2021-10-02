#!/bin/bash

OPTS=()
if [ -z "$1" ]; then
  OPTS=("$1")
else
  OPTS=(--http :9907 --module kasa_exporter.app:app --uid uwsgi --gid uwsgi)
fi

uwsgi "${OPTS[@]}"
