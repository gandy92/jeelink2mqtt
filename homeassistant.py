import logging
import json
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
        # FIXME separate all 4 sensor values into each a single discovery topic, see https://www.home-assistant.io/integrations/mqtt/#sensors
        # FIXME not sure if "identifiers" is set right
        payloads = [
            # temperature
            {
                "device": {
                    "identifiers": f"{self.name.lower()}_device",
                    "name": self.name,
                },
                "unique_id": f"{self.name.lower()}_temp",
                "device_class": "temperature",
                "unit_of_measurement": "°C",
                "value_template": "{{ value_json.temperature}}",
                "state_topic": TOPIC_HASS_STATE.format(
                    component=self.name.lower(), id=self.id
                ),
            },
            # humidity
            {
                "device": {
                    "identifiers": f"{self.name.lower()}_device",
                    "name": self.name,
                },
                "unique_id": f"{self.name.lower()}_humi",
                "device_class": "humidity",
                "unit_of_measurement": "%",
                "value_template": "{{ value_json.humidity}}",
                "state_topic": TOPIC_HASS_STATE.format(
                    component=self.name.lower(), id=self.id
                ),
            },
        ]
        # FIXME remove
        print(json.dumps(payloads[0]))
        print(json.dumps(payloads[1]))

        for payload in payloads:
            self.mqtt.publish(
                TOPIC_HASS_DISCOVERY.format(component=self.name.lower(), id=self.id),
                json.dumps(payload),
                retain=True,
            )

    def publish_hass_change(self):
        # self.mqtt.publish("/test", self.id)
        pass
