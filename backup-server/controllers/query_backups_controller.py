import socket
import logging
import traceback


from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender

BACKUPS_FOLDER = "/backups/"


class QueryBackupsController:
    def __init__(self, port, listen_backlog, lock_backup_file):
        self._external_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._external_requests_socket.bind(('', port))
        self._external_requests_socket.listen(listen_backlog)
        self._lock_backup_file = lock_backup_file

    def _retrieve_backups(self, node, path):
        backups = []
        backups_file_name = BACKUPS_FOLDER + node + path.replace("/", "_") + ".csv"
        self._lock_backup_file.acquire()
        logging.info("Reading backup file.")

        with open(backups_file_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                timestamp, file_size, file_name, worker = line.rstrip().split(",")
                backups.append({
                    'timestamp': timestamp,
                    'file_size': file_size,
                    'file_name': file_name,
                    'worker_ip': worker
                })
        self._lock_backup_file.release()
        return backups

    def listen_to_queries(self):
        while True:
            connection, address = self._external_requests_socket.accept()
            query_request = JsonReceiver.receive_json(connection)
            try:
                if query_request['type'] == 'query':
                    logging.info("Answering query controller correctly.")
                    JsonSender.send_json(connection,
                                         self._retrieve_backups(query_request["node"], query_request["path"]))
                else:
                    JsonSender.send_json(connection, {'status': 'ERROR'})
            except:
                traceback.print_exc()
                logging.info("Answering query controller with error message.")
                JsonSender.send_json(connection, {'status': 'ERROR'})
