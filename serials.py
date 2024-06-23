import asyncio
import time

import serial_asyncio

from lacrosse import LaCrosse
from sensors import Sensor


class Serial:
    def __init__(self, jeelink_address, mqtt, log, sensors):
        self.jeelink_address = jeelink_address
        self.mqtt = mqtt
        self.log = log
        self.sensors = sensors

    async def main(self):
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.jeelink_address, baudrate=57600
            )
        except IOError:
            self.log.error("Can not open USB device!")
            exit("No device")

        # wait till jeelink has settled to ensure init sequence will be received
        time.sleep(2)
        self.log.info("Start receiving...")
        await asyncio.gather(self.receive())

    async def receive(self):
        while True:
            msg = await self.reader.readuntil(b"\n")
            msg = LaCrosse.decodeMessage(msg, self.log)
            if msg is not None:
                if msg["id"] not in self.sensors:
                    self.sensors[msg["id"]] = Sensor(self.mqtt, msg["id"], self.log)
                self.sensors[msg["id"]].update(msg)
