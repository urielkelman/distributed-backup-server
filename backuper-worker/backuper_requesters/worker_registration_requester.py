import json
import socket
import logging

from time import sleep
from backuper_requesters.utils import padd_to_specific_size


class WorkerRegistrationRequester:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20
    BYTES_AMOUNT_REGISTRATION_RESPONSE = 1024

    @staticmethod
    def register_worker_request(worker_process_port):
        return bytes(json.dumps({
            "worker_process_port": worker_process_port
        }), encoding='utf-8')

    @staticmethod
    def register_worker(backup_server_ip, backup_server_port, worker_process_port):
        register_worker_request = WorkerRegistrationRequester.register_worker_request(worker_process_port)
        register_worker_request_size = padd_to_specific_size(str(len(register_worker_request)),
                                                             WorkerRegistrationRequester.BYTES_AMOUNT_REQUEST_SIZE_INDICATION)
        connection_established = False

        while not connection_established:
            try:
                connection = socket.create_connection((backup_server_ip, backup_server_port))
                connection_established = True
            except socket.gaierror:
                logging.info("Retrying connection in one second: {}:{}".format(backup_server_ip, backup_server_port))
                sleep(1)

        connection.sendall(register_worker_request_size)
        connection.sendall(register_worker_request)
        register_response = json.loads(connection.recv(1024))
        logging.info("Respose to register port {} is: {}".format(worker_process_port, str(register_response)))
