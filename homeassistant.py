import logging
from paho.mqtt.client import Client

TOPIC_HASS_DISCOVERY = "homeassistant/{component}/{id}/config"
TOPIC_HASS_STATE = "homeassistant/{component}/{id}/state"


class HomeAssistantSensor:
    log = logging.getLogger("jeelink2mqtt")

    def __init__(self, mqtt: Client, id: str, name: str):
        self.mqtt = mqtt
        self.id = id
        self.name = name

    def publish_hass_discovery(self):
        # FIXME add restrain
        # FIXME publish
        print(TOPIC_HASS_DISCOVERY.format(component=self.name.lower(), id=self.id))

    def publish_hass_change(self):
        # self.mqtt.publish("/test", self.id)
        pass
