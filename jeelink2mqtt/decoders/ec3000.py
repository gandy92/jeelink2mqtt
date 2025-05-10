import logging
from typing import Any

from jeelink2mqtt.homeassistant import MessageDecoder

logger = logging.getLogger("jeelink2mqtt")


class EC3000(MessageDecoder):
    """
    Class for decoding the EC3000 messages using the ec3kSerial.1 firmware.
    """

    @staticmethod
    def extract_id(message: str) -> str:
        if not message.startswith("OK 22 "):
            return ""
        values = message.split()
        bytes = [int(v) for v in values[2:]]
        if len(bytes) < 2:
            return ""
        if bytes[0] < 0 or bytes[0] > 255 or bytes[1] < 0 or bytes[1] > 255:
            return ""

        return f"{bytes[0]:02X}{bytes[1]:02X}"

    @classmethod
    def decode_message(cls, message: str) -> dict[str, Any]:
        """Reurn a dict of values extracted from the message. Uses extract_id fot verification."""

        # From ec3kSerial.ino/lines 2154 ff:
        # ---------------------------------------------------------------------------------------
        # - crc calc algorithm is unknown, therefore rely on ClockRecoveryLock for each bit
        # - the higher the nocrl counter, more likely it is that an incorrect packet was received
        # - therefore a filter could be used (like: if(nocrl <= 2)...)
        #
        # output format:
        #         01 - static jeenode id 22 (defined in nodemap.local)
        #   0-1   02 - ec3k sender id
        #   2-5   03 - seconds total
        #   6-9   04 - seconds on
        #  10-13  05 - watt hours
        #  14-15  06 - actual consumption (shifted by 10)
        #  16-17  07 - max. consumption (shifted by 10)
        #  18     08 - number of resets
        #  19     09 - bits without ClockRecoveryLock on
        # ---------------------------------------------------------------------------------------

        # note: the ec3kSerial firmware has no working CRC implemented, but rather suggests
        # discarding messages with too many "bits without ClockRecoveryLock on" (values > 2)

        # log.debug(f"EC3000: Decoding message: {message}")
        id = cls.extract_id(message)
        if not id:
            return {}

        values = message.split()

        int_vals = [int(v) for v in values[2:]]
        # print(hexlify(bytes(int_vals)))
        bwrcl = int_vals[19]
        if bwrcl > 2:
            return {}

        return {
            "id": id,
            "seconds_total": (int_vals[2] << 24) + (int_vals[3] << 16) + (int_vals[4] << 8) + int_vals[5],
            "seconds_on": (int_vals[6] << 24) + (int_vals[7] << 16) + (int_vals[8] << 8) + int_vals[9],
            "consumption_total": ((int_vals[10] << 24) + (int_vals[11] << 16) + (int_vals[12] << 8) + int_vals[13])
            / 1000.0,
            "power": ((int_vals[14] << 8) + int_vals[15]) / 10.0,
            "power_max": ((int_vals[16] << 8) + int_vals[17]) / 10.0,
            "resets": int_vals[18],
        }
