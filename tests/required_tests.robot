*** Settings ***
Library    Collections

*** Test Cases ***

OTA Happy Flow
    # Init node to version 33, upload 34 to its OTA channel, retry apply, expect 34
    ${node}=    Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_node_by_uuid("MOXA_TBCDB1045001")
    ${ch}=      Set Variable    ${node["ota_channel"]}
    ${_}=       Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_set_node_version("MOXA_TBCDB1045001","33")
    ${ok}=      Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_post_version_to_ota_channel("${ch}","moxa_34.swu")
    Should Be Equal As Integers    ${ok}    200

    FOR    ${i}    IN RANGE    0    5
    ${_}=    Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_apply_node_ota_once("MOXA_TBCDB1045001")
    ${ver}=  Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_node_version("MOXA_TBCDB1045001")
    Run Keyword If    '${ver}'=='34'    Exit For Loop
    END
    Should Be Equal    ${ver}    34

Endpoint DFU With Backlog
    # EP has backlog>0 -> defer; when backlog=0 -> update; low battery -> defer again
    ${n}=         Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_node_by_uuid("AHN2_ABCDEF000001")
    ${ep}=        Set Variable    ${n["Endpoints"][0]}
    ${_}=         Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_set_endpoint_backlog("${ep}",3)
    ${code}=      Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_post_dfu_to_endpoint("${ep}","ahn2_11.swu")
    Should Be Equal As Integers    ${code}    202

    ${_}=         Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_set_endpoint_backlog("${ep}",0)
    ${code2}=     Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_try_apply_pending_dfu("${ep}")
    Should Be Equal As Integers    ${code2}   200

    ${v}=         Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_endpoint_version("${ep}")
    Should Be Equal    ${v}    11

    ${_}=         Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_set_endpoint_battery("${ep}",2000)
    ${code3}=     Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_post_dfu_to_endpoint("${ep}","ahn2_12.swu")
    Should Be Equal As Integers    ${code3}   202

Bad Firmware OTA
    ${_}=       Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_set_node_version("MOXA_TBCDB1045001","33")
    ${node}=    Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_node_by_uuid("MOXA_TBCDB1045001")
    ${ch}=      Set Variable    ${node["ota_channel"]}
    ${status}=  Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_post_version_to_ota_channel("${ch}","cassia_99.swu")
    Should Be Equal As Integers    ${status}    400
    ${ver}=     Evaluate    __import__("iot.Augury_api", fromlist=["*"]).api_get_node_version("MOXA_TBCDB1045001")
    Should Be Equal    ${ver}    33

