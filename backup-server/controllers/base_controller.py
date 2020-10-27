import logging
import socket
import traceback

import network.responses as responses
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class BaseRegistrationController:
    def __init__(self, port: int, listen_backlog: int):
        self._port = port
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._active_external_request_connection = None

    def _accept_new_registration_request(self):
        logging.info("Proceed to receive new external request at port {}.".format(self._port))
        connection, address = self._external_requests_socket.accept()
        logging.info("Address: {}".format(address))
        external_request = JsonReceiver.receive_json(connection)
        self._active_external_request_connection = connection
        return external_request

    def get_registration_request(self):
        try:
            external_request = self._accept_new_registration_request()
            external_request['requester_ip'] = self._active_external_request_connection.getpeername()
            JsonSender.send_json(self._active_external_request_connection, responses.OK_RESPONSE)
            return external_request

        except OSError:
            logging.error("OS Error ocurred.")
            traceback.print_exc()
            JsonSender.send_json(self._active_external_request_connection, responses.OS_ERROR_RESPONSE)
        except:
            logging.error("Unexpected error ocurred: ")
            traceback.print_exc()
            JsonSender.send_json(self._active_external_request_connection, responses.UNKNOWN_ERROR_RESPONSE)

        finally:
            self._active_external_request_connection.close()
            self._active_external_request_connection = None
