import json
import logging
import socket

import expandvars
import paho.mqtt.client
import psutil

from jeelink2mqtt.homeassistant import DeviceConfig
from jeelink2mqtt.homeassistant import hass_name_to_id

logger = logging.getLogger("jeelink2mqtt")

HASS_DISCOVERY_BASE = "homeassistant"
HASS_BIRTH_TOPIC = "homeassistant/status"
HASS_BIRTH_MESSAGE = "online"
DEFAULT_TOPIC_TMPL = "{device_name}/{topic}"  # "{prefix}/{device_name}/{topic}"


def get_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipv4_address = s.getsockname()[0]
    s.close()
    return ipv4_address


def get_ifname(ipv4_address: str) -> str:
    nics = psutil.net_if_addrs()
    ifname = [i for i in nics for j in nics[i] if j.address == ipv4_address and j.family == socket.AF_INET][0]
    return ifname


def get_mac(ifname: str) -> str:
    nics = psutil.net_if_addrs()
    mac = ([j.address for i in nics for j in nics[i] if i == ifname and j.family == psutil.AF_LINK])[0]
    return mac.replace("-", ":")


def get_hostname() -> str:
    return socket.gethostname()


class MqttHandler:
    def __init__(self, mqtt: paho.mqtt.client.Client, devices: list[DeviceConfig], template_path: str):
        self.mqtt = mqtt
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_log = self.on_log
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt._on_message = self.on_message
        self.devices: list[DeviceConfig] = devices
        self.template_path: str = template_path
        self.templates: dict[str, str] = {}
        self.dev_topic_name_tmpl = "{device.type}_{device.id}"
        self.topic_template = DEFAULT_TOPIC_TMPL
        self.whitelist: dict[str, DeviceConfig] = {self._device_topic_name(dev): dev for dev in devices}

    def get_device_config(self, type: str, id: str) -> DeviceConfig | None:
        key = self._device_topic_name(DeviceConfig("", id, type))
        return self.whitelist.get(key, None)

    def _topic(self, prefix: str, device_name: str, topic: str) -> str:
        return self.topic_template.format(prefix=prefix, device_name=device_name, topic=topic)

    def get_template(self, device: DeviceConfig):
        template = device.template or device.type
        if template not in self.templates:
            try:
                filepath = f"{self.template_path}/{template}.json"
                with open(filepath) as f:
                    tmpl = f.read()
                _ = json.loads(tmpl)
                self.templates[template] = tmpl
            except FileNotFoundError:
                logger.error(f"Could not find template at {filepath}")
                self.templates[template] = None
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Could not load template from {filepath}: {e}")
                logger.exception(e)
                self.templates[template] = None
                return None

        return self.templates.get(template, None)

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        if reason_code == 0:
            logger.info("MQTT: Connected successfully to the MQTT broker")
        else:
            logger.error(f"MQTT: Failed to connect with code {reason_code}")
        s = self.mqtt.socket()
        address = s.getsockname()[0]
        self.mac = get_mac(get_ifname(address))
        self.hostname = get_hostname()

        logger.debug(f"{self.hostname=} {address=} {self.mac=}")
        client.subscribe(HASS_BIRTH_TOPIC)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        logger.info("MQTT: Disconnected from the MQTT broker")

    def on_message(self, client, userdata, msg: paho.mqtt.client.MQTTMessage):
        logger.debug(f"Received message on topic={msg.topic} -> {msg.payload}")

        if msg.topic == HASS_BIRTH_TOPIC and msg.payload.decode() == HASS_BIRTH_MESSAGE:
            self.publish_full_discovery()

    def publish_full_discovery(self):
        logger.debug("Will start to publish discovery messages for %d devices" % len(self.devices))
        for device in self.devices:
            self.publish_device_discovery(device)

    def _device_topic_name(self, device: DeviceConfig) -> str:
        return self.dev_topic_name_tmpl.format(device=device)

    def _device_params(self, device: DeviceConfig) -> dict[str, str]:
        dev_topic_name = self._device_topic_name(device)
        state_topic = self._topic("tele", dev_topic_name, "SENSOR")
        rssi_name = f"Signal Strength at {self.hostname}"
        rssi_id = hass_name_to_id(rssi_name)
        rssi_topic = self._topic("tele", dev_topic_name, f"RSSI_{self.hostname}")
        from jeelink2mqtt import __version__ as version

        return {
            "version": version,
            "type": device.type,  # The sensor type, e.g. "EC3000" or "LaCrosse"
            "id": device.id,  # The sensor id, e.g. "ABCD" (EC3000) or "78" (LaCrosse)
            "name": device.name,  # The device name, e.g. "Power Kühlschrank"
            "hass_id": device.hass_id or hass_name_to_id(device.name),
            "state_topic": state_topic,  # Topic for the sensor data, excluding RSSI reasing, e.g. "EC3000_ABCD/STATE"
            "rssi_topic": rssi_topic,  # Topic for the rssi reading, may include the base station id, e.g. "EC3000_ABCD/RSSI" or "EC3000_ABCD/RSSI_AT_LAANTENA"
            "rssi_name": rssi_name,
            "rssi_id": rssi_id,
        }

    def publish_device_discovery(self, device: DeviceConfig):
        if not device.type:
            logger.error("Could not publish a device without type")
            return
        tmpl = self.get_template(device)
        if not tmpl:
            return
        data = expandvars.expand(tmpl, True, self._device_params(device))
        topic = f"{HASS_DISCOVERY_BASE}/device/{device.type}_{device.id.upper()}/config"
        # print(topic)
        # print(data)
        self.mqtt.publish(topic, data)

    def publish_device_data(self, device: DeviceConfig, data: dict) -> None:
        params = self._device_params(device)
        topic = params["state_topic"]
        # print(topic)
        # print(data)
        self.mqtt.publish(topic, json.dumps(data), retain=True)

    def on_log(self, client, userdata, level, buf):
        logger.debug(f"MQTT: Message {buf}")
