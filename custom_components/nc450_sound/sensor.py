"""
Support support for the TP Link NC450 Sound Detection. 

"""
import logging
from datetime import datetime, timedelta

import requests
import base64

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME, CONF_PASSWORD
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=None): cv.string,
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Dublin public transport sensor."""
    name = config.get(CONF_NAME)
    ip_addr = config.get(CONF_IP_ADDRESS)
    password = config.get(CONF_PASSWORD)

    data = TpLinkNC450SoundData(name, ip_addr, password)
    add_entities([TpLinkNC450SoundSensor(data, name)], True)


class TpLinkNC450SoundSensor(Entity):
    """Implementation of a TpLink NC450 Sound sensor."""

    def __init__(self, data, name):
        """Initialize the sensor."""
        self.data = data
        self._name = name
        self._state = 0

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        attrs["sound"] = self.data.sound
        attrs["sound"] = "true" if self.data.sound_data else "false"

        return attrs

    def update(self):
        """Get the latest data and update the states."""
        self.data.update()
        self._state = self.data.sound

    @property
    def device_class(self):
        return "signal_strength"


class TpLinkNC450SoundData:
    """The Class for handling the data retrieval."""

    def __init__(self, name, ip_addr, password):
        """Initialize the data object."""
        self._base_url = f"http://{ip_addr}"
        self._password = password
        self.sound = 0
        self.sound_data = None
        self._session = None
        self._login_data = None

    def update(self):
        """Get the latest data"""

        try:
            pw = base64.standard_b64encode(self._password.encode())
            payload = {
                "Username": "admin",
                "Password": pw
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
            }

            if self._session is None:
                self._session = requests.Session()

            if self._login_data is None:
                response = self._session.post(f'{self._base_url}/login.fcgi', headers=headers, data=payload, timeout=2)
                self._login_data = response.json()

            if 'token' in self._login_data:
                response = self._session.get(f'{self._base_url}/GetADData.fcgi', timeout=2)
                self.sound_data = response.json()

                self.sound = self.sound_data.get('adSounddata', 0)
                _LOGGER.debug(f"sound data {self.sound_data}")
        except:
            self.sound = 0
            self.sound_data = None
            self._session = None
            self._login_data = None
