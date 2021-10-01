#!/usr/bin/env python3
# Copyright 2021 Thomas Helander
# All rights reserved.
import asyncio
from flask import Flask
from kasa import SmartPlug
from prometheus_client import make_wsgi_app, REGISTRY
from prometheus_client.core import GaugeMetricFamily
from werkzeug.middleware.dispatcher import DispatcherMiddleware

DEVICE_ADDRESS = "192.168.86.45"
METRICS_PATH = "/metrics"


class KasaSmartPlugCollector:
    def __init__(self, address, registry=None):
        self.device = SmartPlug(address)

        if registry:
            registry.register(self)

    def get_device_current(self) -> float:
        """Returns the current pulled by the device in mA."""
        if not self.device.has_emeter:
            return None

        return self.device.emeter_realtime.get("current_ma")

    def get_device_voltage(self) -> float:
        """Returns the input voltage of the device in mV."""
        if not self.device.has_emeter:
            return None

        return self.device.emeter_realtime.get("voltage_mv")

    def get_device_power(self) -> float:
        """Returns the power consumption of the device in mW."""
        if not self.device.has_emeter:
            return None

        return self.device.emeter_realtime.get("power_mw")

    def collect(self):
        asyncio.run(self.device.update())

        current = GaugeMetricFamily(
            "kasa_device_current",
            "Current pulled by the device",
            labels=["device"],
            unit="ma",
        )
        voltage = GaugeMetricFamily(
            "kasa_device_voltage",
            "Input voltage of the device",
            labels=["device"],
            unit="mv",
        )
        power = GaugeMetricFamily(
            "kasa_device_power_mw",
            "Power consumption of the device",
            labels=["device"],
            unit="mw",
        )

        current.add_metric([self.device.alias], self.get_device_current())
        voltage.add_metric([self.device.alias], self.get_device_voltage())
        power.add_metric([self.device.alias], self.get_device_power())

        return [current, voltage, power]


app = Flask(__name__)
KasaSmartPlugCollector(DEVICE_ADDRESS, REGISTRY)


@app.route("/")
def index():
    return f"""<html>
    <head><title>Kasa Smart Plug Exporter</title></head>
    <body>
        <h1>Kasa Smart Plug Exporter</h1>
        <p><a href="{METRICS_PATH}">Metrics</a></p>
    </body>
</html>"""


app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {METRICS_PATH: make_wsgi_app()})
