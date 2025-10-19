# Battery thresholds per Endpoint type
BATTERY_THRESHOLDS = {
    "EP1": 2500,
    "EP2": 2500,
    "Canary_A": 3600,
}

class Endpoint:
    """Represents a single IoT sensor (Endpoint)."""

    def __init__(self, ep_type, serial_number, hardware_type, version, battery_mA):
        self.ep_type = ep_type               # Endpoint type (EP1, EP2, Canary_A)
        self.serial_number = serial_number   # Unique sensor ID
        self.hardware_type = hardware_type   # Hardware family (e.g., moxa)
        self.version = version               # Firmware version
        self.battery_mA = battery_mA         # Current battery level (mA)

    def battery_threshold(self):
        """Return the battery threshold for this Endpoint type."""
        return BATTERY_THRESHOLDS[self.ep_type]

    def is_battery_low(self):
        """Return True if the battery is below the threshold."""
        return self.battery_mA < self.battery_threshold()

    def dfu_update(self, version_artifact):
        """Simulate a Device Firmware Update (DFU) for the Endpoint."""
        try:
            prefix, ver_with_ext = version_artifact.split("_", 1)
            ver = ver_with_ext.replace(".swu", "")
            self.version = ver
            return True
        except Exception:
            return False
