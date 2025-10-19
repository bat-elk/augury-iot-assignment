from .Endpoint import Endpoint

# Mapping between Node name and its API address
API_ADDRESS_BY_NODE = {
    "AHN2": "buildroot_api.azure",
    "Cassia": "buildroot_api.azure",
    "Moxa": "moxa_api.azure",
}

class Node:
    """Represents a gateway that contains multiple Endpoints."""

    def __init__(self, name, uuid, hardware_type, version):
        self.name = name                       # Node name (AHN2, Cassia, Moxa)
        self.uuid = uuid                       # Unique Node ID
        self.hardware_type = hardware_type     # Hardware family type
        self.version = version                 # Current firmware version
        self.endpoints = []                    # List of Endpoint objects

    def api_address(self):
        """Return the Node's API address."""
        return API_ADDRESS_BY_NODE[self.name]

    def ota_channel(self):
        """Return the OTA channel name."""
        return f"OTA_{self.uuid}"

    def add_endpoint(self, endpoint):
        """Attach an Endpoint to this Node."""
        self.endpoints.append(endpoint)

    def get_endpoint_by_serial(self, serial_number):
        """Find an Endpoint by its serial number."""
        for ep in self.endpoints:
            if ep.serial_number == serial_number:
                return ep
        return None

    def ota_update(self, version_artifact):
        """Simulate an Over-The-Air (OTA) firmware update for the Node."""
        try:
            prefix, ver_with_ext = version_artifact.split("_", 1)
            # Validate that the file matches this hardware type
            if prefix.lower() != self.hardware_type.lower():
                return False
            # Extract version and update Node
            ver = ver_with_ext.replace(".swu", "")
            self.version = ver
            return True
        except Exception:
            return False
