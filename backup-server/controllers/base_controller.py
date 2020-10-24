import logging
import socket
import json
import traceback

import controllers.responses as responses


class BaseRegistrationController:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    def __init__(self, port: int, listen_backlog: int):
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._active_external_request_connection = None

    def _wait_for_registration_request(self, connection: socket.socket):
        request_size = int(connection.recv(self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION).decode('utf'))
        logging.info("Going to listen for a request that contains {} bytes".format(request_size))
        external_request = connection.recv(request_size)
        logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                           external_request))
        return json.loads(external_request.decode('utf-8'))

    def _accept_new_registration_request(self):
        logging.info("Proceed to receive new external request.")
        connection, address = self._external_requests_socket.accept()
        logging.info("Address: {}".format(address))
        external_request = self._wait_for_registration_request(connection)
        self._active_external_request_connection = connection
        return external_request

    def get_registration_request(self):
        try:
            external_request = self._accept_new_registration_request()
            self._active_external_request_connection.send(
                "Your request has been processed successfully".encode('utf-8'))
            return external_request

        except OSError:
            logging.error("OS Error ocurred.")
            traceback.print_exc()
            self._active_external_request_connection.sendall(responses.OS_ERROR_RESPONSE,
                                                             encoding='utf-8')
        except:
            logging.error("Error ocurred: ")
            traceback.print_exc()
            self._active_external_request_connection.sendall(responses.UNKNOWN_ERROR_RESPONSE, encoding='utf-8')

        finally:
            self._active_external_request_connection.close()
            self._active_external_request_connection = None
