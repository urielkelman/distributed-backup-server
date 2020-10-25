import logging
import socket
from pathlib import Path

from network.tgz_file_receiver import TgzFileReceiver
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class NodeBackupRequester:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20
    DATETIME_FORMAT = "%m/%d/%Y-%H:%M:%S"

    @staticmethod
    def _generate_backup_request(path):
        return {
            'path': path
        }

    @staticmethod
    def generate_backup(node, node_port, path):
        logging.info("Starting to generate backup for node {} with port {} for path {}".format(node, node_port, path))
        dir_path_str = "/backups/" + node + "_" + path.replace("/", "_")
        dir_path = Path(dir_path_str)
        if not dir_path.is_dir():
            dir_path.mkdir()
            logging.info("Created new directory for backups: {}".format(dir_path_str))

        connection = socket.create_connection((node, node_port))
        backup_request = NodeBackupRequester._generate_backup_request(path)
        JsonSender.send_json(connection, backup_request)

        response = JsonReceiver.receive_json(connection)

        if response['status'] == 'OK' and response['transfer']:
            timestamp = TgzFileReceiver.receive_file(connection, dir_path_str)
            return True, timestamp, None
        elif response['status'] == 'OK' and not response['transfer']:
            logging.info("It's not necessary to do a backup.")
            return False, None, None
        else:
            logging.info('An error ocurred.')
            return False, None, response['cause']
