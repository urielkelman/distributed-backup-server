import socket
import logging

from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class QueryBackupsController:
    def __init__(self, port, listen_backlog, backups):
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._backups = backups

    def listen_to_queries(self):
        while True:
            connection, address = self._external_requests_socket.accept()
            query_request = JsonReceiver.receive_json(connection)
            if query_request['type'] == 'query':
                logging.info("Answering query controller correctly.")
                JsonSender.send_json(connection, self._backups.copy())
            else:
                logging.info("Answering query controller with error message.")
                JsonSender.send_json(connection, {'status': 'ERROR'})
