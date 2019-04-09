"""
Support support for the Virgin Media Hub. 

Currently supports reading downstream values
"""
import logging
from datetime import datetime, timedelta
from xml.dom import minidom

import requests

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
_RESOURCE = '192.168.100.1'

CONF_IP = 'ip_addr'
CONF_POSTRS_THRESHOLD = "postrs_threshold"
CONF_RXMER_THRESHOLD = "rxmer_threshold"

SCAN_INTERVAL = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_IP, default=_RESOURCE): cv.string,
    vol.Optional(CONF_POSTRS_THRESHOLD, default=10000): cv.positive_int,
    vol.Optional(CONF_RXMER_THRESHOLD, default=30): cv.positive_int
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Dublin public transport sensor."""
    ip_addr = config.get(CONF_IP)
    postrs_threshold = config.get(CONF_POSTRS_THRESHOLD)
    rxmer_threshold = config.get(CONF_RXMER_THRESHOLD)

    data = VirginMediaHubData(ip_addr)
    add_entities([VirginMediaHubSensor(data, ip_addr, postrs_threshold, rxmer_threshold)], True)


class VirginMediaHubSensor(Entity):
    """Implementation of a virgin media hub sensor."""

    def __init__(self, data, ip_addr, postrs_threshold, rxmer_threshold):
        """Initialize the sensor."""
        self.data = data
        self._ip_addr = ip_addr
        self._postrs_threshold = postrs_threshold
        self._rxmer_threshold = rxmer_threshold
        self._name = f"Hub DS {self._ip_addr}"
        self._state = None
        self._downstream = None

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
        if self._downstream is not None:
            for ds in self._downstream:
                chid = ds.get("chid", 0)
                attrs["{}_freq".format(chid)] = ds.get("freq", 0)
                attrs["{}_postrs".format(chid)] = ds.get("PostRs", 0)
                attrs["{}_rxmer".format(chid)] = ds.get("RxMER", 0)

        return attrs

    def update(self):
        """Get the latest data and update the states."""
        self.data.update()
        self._downstream = self.data.downstream
        if self._downstream:
            self._state = "OK"
        else:
            self._state = "NC"
        for ds in self._downstream:
            if ds["RxMER"] < self._rxmer_threshold:
                self._state = "BRX"
                break
            elif ds["PostRs"] > self._postrs_threshold:
                self._state = "PRS"


class VirginMediaHubData:
    """The Class for handling the data retrieval."""

    def __init__(self, ip_addr):
        """Initialize the data object."""
        self._url = f"http://{ip_addr}"
        self.downstream = None

    def update(self):
        """Get the latest data"""

        r1 = requests.get(self._url)
        if r1.status_code != 200:
            self.downstream = None
            return

        data = {"token": r1.cookies.get_dict()["sessionToken"], "fun": 10}
        r2 = requests.post(f'{self._url}/xml/getter.xml', data=data, cookies=r1.cookies)

        if r2.status_code != 200:
            self.downstream = None
            return

        parsed_xml = minidom.parseString(r2.text)
        self.downstream = []
        for obj in parsed_xml.getElementsByTagName("downstream_table"):
            for ds in obj.getElementsByTagName("downstream"):
                parsed_object = {}
                parsed_object["freq"] = int(ds.getElementsByTagName("freq")[0].firstChild.nodeValue)
                parsed_object["chid"] = int(ds.getElementsByTagName("chid")[0].firstChild.nodeValue)
                parsed_object["PostRs"] = int(ds.getElementsByTagName("PostRs")[0].firstChild.nodeValue)
                parsed_object["RxMER"] = float(ds.getElementsByTagName("RxMER")[0].firstChild.nodeValue)
                self.downstream.append(parsed_object)

