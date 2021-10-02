# Copyright 2021 Thomas Helander
# All rights reserved.
import sys
from flask import Flask
from prometheus_client import make_wsgi_app, REGISTRY
from subprocess import check_output, CalledProcessError
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from .collectors import KasaSmartPlugCollector

DEVICE_ADDRESS = "192.168.86.45"
METRICS_PATH = "/metrics"

app = Flask(__name__)


@app.route("/")
def index():
    return f"""<html>
    <head><title>Kasa Smart Plug Exporter</title></head>
    <body>
        <h1>Kasa Smart Plug Exporter</h1>
        <p><a href="{METRICS_PATH}">Metrics</a></p>
    </body>
</html>"""


# Verify the device is reachable
try:
    check_output(["ping", "-c", "1", "-W", "5", DEVICE_ADDRESS])
except CalledProcessError:
    sys.exit(f"Failed to ping {DEVICE_ADDRESS}.")

KasaSmartPlugCollector(DEVICE_ADDRESS, REGISTRY)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {METRICS_PATH: make_wsgi_app()})


def get_application():
    return app
