import logging
import socket
import json
import traceback

import controllers.responses as responses
from controllers.utils import padd_to_specific_size


class BackupController:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    def __init__(self, port: int, listen_backlog: int):
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._active_external_request_connection = None

    def _wait_for_backup_request(self, connection: socket.socket):
        request_size = int(connection.recv(self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION).decode('utf-8'))
        logging.info("Going to listen for a request that contains {} bytes".format(request_size))
        external_request = connection.recv(request_size)
        logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                           external_request))
        return json.loads(external_request.decode('utf-8'))

    def _accept_new_backup_request(self):
        logging.info("Proceed to receive new external request.")
        connection, address = self._external_requests_socket.accept()
        logging.info("Address: {}".format(address))
        external_request = self._wait_for_backup_request(connection)
        self._active_external_request_connection = connection
        return external_request

    def get_registration_request(self):
        try:
            external_request = self._accept_new_backup_request()
            self._active_external_request_connection.sendall(padd_to_specific_size(str(len(responses.OK_RESPONSE)),
                                                                                   self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
            self._active_external_request_connection.sendall(responses.OK_RESPONSE)
            return external_request

        except OSError:
            logging.error("OS Error ocurred.")
            traceback.print_exc()
            self._active_external_request_connection.sendall(
                padd_to_specific_size(str(len(responses.OS_ERROR_RESPONSE)),
                                      self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
            self._active_external_request_connection.sendall(responses.OS_ERROR_RESPONSE)
        except:
            logging.error("Unexpected error ocurred: ")
            traceback.print_exc()
            self._active_external_request_connection.sendall(
                padd_to_specific_size(str(len(responses.OS_ERROR_RESPONSE)),
                                      self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
            self._active_external_request_connection.sendall(responses.UNKNOWN_ERROR_RESPONSE)

        finally:
            self._active_external_request_connection.close()
            self._active_external_request_connection = None
