import asyncio
import logging
import sys
import time

import serial_asyncio


class Serial:
    async def main(self):
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url="/dev/ttyUSB0", baudrate=57600
            )
        except IOError:
            log.error("Can not open USB device!")
            exit("No device")

        # wait till jeelink has settled to ensure init sequence will be received
        time.sleep(2)
        log.info("Start receiving...")


if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG")
    fmt = logging.Formatter("%(asctime)s %(levelname)7s: %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(sh)

    try:
        s = Serial()
        asyncio.run(s.main())
    except KeyboardInterrupt:
        time.sleep(2)
        print("Terminated")
