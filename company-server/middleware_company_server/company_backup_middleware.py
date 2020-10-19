import socket
import logging
import json


class CompanyBackupMiddleware:
    HEALTH_CHECK_REQUEST_TYPE = 'HEALTH_CHECK_REQUEST_TYPE'
    HEALTH_CHECK_RESPONSE = json.dumps({
        "status": "OK"
    })

    def __init__(self, port: int, listen_backlog: int):
        logging.info("initializing backup middleware.")
        self._backup_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._backup_requests_socket.bind(('', port))
        self._backup_requests_socket.listen(listen_backlog)
        self._handle_backup_requests()

    def _wait_for_backup_request(self, connection):
        try:
            external_request = connection.recv(1024).rstrip()
            logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                               external_request))
            return external_request.decode('utf-8')
        except OSError:
            logging.error("Error reading socket {}".format(connection))
            connection.send('There was an error reading the socket'.encode('utf-8'))

    def _process_backup_request(self, connection, backup_request):
        backup_request = json.loads(backup_request)
        if backup_request['type'] == self.HEALTH_CHECK_REQUEST_TYPE:
            logging.info("Answering health check request.")
            connection.sendall(bytes(self.HEALTH_CHECK_RESPONSE, encoding='utf-8'))
        else:
            pass

    def _handle_backup_requests(self):
        logging.info("Proceed to receive backup request.")
        connection, address = self._backup_requests_socket.accept()
        logging.info("Address: {}".format(address))
        backup_request = self._wait_for_backup_request(connection)
        self._process_backup_request(connection, backup_request)
