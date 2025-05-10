import pytest

from jeelink2mqtt.homeassistant import hass_name_to_id


@pytest.mark.parametrize(
    "entity_name,expected_id",
    [
        ("Living Room Light", "living_room_light"),
        ("Kitchen Humidifier", "kitchen_humidifier"),
        ("Bedroom Lamp (Nightstand)", "bedroom_lamp_nightstand"),
        ("Hall Sensor-1", "hall_sensor_1"),
        ("Bathroom Fan 50%", "bathroom_fan_50"),
        ("Sofía's Thermostat", "sofia_s_thermostat"),
        ("Outside Temperature & Humidity", "outside_temperature_humidity"),
        ("MAX_CPU_TEMP", "max_cpu_temp"),
        ("  Weird  Spacing  Device  ", "weird_spacing_device"),
        ("Special@#$Characters^&*()", "special_characters"),
    ],
)
def test_entity_name_to_id_without_domain(entity_name, expected_id):
    """Test entity name to entity ID conversion without domain."""
    assert hass_name_to_id(entity_name) == expected_id


@pytest.mark.parametrize(
    "entity_name,expected_id",
    [
        # Test edge cases
        ("", ""),
        (" ", "_"),
        ("___", "_"),
        ("a__b__c", "a_b_c"),
        ("Ελληνικά", "ellenika"),
        ("日本語", "ri_ben_yu"),
        ("👍 Emoji Test", "emoji_test"),
    ],
)
def test_entity_name_edge_cases(entity_name, expected_id):
    """Test entity name conversion with edge cases."""
    assert hass_name_to_id(entity_name) == expected_id
