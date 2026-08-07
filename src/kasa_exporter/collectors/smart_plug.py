import asyncio

import kasa.exceptions
from kasa import Device, Module
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector


class KasaSmartPlugCollector(Collector):
    """Prometheus collector for Kasa Smart Plugs with energy monitoring."""

    def __init__(self, address: str, registry=None):
        self.address = address
        self.device: Device | None = None

        if registry:
            registry.register(self)

    async def update_device(self):
        if not self.device:
            self.device = await Device.connect(host=self.address)
        await self.device.update()

    def collect(self) -> list[GaugeMetricFamily]:
        metrics = []
        up = GaugeMetricFamily("kasa_up", "Is the device up", labels=["device"])
        metrics.append(up)

        try:
            asyncio.run(self.update_device())
        except kasa.exceptions.KasaException:
            up.add_metric([], 0)
            return metrics

        if not self.device:
            up.add_metric([], 0)
            return metrics

        up.add_metric([], 1)

        info = InfoMetricFamily("kasa_meta", "Device information")
        info.add_metric([], {"alias": self.device.alias or ""})
        metrics.append(info)

        if self.device.has_emeter:
            energy = self.device.modules[Module.Energy]
            current = GaugeMetricFamily(
                "kasa_device_current", "Current pulled by the device", unit="ma"
            )
            voltage = GaugeMetricFamily(
                "kasa_device_voltage", "Input voltage of the device", unit="mv"
            )
            power = GaugeMetricFamily(
                "kasa_device_power_mw", "Power consumption of the device", unit="mw"
            )

            if energy.current is not None:
                current.add_metric([], energy.current * 1000)
            if energy.voltage is not None:
                voltage.add_metric([], energy.voltage * 1000)

            if energy.current is not None and energy.voltage is not None:
                power.add_metric([], energy.current * energy.voltage * 1000)

            metrics.extend([current, voltage, power])

        return metrics
