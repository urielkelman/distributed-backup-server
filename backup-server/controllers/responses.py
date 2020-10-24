import json

from controllers.utils import padd_to_specific_size

BYTES_AMOUNT_RESPONSE = 1024

OK_RESPONSE = padd_to_specific_size(str({
    "status": "ok"
}), BYTES_AMOUNT_RESPONSE)

OS_ERROR_RESPONSE = padd_to_specific_size(str({
    "status": "error",
    "cause": "OS error when reading from socket."
}), BYTES_AMOUNT_RESPONSE)

UNKNOWN_ERROR_RESPONSE = padd_to_specific_size(str({
    "status": "error",
    "cause": "An unknown error occurred."
}), BYTES_AMOUNT_RESPONSE)
