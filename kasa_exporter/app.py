# Copyright 2021-2022 Thomas Helander
# All rights reserved.
from flask import Flask, request, Response
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from .collectors import KasaSmartPlugCollector

METRICS_PATH = "/metrics"

app = Flask(__name__)


@app.route("/")
def index():
    return f"""<html>
    <head><title>Kasa Smart Plug Exporter</title></head>
    <body>
        <h1>Kasa Smart Plug Exporter</h1>
        <form method="get" action="/metrics">
        <label for="target">Target</label>
        <input type="text" name="target" id="target" placeholder="1.2.3.4"/>
        <button type="submit">Get</button>
        </form>
        <!--<p><a href="{METRICS_PATH}">Metrics</a></p>-->
    </body>
</html>"""


@app.route("/metrics")
def metrics():
    target = request.args.get("target")
    if not target:
        return "Required parameter missing: target", 400

    registry = CollectorRegistry()
    KasaSmartPlugCollector(target, registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)


def get_application():
    return app
