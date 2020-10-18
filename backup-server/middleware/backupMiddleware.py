import socket

class BackupMiddleware:
    def __init__(self, port: int, listen_backlog: int):
        self._external_requets_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requets_socket.bind(('', port))
        self._external_requets_socket.listen(listen_backlog)

