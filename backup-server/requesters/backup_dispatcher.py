import logging
import socket
from datetime import datetime
from pathlib import Path

from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender

STATUS_NOT_RUNNING_BACKUP = 'STATUS_NOT_RUNNING_BACKUP'
DATETIME_FORMAT = "%m/%d/%Y-%H:%M:%S"

BACKUPS_FILE = "/backups/backups.csv"

class BackupDispatcher:
    @staticmethod
    def _generate_backup_request(node, node_port, path, id):
        return {
            'node': node,
            'node_port': node_port,
            'path': path,
            'id': id
        }

    @staticmethod
    def _save_backup_records(backup_records, node, path, timestamp, file_size, file_name, worker, lock_backup_file):
        backup_record = [{
            'timestamp': timestamp,
            'file_size': file_size,
            'file_name': file_name,
            'worker_ip': worker
        }]
        if node not in backup_records:
            backup_records[node] = {
                path: backup_record
            }
        else:
            node_records = backup_records[node]
            if path not in node_records:
                node_records[path] = backup_record
            else:
                node_records[path] += backup_record
            backup_records[node] = node_records

        lock_backup_file.acquire()
        mode = "w+"
        if Path(BACKUPS_FILE).is_file():
            mode = "a+"
        with open(BACKUPS_FILE, mode) as file:
            file.write("{},{},{},{},{}\n".format(node, path, timestamp, file_size, file_name, worker))
        lock_backup_file.release()

    @staticmethod
    def dispatch_backup(node, node_port, path, backup_tasks, backup_records, lock_backup_tasks, lock_backup_file):
        backup_task = backup_tasks[(node, node_port, path)]
        backup_worker = backup_task['backup_worker']
        logging.info("Launched backup request for node {} at port {} for path {} in worker: {}.". \
                     format(node, node_port, path, str(backup_worker)))

        connection = socket.create_connection((backup_worker[0], backup_worker[1]))
        backup_request = BackupDispatcher._generate_backup_request(node, node_port, path, backup_task['hash_id'])
        JsonSender.send_json(connection, backup_request)
        response = JsonReceiver.receive_json(connection)

        if response['status'] == 'ok' and response['time']:
            backup_task['last_backup'] = datetime.strptime(response['time'], DATETIME_FORMAT)
            BackupDispatcher._save_backup_records(backup_records, node, path, response['time'],
                                                  response['file_size'], response['file_name'],
                                                  backup_worker[0], lock_backup_file)
        elif response['status'] == 'ok' and response['time'] is None:
            backup_task['last_backup'] = datetime.now()

        backup_task['status'] = STATUS_NOT_RUNNING_BACKUP

        lock_backup_tasks.acquire()
        if (node, node_port, path) in backup_tasks:
            backup_tasks[(node, node_port, path)] = backup_task
        lock_backup_tasks.release()

        connection.close()
