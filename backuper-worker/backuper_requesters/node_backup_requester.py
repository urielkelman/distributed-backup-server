import logging
import socket
from pathlib import Path

from network.tgz_file_receiver import TgzFileReceiver
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender

LAST_BACKUP_FILES = 10


class NodeBackupRequester:
    @staticmethod
    def _generate_backup_request(path, id):
        return {
            'path': path,
            'id': id
        }

    @staticmethod
    def _check_and_delete_backups(dir_path_str):
        file_paths = [x for x in Path(dir_path_str).iterdir()]
        if len(file_paths) <= LAST_BACKUP_FILES:
            logging.info("It's unnecessary to delete any backup file")
        else:
            file_paths.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
            logging.info("Deleting backup file: {}".format(file_paths[-1]))
            Path(file_paths[-1]).unlink()

    @staticmethod
    def generate_backup(node, node_port, path, id):
        logging.info("Starting to generate backup for node {} with port {} for path {} and id {}.".format(node, node_port, path, id))
        dir_path_str = "/backups/" + node + "_" + path.replace("/", "_")[1:]
        dir_path = Path(dir_path_str)
        if not dir_path.is_dir():
            dir_path.mkdir()
            logging.info("Created new directory for backups: {}".format(dir_path_str))

        connection = socket.create_connection((node, node_port))
        backup_request = NodeBackupRequester._generate_backup_request(path, id)
        JsonSender.send_json(connection, backup_request)

        response = JsonReceiver.receive_json(connection)

        if response['status'] == 'OK' and response['transfer']:
            timestamp, file_size, file_name = TgzFileReceiver.receive_file(connection, dir_path_str)
            NodeBackupRequester._check_and_delete_backups(dir_path_str)
            return True, timestamp, file_size, file_name, None
        elif response['status'] == 'OK' and not response['transfer']:
            logging.info("It's not necessary to do a backup.")
            return False, None, None, None, None
        else:
            logging.info('An error ocurred.')
            return False, None, None, None, response['cause']
