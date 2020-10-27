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

PATH_NOT_FOUND_RESPONSE = {
    "status": "ERROR",
    "cause": "Invalid path."
}


def unnecessary_backup_response(id):
    return {
        "status": "OK",
        "transfer": False,
        "id": id
    }


def start_transfer_response(id):
    return {
        "status": "OK",
        "transfer": True,
        "id": id
    }
