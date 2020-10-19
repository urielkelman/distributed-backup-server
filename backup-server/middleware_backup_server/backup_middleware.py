import socket
import logging
import json

from middleware_backup_server.external_request_integrity_checker import ExternalRequestIntegrityChecker


class BackupMiddleware:
    NON_EXISTENT_NODE_IN_NETWORK_RESPONSE = {
        "status": "error",
        "cause": "The address of the node is invalid."
    }

    ERROR_TRYING_TO_CONNECT_RESPONSE = {
        "status": "error",
        "cause": "An error happened when connecting to given node."
    }


    def __init__(self, port: int, listen_backlog: int):
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._active_external_request_connection = None

    def _wait_for_external_request(self, connection: socket.socket):
        try:
            external_request = connection.recv(1024).rstrip()
            logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                               external_request))
            return external_request.decode('utf-8')
        except OSError:
            logging.error("Error reading socket {}".format(connection))
            connection.send('There was an error reading the socket'.encode('utf-8'))

    def _accept_new_backup_request(self):
        logging.info("Proceed to receive new external request.")
        connection, address = self._external_requests_socket.accept()
        logging.info("Address: {}".format(address))
        external_request = self._wait_for_external_request(connection)
        return external_request, connection

    def get_external_request(self):
        external_request, connection = self._accept_new_backup_request()
        self._active_external_request_connection = connection
        try:
            ExternalRequestIntegrityChecker.check_request_integrity(external_request)
        except TimeoutError:
            connection.sendall(bytes(json.dumps(self.NON_EXISTENT_NODE_IN_NETWORK_RESPONSE), encoding='utf-8'))
        except OSError:
            logging.error("Error ocurred: {}".format(OSError))
            connection.sendall(bytes(json.dumps(self.ERROR_TRYING_TO_CONNECT_RESPONSE), encoding='utf-8'))

        return external_request

    def reply_to_external_request_successfully(self):
        self._active_external_request_connection.send("Your request has been processed successfully".encode('utf-8'))
        self._active_external_request_connection.close()
        self._active_external_request_connection = None
