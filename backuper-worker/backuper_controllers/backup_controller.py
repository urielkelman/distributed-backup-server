import logging
import os
import socket
import traceback

import network.responses as responses
from backuper_requesters.node_backup_requester import NodeBackupRequester
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class BackupController:
    def __init__(self, port: int, listen_backlog: int):
        self._backup_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._backup_requests_socket.bind(('', port))
        self._backup_requests_socket.listen(listen_backlog)
        self._active_external_request_connection = None

    @staticmethod
    def _successful_backup_response(timestamp):
        return {
            'status': 'ok',
            'time': timestamp
        }

    @staticmethod
    def _error_response(error):
        return {
            'status': 'error',
            'cause': error
        }

    @staticmethod
    def _unnecessary_backup_response():
        return {
            'status': 'ok',
            'time': None
        }

    def _accept_new_backup_request(self):
        logging.info("Proceed to receive new backup request from backup server.")
        connection, address = self._backup_requests_socket.accept()
        logging.info("Address: {}".format(address))
        backup_request = JsonReceiver.receive_json(connection)
        self._active_external_request_connection = connection
        return backup_request

    def _send_response(self, response):
        JsonSender.send_json(self._active_external_request_connection, response)

    def process_backup_request(self):
        try:
            backup_request = self._accept_new_backup_request()
            has_backuped, timestamp, error = NodeBackupRequester.generate_backup(backup_request['node'],
                                                                                 backup_request['node_port'],
                                                                                 backup_request['path'])

            if has_backuped:
                self._send_response(self._successful_backup_response(timestamp))
            elif error:
                self._send_response(self._error_response(error))
            else:
                self._send_response(self._unnecessary_backup_response())

        except OSError:
            logging.error("OS Error ocurred. Pid: {}".format(os.getpid()))
            traceback.print_exc()
            self._send_response(responses.OS_ERROR_RESPONSE)
        except:
            logging.error("Unexpected error ocurred: ")
            traceback.print_exc()
            self._send_response(responses.UNKNOWN_ERROR_RESPONSE)

        finally:
            self._active_external_request_connection.close()
            self._active_external_request_connection = None
