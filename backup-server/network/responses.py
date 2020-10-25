import json

BYTES_AMOUNT_RESPONSE = 1024

OK_RESPONSE = {
    "status": "ok"
}

OS_ERROR_RESPONSE = {
    "status": "error",
    "cause": "OS error when reading from socket."
}

UNKNOWN_ERROR_RESPONSE = {
    "status": "error",
    "cause": "An unknown error occurred."
}
