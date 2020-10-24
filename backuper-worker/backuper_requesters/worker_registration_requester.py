import json
import socket
import logging

from backuper_requesters.utils import padd_to_specific_size


class WorkerRegistrationRequester:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20
    BYTES_AMOUNT_REGISTRATION_RESPONSE = 1024

    @staticmethod
    def register_worker_request(worker_process_port):
        return bytes(json.dumps({
            "worker_process_port": worker_process_port
        }))

    @staticmethod
    def register_worker(backup_server_ip, backup_server_port, worker_process_port):
        register_worker_request = WorkerRegistrationRequester.register_worker_request(worker_process_port)
        register_worker_request_size = padd_to_specific_size(register_worker_request,
                                                             WorkerRegistrationRequester.BYTES_AMOUNT_REQUEST_SIZE_INDICATION)

        connection = socket.create_connection((backup_server_ip, backup_server_port))
        connection.sendall(register_worker_request_size)
        connection.sendall(register_worker_request)
        register_response = json.loads(connection.recv(1024))
        logging.info("Respose to register port {} is: {}".format(worker_process_port, str(register_response)))
