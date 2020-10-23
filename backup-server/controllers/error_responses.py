import json

NON_EXISTENT_NODE_IN_NETWORK_RESPONSE = bytes(json.dumps({
    "status": "error",
    "cause": "The address of the node is invalid."
}), encoding='utf-8')

ERROR_TRYING_TO_CONNECT_RESPONSE = bytes(json.dumps({
    "status": "error",
    "cause": "An error happened when connecting to given node."
}), encoding='utf-8')

UNKNOWN_ERROR_RESPONSE = bytes(json.dumps({
    "status": "error",
    "cause": "An unknown error occurred."
}), encoding='utf-8')
