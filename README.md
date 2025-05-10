# Jeelink2MQTT

Reads from a [Jeelink](https://www.digitalsmarties.net/products/jeelink) (currently only the 868 MHz variant is tested) to resolve LaCrosse sensor values (e.g. [Technoline TX 29 DTH-IT](https://www.amazon.com/dp/B00392XX5U)). The values are then published to MQTT, mainly in a format to use it with [Home Assistant](https://www.home-assistant.io/).

## Config file

The config file defines the sensors that shall be published to MQTT.

```
; config.ini
[Kitchen]
id=14
type=LaCrosee

[Living Room]
id=36
type=LaCrosee

[Power Fridge]
id=ABCD
type=EC3000

[Power Washingmachine]
ID=DCBA
tpye=EC3000
hass_id=power_washer
template=special_wm_template
```

## Discovery Templates

Each sensor defined in the config.ini file can be associated with a discovery template. Either, the template name is specified in the sensor definition. If that is not the case, a template named after the sensor type is used.

Templates contain the json structure published to the discovery topic `homeassistant/device/+/config` where "+" is replaced by the sensor type and ID, e.g. "EC3000_ABCD". Before publishing, variables in the template are replaced with sensor specifc values:
* `type`: The sensor type, e.g. "EC3000" or "LaCrosse"
* `id`: The sensor id, e.g. "ABCD" (EC3000) or "78" (LaCrosse)
* `name`: The device name, e.g. "Power Kühlschrank"
* `hass_id`: Optional base for entity id's, e.g. "power_kuhlschrank"
* `state_topic`: Topic for the sensor data, excluding RSSI reasing, e.g. "EC3000_ABCD/state"
* `rssi_topic`: Topic for the rssi reading, may include the base station id, e.g. "EC3000_ABCD/rssi" or "EC3000_ABCD/rssi_at_laantena"
* `rssi_name`: Name for the RSSI entity, e.g. "RSSI at laantena"
* `rssi_id`: Is to rssi_name what `hass_id` is to `name`, e.g. "rssi_at_laantena"
* `version`: The jeelink2mqtt version

In case the hass_id is not specified, it will be constructed from the sensor name similar to how home assistant does.

By omitting the frameid (aka device id) in the entity ids, replacing broken hardware boils down to replacing the ID in the config.ini
while keeping the complete Home Assistant configuration intact.

# Supported protocols / JeeLink firmware flavours

## LaCrosse

Should be supported as in the original implementation, probably with differences in the entity ids. Untested due to lack of hardware.

## EC3000

The Conrad Electronic EC3000 power meter sockets require a special firmware, ec3kSerial.ino

Drawbacks:
* missing signal strength (RSSI) reading
* no CRC valuation of the received data, see notes in firmware source code (Todo: Add link to firmware)
