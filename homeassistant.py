import logging
import json
from paho.mqtt.client import Client

TOPIC_HASS_DISCOVERY = "homeassistant/sensor/{id}/config"
TOPIC_HASS_STATE = "homeassistant/sensor/{id}/state"


class HomeAssistantSensor:
    log = logging.getLogger("jeelink2mqtt")

    def __init__(self, mqtt: Client, id: str, name: str):
        self.mqtt = mqtt
        self.id = id
        self.name = name

    def publish_hass_discovery(self):
        # FIXME separate all 4 sensor values into each a single discovery topic, see https://www.home-assistant.io/integrations/mqtt/#sensors
        shared = {
            "device": {
                "identifiers": f"{self.name.lower()}_device",
                "name": self.name,
            },
            "state_topic": TOPIC_HASS_STATE.format(id=self.id),
        }

        # temperature
        self.mqtt.publish(
            TOPIC_HASS_DISCOVERY.format(id=f"{self.id}_temp"),
            json.dumps(
                {
                    "unique_id": f"{self.name.lower()}_temp",
                    "device_class": "temperature",
                    "unit_of_measurement": "°C",
                    "value_template": "{{ value_json.temperature}}",
                    **shared,
                }
            ),
            retain=True,
        )

        # humidity
        self.mqtt.publish(
            TOPIC_HASS_DISCOVERY.format(id=f"{self.id}_humi"),
            json.dumps(
                {
                    "unique_id": f"{self.name.lower()}_humi",
                    "device_class": "humidity",
                    "unit_of_measurement": "%",
                    "value_template": "{{ value_json.humidity}}",
                    **shared,
                },
            ),
            retain=True,
        )

    # FIXME implement
    def publish_hass_change(self):
        # self.mqtt.publish("/test", self.id)
        pass
