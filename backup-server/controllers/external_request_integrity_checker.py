import socket
import json
import logging

from middleware_backup_server.utils import padd_to_specific_size


class ExternalRequestIntegrityChecker:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    @staticmethod
    def health_check_request(path):
        return bytes(json.dumps({
            'type': 'HEALTH_CHECK_REQUEST_TYPE',
            'path': path
        }))

    @staticmethod
    def _validate_address_and_path(_external_request):
        """Validates the specified node exists in the company network, and the path
        exists in the specified node.

        Parameters:
            external_request (dict): Dictionary that contains the node address and port,
            and the path that should be backuped.

        Returns:
              bool:Whether the original client request is valid or not.

        """
        external_request = json.loads(_external_request)
        connection = socket.create_connection((external_request["node"], external_request["node_port"]), timeout=2)
        health_check_request = ExternalRequestIntegrityChecker.health_check_request(external_request['path'])
        health_check_request_size = len(health_check_request)
        bytes_size_request = padd_to_specific_size(str(health_check_request_size))
        connection.sendall(bytes_size_request)

        connection.send(health_check_request)

        connection.sendall(ExternalRequestIntegrityChecker.health_check_request(external_request['path']),
                           encoding='utf-8')
        health_check_response = json.loads(connection.recv(1024).rstrip().decode('utf-8'))
        logging.info("Response received: {}".format(health_check_response))
        if health_check_response['status'] == 'OK':
            logging.info("Node {}:{} exists.".format(external_request["node"], external_request["node_port"]))

    @staticmethod
    def check_request_integrity(external_request):
        logging.info("Validating request: {}".format(json.loads(external_request)))
        ExternalRequestIntegrityChecker._validate_address_and_path(external_request)
