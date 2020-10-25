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

UNNECESSARY_BACKUP_RESPONSE = {
    "status": "OK",
    "transfer": False
}

START_TRANSFER_RESPONSE = {
    "status": "OK",
    "transfer": True
}
