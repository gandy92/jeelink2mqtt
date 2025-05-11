import argparse
import asyncio
import configparser
import logging
import sys
import time

import paho
import paho.mqtt
import paho.mqtt.client

from jeelink2mqtt.homeassistant import DeviceConfig
from jeelink2mqtt.jeelink_handler import Jeelink
from jeelink2mqtt.mqtt_handler import MqttHandler
from jeelink2mqtt.mqtt_handler import get_hostname

logger = logging.getLogger("jeelink2mqtt")


def main():
    # cli arguments
    parser = argparse.ArgumentParser(
        prog="Jeelink2MQTT",
        description="Connects to LaCrosse sensors via Jeelink and publishes received information to MQTT",
    )
    parser.add_argument(
        "-j",
        "--jeelink",
        help="Serial port address of the connected JeeLink, default: /dev/ttyUSB0",
        metavar="serial_address",
        default="/dev/ttyUSB0",
        dest="jeelink_address",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        help="Path to the config ini file, default: config.ini",
        metavar="config_file",
        default="config.ini",
        dest="config_file",
    )
    parser.add_argument(
        "--mqtt",
        help="Hostname of MQTT, default: localhost",
        metavar="host",
        default="localhost",
        dest="mqtt_host",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Print out debug messages",
        action="store_true",
        default=False,
        dest="debug",
    )
    args = parser.parse_args()

    # logging
    logger.setLevel("DEBUG" if args.debug else "INFO")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)7s: %(message)s"))
    logger.addHandler(sh)

    # config file
    config = configparser.ConfigParser()
    config.read(args.config_file)

    devices: list[DeviceConfig] = []
    for device_name in config.sections():
        if "id" not in config[device_name]:
            continue
        params = dict(config[device_name].items())
        try:
            device = DeviceConfig(name=device_name, **params)
            logger.info(f"Registering {device}")
            devices.append(device)
        except Exception as e:
            logger.exception(e)

    # mqtt
    mqtt = paho.mqtt.client.Client(
        paho.mqtt.enums.CallbackAPIVersion.VERSION2, client_id=f"jeelink2mqtt-at-{get_hostname()}"
    )
    handler = MqttHandler(mqtt, devices, "templates")

    mqtt.connect(args.mqtt_host, 1883, 60)
    mqtt.loop_start()

    while not mqtt.is_connected():
        logger.debug("MQTT: Waiting for connection")
        time.sleep(1)

    # event loop
    try:
        s = Jeelink(args.jeelink_address, handler, devices)
        while True:
            try:
                asyncio.run(s.main())
            except OSError:
                logger.error("JeeLink not ready - will retry in two seconds...")
                time.sleep(2)
    except KeyboardInterrupt:
        mqtt.loop_stop()
        mqtt.disconnect()
        logger.info("Terminated.")


if __name__ == "__main__":
    main()
