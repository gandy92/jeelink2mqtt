class Sensor:
    def __init__(self, mqtt, id, log):
        self.mqtt = mqtt
        self.id = id
        self.batteryNew = None
        self.batteryWeak = None
        self.temperature = None
        self.humidity = None
        self.log = log

    def update(self, values):
        self._update("batteryNew", values["batteryNew"])
        self._update("batteryWeak", values["batteryWeak"])
        self._update("temperature", values["temperature"])
        self._update("humidity", values["humidity"])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    def _update(self, prop, value):
        if getattr(self, prop) != value:
            self.log.debug(
                f"Sensor {self.id}\t{prop}\tfrom\t{self.__getattribute__(prop)}\tto\t{value:<4}"
            )
            setattr(self, prop, value)

    def __repr__(self) -> str:
        return f"Sensor(id={self.id}, temperature={self.temperature}, humidity={self.humidity}, batteryWeak={self.batteryWeak}, batteryNew={self.batteryNew})"
