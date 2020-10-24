import json

OS_ERROR_RESPONSE = bytes(json.dumps({
    "status": "error",
    "cause": "OS error when reading from socket."
}), encoding='utf-8')

UNKNOWN_ERROR_RESPONSE = bytes(json.dumps({
    "status": "error",
    "cause": "An unknown error occurred."
}), encoding='utf-8')
