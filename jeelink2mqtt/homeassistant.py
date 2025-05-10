import re
import unicodedata
from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceConfig:
    name: str
    id: str
    type: str | None = None
    template: str | None = None
    hass_id: str | None = None


class MessageDecoder(ABC):

    @staticmethod
    def extract_id(message: str) -> str:
        """Check if the message can be decoded and return the device id or an empty string."""
        raise NotImplementedError()

    @staticmethod
    def decode_message(message: str) -> dict[str, Any]:
        """Reurn a dict of values extracted from the message. Uses extract_id fot verification."""
        raise NotImplementedError()


def hass_name_to_id(name: str):
    """
    Mimic Home Assistant's entity name to entity ID conversion process.

    Args:
        entity_name (str): The name of the entity (e.g., "Living Room Light")
        domain (str, optional): The domain prefix (e.g., "light", "switch", "sensor")

    Returns:
        str: The entity ID (e.g., "light.living_room_light")
    """

    result = name.lower()
    result = unicodedata.normalize("NFKD", result)
    result = "".join([c for c in result if not unicodedata.combining(c)])
    result = re.sub(r"[^\w\s]", "_", result)  # Replace special chars with underscore
    result = re.sub(r"\s+", "_", result)  # Replace whitespace with underscore
    result = re.sub(r"_+", "_", result)
    result = result.strip("_")

    return result
