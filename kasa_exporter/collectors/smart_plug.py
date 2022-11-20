import asyncio
import kasa.exceptions
import sys
from kasa import SmartPlug
from prometheus_client.core import GaugeMetricFamily
from typing import List
from kasa_exporter.utils import ping


class KasaSmartPlugCollector:
    """Prometheus collector for Kasa Smart Plugs with energy monitoring."""
    def __init__(self, address, registry=None):
        self.address = address
        self.device = SmartPlug(address)

        if registry:
            registry.register(self)

    def get_device_current(self) -> float:
        """Returns the current pulled by the device in mA."""
        if not self.device.has_emeter:
            return 0.0

        return self.device.emeter_realtime.get("current_ma")

    def get_device_voltage(self) -> float:
        """Returns the input voltage of the device in mV."""
        if not self.device.has_emeter:
            return 0.0

        return self.device.emeter_realtime.get("voltage_mv")

    def get_device_power(self) -> float:
        """Returns the power consumption of the device in mW."""
        if not self.device.has_emeter:
            return 0.0

        return self.device.emeter_realtime.get("power_mw")

    def collect(self) -> List[GaugeMetricFamily]:
        if not ping(self.address):
            print(f"{self.address} not responding", file=sys.stderr)
            return []

        evtloop = self.device.protocol.loop
        if not evtloop:
            evtloop = asyncio.new_event_loop()

        try:
            evtloop.run_until_complete(self.device.update())
        except kasa.exceptions.SmartDeviceException:
            print("Failed to update device")
            return []

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
