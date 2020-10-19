import socket
import json
import logging

class ExternalRequestIntegrityChecker:
    HEALTH_CHECK_REQUEST = {
        'type': 'HEALTH_CHECK_REQUEST_TYPE'
    }

    @staticmethod
    def _validate_fields(external_request):
        if 'type' not in external_request:
            raise ValueError('Request should have \'type\' field')

    @staticmethod
    def _validate_address(external_request):
        external_request = json.loads(external_request)
        connection = socket.create_connection((external_request["node"], external_request["node_port"]), timeout=2)
        connection.sendall(bytes(json.dumps(ExternalRequestIntegrityChecker.HEALTH_CHECK_REQUEST), encoding='utf-8'))
        health_check_response = json.loads(connection.recv(1024).rstrip().decode('utf-8'))
        logging.info("Response received: {}".format(health_check_response))
        if health_check_response['status'] == 'OK':
            logging.info("Node {}:{} exists.".format(external_request["node"], external_request["node_port"]))

    @staticmethod
    def check_request_integrity(external_request):
        logging.info("Validating request: {}".format(json.loads(external_request)))
        ExternalRequestIntegrityChecker._validate_fields(external_request)
        ExternalRequestIntegrityChecker._validate_address(external_request)