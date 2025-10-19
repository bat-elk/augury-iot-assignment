
from .Node import Node
from .Endpoint import Endpoint

# "Database" in memory
NODES = {}          # key: node uuid -> Node
EP_INDEX = {}       # key: endpoint serial -> Endpoint
OTA_CHANNELS = {}   # key: "OTA_<uuid>" -> list of artifacts
PENDING_DFU = {}    # serial -> pending artifact  

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

###################Helper function################# 
def find_node_by_ota_channel(ota_channel):
    """Find Node object by its OTA_<uuid> channel."""
    for node in NODES.values():
        if node.ota_channel() == ota_channel:
            return node
    return None

###################Functions for the firsr/third test################# 
def api_set_node_version(uuid, version_str):
    """Force-set Node version"""
    node = NODES.get(uuid)
    if not node:
        return 400
    node.version = str(version_str)
    return 200

def api_get_node_version(uuid):
    """Return node current firmware version"""
    node = NODES.get(uuid)
    return node.version if node else ""

def api_apply_node_ota_once(uuid):
    """Pick the LAST artifact in the node's OTA channel that matches
      "<hardware>_*.swu" and try to apply it.
      200 - applied now
      204 - nothing to do / already up to date
      400 - node not found / bad artifact format"""
  
    node = NODES.get(uuid)
    if not node:
        return 400

    ch = node.ota_channel()
    artifacts = OTA_CHANNELS.get(ch) or []

    hw_prefix = node.hardware_type.lower() + "_" # Filter only artifacts for this hardware and '.swu' suffix
    matches = []
    for a in artifacts:
        if a.lower().startswith(hw_prefix) and a.endswith(".swu"):
            matches.append(a)
    if not matches:
        return 204  
    
    artifact = matches[-1] #the last element in the list 

    try:                                           #Extract version string from "<hw>_<version>.swu"
        ver_with_ext = artifact.split("_", 1)[1]   #taking the part after the _ 
        version = ver_with_ext[:-4]                # remove ".swu" -> "34"
        if not version:                            # empty version is invalid
            return 400
    except Exception:
        return 400

    if node.version == version:
        return 204

    ok = node.ota_update(artifact) #update the version of the node
    return 200 if ok else 400


###################Functions for the second test################# 
def api_set_endpoint_backlog(serial, count):
    """set backlog to an Endpoint"""
    ep = EP_INDEX.get(serial)
    if not ep:
        return 400
    ep.backlog = int(count)
    return 200

def api_set_endpoint_battery(serial, mA):
    """Update battery level for Endpoint"""
    ep = EP_INDEX.get(serial)
    if not ep:
        return 400
    ep.battery_mA = int(mA)
    return 200

def api_get_endpoint_version(serial):
    """Return Endpoint version"""
    ep = EP_INDEX.get(serial)
    return ep.version if ep else ""

def api_post_dfu_to_endpoint(serial, version_artifact):
    """Request a DFU for an endpoint.
      - return 202 (Accepted but deferred)
      - If everything is OK -> apply DFU immediately and return 200
      - If the artifact is invalid / wrong hardware prefix / bad suffix -> return 400"""
    ep = EP_INDEX.get(serial)
    if not ep:
        return 400

    try: #valdiation of the input
        prefix, ver_with_ext = version_artifact.split("_", 1)
        if prefix.lower() != ep.hardware_type.lower():
            return 400
        if not ver_with_ext.endswith(".swu"):
            return 400
    except Exception:
        return 400

    if ep.has_backlog() or ep.is_battery_low(): #policy check of the test
        PENDING_DFU[serial] = version_artifact
        return 202 

    return 200 if ep.dfu_update(version_artifact) else 400


def api_try_apply_pending_dfu(serial):
    """Try to apply a previously deferred DFU for the given endpoint"""
    ep = EP_INDEX.get(serial)
    if not ep:
        return 400

    if ep.has_backlog() or ep.is_battery_low(): #check it's still blocked
        return 202

    artifact = PENDING_DFU.get(serial)
    if not artifact:
        return 204  # No pending DFU to apply

    ok = ep.dfu_update(artifact)
    if ok:
        PENDING_DFU.pop(serial, None) #update the PENDING_DFU that we will not use this update again
        return 200

    return 400
