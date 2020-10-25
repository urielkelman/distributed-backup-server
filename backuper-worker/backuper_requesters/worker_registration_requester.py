import json
import socket
import logging

from time import sleep
from network.json_sender import JsonSender
from network.json_receiver import JsonReceiver


class WorkerRegistrationRequester:
    @staticmethod
    def register_worker_request(worker_process_port):
        return {
            "worker_process_port": worker_process_port
        }

    @staticmethod
    def register_worker(backup_server_ip, backup_server_port, worker_process_port):
        connection_established = False
        while not connection_established:
            try:
                connection = socket.create_connection((backup_server_ip, backup_server_port))
                connection_established = True
                register_worker_request = WorkerRegistrationRequester.register_worker_request(worker_process_port)
                JsonSender.send_json(connection, register_worker_request)
                register_response = JsonReceiver.receive_json(connection)
                logging.info("Response to register port {} is: {}".format(worker_process_port, str(register_response)))
            except socket.gaierror:
                logging.info("Retrying connection in one second: {}:{}".format(backup_server_ip, backup_server_port))
                sleep(1)
