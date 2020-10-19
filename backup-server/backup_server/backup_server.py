import socket
import logging
import json

from middleware_backup_server.backup_middleware import BackupMiddleware

class BackupServer:
    def __init__(self, port: int, listen_backlog: int):
        self._backup_middleware = BackupMiddleware(port, listen_backlog)

    def run(self):
        while True:
            external_request = self._backup_middleware.get_external_request()




