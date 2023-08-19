"""Common utilities for VeSync Component."""
import logging

from homeassistant.helpers.entity import ToggleEntity

from .const import VS_FANS, VS_LIGHTS, VS_SWITCHES, VS_HUMIDIFIERS

_LOGGER = logging.getLogger(__name__)

HUMI_DEV_TYPE_TO_HA = {
    "Classic300S": "humidifier"
}


async def async_process_devices(hass, manager):
    """Assign devices to proper component."""
    devices = {}
    devices[VS_SWITCHES] = []
    devices[VS_FANS] = []
    devices[VS_LIGHTS] = []
    devices[VS_HUMIDIFIERS] = []

    await hass.async_add_executor_job(manager.update)

    fans_count = 0
    humidifiers_count = 0
    lights_count = 0
    outlets_count = 0
    switches_count = 0
    if manager.fans:
        for fan in manager.fans:
            if HUMI_DEV_TYPE_TO_HA.get(fan.device_type):
                devices[VS_HUMIDIFIERS].append(fan)
                devices[VS_SWITCHES].append(fan)
                devices[VS_LIGHTS].append(fan)
                humidifiers_count += 1
                switches_count += 1
                lights_count += 1
            else:
                devices[VS_FANS].append(fan)
                fans_count += 1

    if manager.bulbs:
        devices[VS_LIGHTS].extend(manager.bulbs)
        lights_count += len(manager.bulbs)

    if manager.outlets:
        devices[VS_SWITCHES].extend(manager.outlets)
        outlets_count += len(manager.outlets)

    if manager.switches:
        for switch in manager.switches:
            if not switch.is_dimmable():
                devices[VS_SWITCHES].append(switch)
            else:
                devices[VS_LIGHTS].append(switch)
        switches_count += len(manager.switches)

    if fans_count > 0:
        _LOGGER.info("%d VeSync fans found", fans_count)
    if humidifiers_count > 0:
        _LOGGER.info("%d VeSync humidifiers found", humidifiers_count)
    if lights_count > 0:
        _LOGGER.info("%d VeSync lights found", lights_count)
    if outlets_count > 0:
        _LOGGER.info("%d VeSync outlets found", outlets_count)
    if switches_count > 0:
        _LOGGER.info("%d VeSync switches found", switches_count)
    return devices


class VeSyncDevice(ToggleEntity):
    """Base class for VeSync Device Representations."""

    def __init__(self, device):
        """Initialize the VeSync device."""
        self.device = device

    @property
    def unique_id(self):
        """Return the ID of this device."""
        if isinstance(self.device.sub_device_no, int):
            return f"{self.device.cid}{str(self.device.sub_device_no)}"
        return self.device.cid

    @property
    def name(self):
        """Return the name of the device."""
        return self.device.device_name

    @property
    def is_on(self):
        """Return True if device is on."""
        return self.device.device_status == "on"

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self.device.connection_status == "online"

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.device.turn_off()

    def update(self):
        """Update vesync device."""
        self.device.update()
