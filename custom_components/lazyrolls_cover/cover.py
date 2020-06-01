import logging
import requests
from xml.etree import ElementTree
import voluptuous as vol

from homeassistant.components.cover import (
    CoverDevice, PLATFORM_SCHEMA, SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_STOP, SUPPORT_SET_POSITION)
from homeassistant.const import (
    CONF_IP_ADDRESS, CONF_ID, CONF_CODE, CONF_NAME, CONF_COVERS, CONF_DEVICE, STATE_CLOSED, STATE_OPEN, STATE_UNKNOWN,CONF_FRIENDLY_NAME)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'lazyrolls'

COVER_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Optional(CONF_FRIENDLY_NAME, default=DEFAULT_NAME): cv.string,
})

pos = '/set?pos='
blindDown = 'http://{}:80'+ pos+'{}'
blindUp = 'http://{}:80'+ pos+'{}'
blindStop = 'http://{}:80/stop'
blindStatus = 'http://{}:80/xml'

############

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): vol.Schema({cv.slug: COVER_SCHEMA}),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the LazyRolls covers."""
    covers = []
    devices = config.get(CONF_COVERS)

    for device_id, device_config in devices.items():
        args = {
            CONF_IP_ADDRESS: device_config.get(CONF_IP_ADDRESS),
            CONF_FRIENDLY_NAME: device_config.get(CONF_FRIENDLY_NAME),
        }

        covers.append(lazyrolls(hass, args))

    add_devices(covers, True)


class lazyrolls(CoverDevice):
    """Representation of LazyRolls cover."""

    # pylint: disable=no-self-use
    def __init__(self, hass, args):
        """Initialize the cover."""
        self.hass = hass
        self._name = args[CONF_FRIENDLY_NAME]
        self._ip_addr = args[CONF_IP_ADDRESS]
        self._available = True
        self._state = None
        self._pos = 100
        self.update()

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    ################

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position == 0
    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._name

    @property
    def device_info(self):
        """Return the device info."""
        return {"name": self._name, "identifiers": {(DOMAIN, self._unique_id)}, "model":"LazyRolls", "manufacturer":"LazyRolls"}

    def update(self):
        response = requests.get(blindStatus.format(self._ip_addr))
        root = ElementTree.fromstring(response.content)
        p_now = int(root.find("Position/Now").text)
        p_dst = int(root.find("Position/Dest").text)
        p_max = int(root.find("Position/Max").text)
        if (p_max == 0): p_max = 100;
        percent = round(p_now * 100 / p_max)
        self._pos = 100 - percent
        nVal = 2
        if (p_now <= 0): nVal = 0
        if (p_now >= p_max): nVal = 1
        _LOGGER.debug("in update Status: " + self._name + " : " + self._ip_addr + " - " + str(response.status_code)+" "+ response.text)

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._pos

    def close_cover(self):
        """Close the cover."""
        requests.get(blindDown.format(self._ip_addr, "100")) #0
        self.update()

    def open_cover(self):
        """Open the cover."""
        requests.get(blindUp.format(self._ip_addr, "0")) #100
        self.update()

    def stop_cover(self):
        """Stop the cover."""
        requests.get(blindStop.format(self._ip_addr))
        self.update()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        requests.get(blindUp.format(self._ip_addr, str(kwargs['position'])))
        _LOGGER.debug("Writing Set position to " + self._name + " : " + self._ip_addr + " - " + str(kwargs['position']) + " was succesfull!")
        self.update()

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return 'window'

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP | SUPPORT_SET_POSITION
