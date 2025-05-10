import asyncio
import logging
import time

import serial_asyncio
from serial import SerialException

from jeelink2mqtt.decoders.ec3000 import EC3000
from jeelink2mqtt.decoders.lacrosse import LaCrosse
from jeelink2mqtt.homeassistant import DeviceConfig
from jeelink2mqtt.homeassistant import MessageDecoder
from jeelink2mqtt.mqtt_handler import MqttHandler

logger = logging.getLogger("jeelink2mqtt")

decoders = {
    "OK 9 ": LaCrosse,
    "OK 22 ": EC3000,
}


def get_message_decoder(msg: str) -> MessageDecoder:
    for key, decoder in decoders.items():
        if msg.startswith(key):
            return decoder
    # log.debug(f"LaCrosse: Don't know how to handle message: {msg}")
    return None


class Jeelink:

    def __init__(self, jeelink_device: str, mqtt: MqttHandler, devices: list[DeviceConfig]):
        self.jeelink_address = jeelink_device
        self.mqtt: MqttHandler = mqtt
        self.devices: list[DeviceConfig] = devices
        self.log = logging.getLogger("jeelink2mqtt")

    async def main(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(url=self.jeelink_address, baudrate=57600)

        # wait till jeelink has settled to ensure init sequence will be received
        time.sleep(2)
        self.log.info("Start receiving...")
        await asyncio.gather(self.receive())

    async def receive(self):
        while True:
            try:
                raw_msg = await self.reader.readuntil(b"\n")
                message = raw_msg.decode()
                # print(f"<< {message}")
                decoder = get_message_decoder(msg=message)
                if not decoder:
                    continue
                id = decoder.extract_id(message)
                device = self.mqtt.get_device_config(decoder.__name__, id)
                if device is None:
                    print(f"******  unknown {decoder.__name__} {id}")
                    # Todo: maybe leave some information on unknown devices somewhere
                    continue
                data = decoder.decode_message(message)
                if not data:
                    continue
                logger.debug("Sending data from %s: %s", device, data)
                self.mqtt.publish_device_data(device, data)

            except SerialException:
                raise

            except Exception as e:
                self.log.error("Potentially recoverable error: %s", e)
