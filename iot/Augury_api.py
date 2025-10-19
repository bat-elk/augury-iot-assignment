
from .Node import Node
from .Endpoint import Endpoint

# "Database" in memory
NODES = {}          # key: node uuid -> Node
EP_INDEX = {}       # key: endpoint serial -> Endpoint
OTA_CHANNELS = {}   # key: "OTA_<uuid>" -> list of artifacts


# Create 3 sample Nodes, each with 3 Endpoints
def register_sample_topology():
    if NODES:  # already initialized
        return

    def make_node(name, hw, uuid, ver):
        node = Node(name, uuid, hw, ver)
        # three endpoints per node
        ep1 = Endpoint("EP1", f"{uuid}_EP1_SN", hw, "10", 3000)
        ep2 = Endpoint("EP2", f"{uuid}_EP2_SN", hw, "10", 2600)
        can = Endpoint("Canary_A", f"{uuid}_CANARY_SN", hw, "10", 3800)
        node.add_endpoint(ep1)
        node.add_endpoint(ep2)
        node.add_endpoint(can)

        # add to global "database"
        EP_INDEX[ep1.serial_number] = ep1
        EP_INDEX[ep2.serial_number] = ep2
        EP_INDEX[can.serial_number] = can
        OTA_CHANNELS[node.ota_channel()] = []
        NODES[uuid] = node
        return node

    make_node("AHN2", "ahn2", "AHN2_ABCDEF000001", "33")
    make_node("Cassia", "cassia", "CASSIA_ABCDEF000002", "33")
    make_node("Moxa", "moxa", "MOXA_TBCDB1045001", "33")


register_sample_topology() #calling this function to create a demo test


# -----------------------------
# API FUNCTIONS
# -----------------------------

def api_get_endpoint_by_serial(serial_number):
    """Return endpoint info by serial."""
    ep = EP_INDEX.get(serial_number)
    if not ep:
        return {}

    # find node that owns this endpoint
    owner_uuid = ""
    for n in NODES.values():
        if n.get_endpoint_by_serial(serial_number):
            owner_uuid = n.uuid
            break

    return {
        "serial_number": ep.serial_number,
        "battery": ep.battery_mA,
        "hardware_type": ep.hardware_type,
        "uuid": owner_uuid,
        "version": ep.version,
    }


def api_get_node_by_uuid(uuid):
    """Return node info."""
    node = NODES.get(uuid)
    if not node:
        return {}

    return {
        "uuid": node.uuid,
        "ota_channel": node.ota_channel(),
        "version": node.version,
        "Endpoints": [ep.serial_number for ep in node.endpoints],
    }


def api_post_version_to_ota_channel(ota_channel, version_artifact):
    """Add version artifact to OTA channel."""
    node = find_node_by_ota_channel(ota_channel)
    if not node:
        return 400

    try:
        prefix, ver_with_ext = version_artifact.split("_", 1)
        if prefix.lower() != node.hardware_type.lower():
            return 400
        if not ver_with_ext.endswith(".swu"):
            return 400
    except Exception:
        return 400

    if ota_channel not in OTA_CHANNELS:
        OTA_CHANNELS[ota_channel] = []
    if version_artifact not in OTA_CHANNELS[ota_channel]:
        OTA_CHANNELS[ota_channel].append(version_artifact)
    return 200


def api_clear_ota_channel(ota_channel, version_artifact):
    """Remove a version artifact from OTA channel."""
    artifacts = OTA_CHANNELS.get(ota_channel)
    if not artifacts:
        return 400
    if version_artifact in artifacts:
        artifacts.remove(version_artifact)
        return 200
    return 400


def find_node_by_ota_channel(ota_channel):
    """Find Node object by its OTA_<uuid> channel."""
    for node in NODES.values():
        if node.ota_channel() == ota_channel:
            return node
    return None
