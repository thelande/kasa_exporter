# Copyright 2021-2022,2024 Thomas Helander
# All rights reserved.
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from .collectors import KasaSmartPlugCollector

METRICS_PATH = "/metrics"

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<html>
    <head><title>Kasa Smart Plug Exporter</title></head>
    <body>
        <h1>Kasa Smart Plug Exporter</h1>
        <form method="get" action="/metrics">
        <label for="target">Target</label>
        <input type="text" name="target" id="target" placeholder="1.2.3.4"/>
        <button type="submit">Get</button>
        </form>
    </body>
</html>"""


@app.get("/metrics")
def metrics(target: str) -> Response:
    registry = CollectorRegistry()
    KasaSmartPlugCollector(target, registry)
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


def get_application():
    return app
