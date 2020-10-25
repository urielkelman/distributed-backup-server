import json
import logging
import socket
from datetime import datetime

from controllers.utils import padd_to_specific_size
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class BackupRequester:
    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20
    STATUS_NOT_RUNNING_BACKUP = 'STATUS_NOT_RUNNING_BACKUP'
    STATUS_RUNNING_BACKUP = 'STATUS_RUNNING_BACKUP'
    DATETIME_FORMAT = "%m/%d/%Y-%H:%M:%S"

    @staticmethod
    def _generate_backup_request(node, node_port, path):
        return {
            'node': node,
            'node_port': node_port,
            'path': path
        }

    @staticmethod
    def dispatch_backup(node, node_port, path, backup_tasks):
        backup_task = backup_tasks[(node, node_port, path)]
        backup_worker = backup_task['backup_worker']
        logging.info("Launched backup request for node {} at port {} for path {} in worker: {}.". \
                     format(node, node_port, path, str(backup_worker)))

        connection = socket.create_connection((backup_worker[0], backup_worker[1]))
        backup_request = BackupRequester._generate_backup_request(node, node_port, path)
        JsonSender.send_json(connection, backup_request)
        response = JsonReceiver.receive_json(connection)

        if response['status'] == 'ok' and response['time']:
            backup_task['last_backup'] = datetime.strptime(response['time'], BackupRequester.DATETIME_FORMAT)
        elif response['status'] == 'ok' and response['time'] is None:
            backup_task['last_backup'] = datetime.now()

        backup_task['status'] = BackupRequester.STATUS_NOT_RUNNING_BACKUP
        backup_tasks[(node, node_port, path)] = backup_task

        connection.close()
