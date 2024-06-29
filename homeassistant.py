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

    def get_unique_id(self) -> str:
        return f"j2m_{self.name.lower()}"

    def get_unique_id_with_type(self, type: str) -> str:
        return f"{self.get_unique_id()}_{type}"

    def publish_hass_discovery(self):
        # the different types are separated into different discovery messages
        shared = {
            "device": {
                "identifiers": f"{self.name.lower()}_device",
                "name": self.name,
            },
            "state_topic": TOPIC_HASS_STATE.format(id=self.get_unique_id()),
        }

        # temperature
        self.mqtt.publish(
            TOPIC_HASS_DISCOVERY.format(id=self.get_unique_id_with_type("temp")),
            json.dumps(
                {
                    "unique_id": self.get_unique_id_with_type("temp"),
                    "device_class": "temperature",
                    "unit_of_measurement": "°C",
                    "value_template": "{{ value_json.temperature }}",
                    **shared,
                }
            ),
            retain=True,
        )

        # humidity
        self.mqtt.publish(
            TOPIC_HASS_DISCOVERY.format(id=self.get_unique_id_with_type("humi")),
            json.dumps(
                {
                    "unique_id": self.get_unique_id_with_type("humi"),
                    "device_class": "humidity",
                    "unit_of_measurement": "%",
                    "value_template": "{{ value_json.humidity }}",
                    **shared,
                },
            ),
            retain=True,
        )

        # battery
        self.mqtt.publish(
            TOPIC_HASS_DISCOVERY.format(id=self.get_unique_id_with_type("batt")),
            json.dumps(
                {
                    "unique_id": self.get_unique_id_with_type("batt"),
                    "device_class": "battery",
                    "value_template": "{{ value_json.battery }}",
                    **shared,
                },
            ),
            retain=True,
        )

    def publish_hass_change(self):
        self.mqtt.publish(
            TOPIC_HASS_STATE.format(id=self.get_unique_id()),
            json.dumps(
                {
                    "temperature": self.temperature,
                    "humidity": self.humidity,
                    "battery": 20 if self.batteryWeak else 100,
                }
            ),
            retain=False,
        )
