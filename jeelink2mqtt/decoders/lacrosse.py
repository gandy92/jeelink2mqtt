import logging
from typing import Any

from jeelink2mqtt.homeassistant import MessageDecoder

logger = logging.getLogger("jeelink2mqtt")


class LaCrosse(MessageDecoder):
    """
    Class for decoding the LaCrosse messages.
    Protocol: http://fredboboss.free.fr/articles/tx29.php
    """

    @staticmethod
    def extract_id(message: str) -> str:
        if not message.startswith("OK 9 "):
            return ""
        values = message.split()
        bytes = [int(v) for v in values[2:]]
        if len(bytes) < 1:
            return ""
        if bytes[0] < 0 or bytes[0] > 255:
            return ""

        return f"{bytes[0]:d}"

    @classmethod
    def decode_message(cls, message: str) -> dict[str, Any]:
        """Reurn a dict of values extracted from the message. Uses extract_id fot verification."""

        # log.debug(f"LaCrosse: Decoding message: {message}")
        values = message.split()

        try:
            id = int(values[2])
            batteryNew = int(values[3]) >> 7
            # type = int(values[3]) & 0x7F
            temperature = int(values[4]) * 256 + int(values[5])
            temperature = (float(temperature) - 1000) / 10
            batteryWeak = int(values[6]) >> 7
            humidity = int(values[6]) & 0x7F
        except Exception as err:
            logger.debug(f"LaCrosse: Illegal message received {message}, {err}")
            return

        # log.debug(
        #     f"LaCrosse: Sensor reporting: ID {id}, Temperature {temperature}, Humidity {humidity}, Battery new {batteryNew}, Battery weak {batteryWeak}"
        # )

        return {
            "id": id,
            "batteryNew": batteryNew,
            "batteryWeak": batteryWeak,
            "temperature": temperature,
            "humidity": humidity,
            "battery": 20 if batteryWeak else 100,
        }
