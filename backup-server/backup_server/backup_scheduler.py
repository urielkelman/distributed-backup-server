import logging
from datetime import datetime
from multiprocessing import Process, Manager, Lock
from hashlib import md5
from requesters.backup_dispatcher import BackupDispatcher

REGISTER_TYPE = 'register'
UNREGISTER_TYPE = 'unregister'
STATUS_NOT_RUNNING_BACKUP = 'STATUS_NOT_RUNNING_BACKUP'
STATUS_RUNNING_BACKUP = 'STATUS_RUNNING_BACKUP'


class BackupScheduler:
    @staticmethod
    def _backup_of_frequency(backup_task):
        now = datetime.now()
        time_delta = now - backup_task['last_backup']
        return time_delta.total_seconds() > backup_task['frequency']

    @staticmethod
    def start_backups(backup_request_queue, worker_registration_queue, backup_records):
        backup_tasks = Manager().dict()
        lock_backup_tasks = Lock()
        backups_by_worker = {}
        while True:
            if not worker_registration_queue.empty():
                backuper_registration_request = worker_registration_queue.get()
                worker_ip, worker_port = backuper_registration_request['requester_ip'][0], \
                                         backuper_registration_request['worker_process_port']
                if worker_ip in backups_by_worker:
                    backups_by_worker[worker_ip][worker_port] = 0
                else:
                    backups_by_worker[worker_ip] = {
                        worker_port: 0
                    }

            if not backup_request_queue.empty():
                backup_request = backup_request_queue.get()
                logging.info("Backup scheduler received new backup request: {}".format(str(backup_request)))
                if backup_request['type'] == REGISTER_TYPE:
                    backup_tasks[(backup_request['node'], backup_request['node_port'], backup_request['path'])] = {
                        'status': STATUS_NOT_RUNNING_BACKUP,
                        'last_backup': None,
                        'frequency': backup_request['frequency'],
                        'backup_worker': BackupScheduler._select_worker_for_backup_task(backups_by_worker),
                        'hash_id': md5(bytes(backup_request['path'].replace("/", "") + str(backup_request['node']) + str(backup_request['node_port']), encoding='utf-8')).hexdigest()
                    }
                else:
                    for (node, node_port, path) in backup_tasks:
                        if node == backup_request['node'] and path == backup_request['path']:
                            lock_backup_tasks.acquire()
                            del backup_tasks[(node, node_port, path)]
                            lock_backup_tasks.release()
                            logging.info("Unregistered backup task for node: {} and path: {}".format(node, path))
                            break

            BackupScheduler._check_and_launch_backups(backup_tasks, backup_records, lock_backup_tasks)

    @staticmethod
    def _check_and_launch_backups(backup_tasks, backups_records, lock_backup_tasks):
        for node, node_port, path in backup_tasks:
            backup_task = backup_tasks[(node, node_port, path)]
            if backup_task['status'] == STATUS_NOT_RUNNING_BACKUP \
                    and (backup_task['last_backup'] is None or BackupScheduler._backup_of_frequency(backup_task)):
                backup_task['status'] = STATUS_RUNNING_BACKUP
                backup_tasks[(node, node_port, path)] = backup_task
                backup_request_process = Process(target=BackupDispatcher.dispatch_backup,
                                                 args=(node, node_port, path, backup_tasks, backups_records,
                                                       lock_backup_tasks,))
                backup_request_process.start()

    @staticmethod
    def _select_worker_for_backup_task(backups_by_worker):
        worker_with_less_tasks = sorted(backups_by_worker.items(), key=lambda w: sum(w[1].values()))[0][0]
        backups_by_port = backups_by_worker[worker_with_less_tasks]
        port_with_less_tasks = sorted(backups_by_port.items(), key=lambda x: x[1])[0][0]
        backups_by_worker[worker_with_less_tasks][port_with_less_tasks] += 1
        logging.info("Backups by workers after assigning worker: {}".format(backups_by_worker))
        return worker_with_less_tasks, port_with_less_tasks

