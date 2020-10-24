import logging

from time import sleep
from requesters.backup_requester import BackupRequester
from multiprocessing import Process, Manager


class BackupScheduler:
    REGISTER_TYPE = 'register'
    UNREGISTER_TYPE = 'unregister'

    STATUS_NOT_RUNNING_BACKUP = 'STATUS_NOT_RUNNING_BACKUP'
    STATUS_RUNNING_BACKUP = 'STATUS_RUNNING_BACKUP'

    @staticmethod
    def _check_and_launch_backups(backup_tasks):
        for node, node_port, path in backup_tasks:
            backup_task = backup_tasks[(node, node_port, path)]
            if backup_task['status'] == BackupScheduler.STATUS_NOT_RUNNING_BACKUP and backup_task['last_backup'] is None:
                backup_request_process = Process(target=BackupRequester.request_backup,
                                                 args=(node, node_port, path, backup_tasks,))
                backup_request_process.start()

    @staticmethod
    def start_backups(backup_request_queue):
        backup_tasks = Manager().dict()
        while True:
            if not backup_request_queue.empty():
                backup_request = backup_request_queue.get()
                logging.info("Backup scheduler received new backup request: {}".format(str(backup_request)))
                if backup_request['type'] == BackupScheduler.REGISTER_TYPE:
                    backup_tasks[(backup_request['node'], backup_request['node_port'], backup_request['path'])] = {
                        'status': BackupScheduler.STATUS_NOT_RUNNING_BACKUP,
                        'last_backup': None,
                        'frequency': backup_request['frequency']
                    }

            BackupScheduler._check_and_launch_backups(backup_tasks)

            logging.info("scheduler to sleep")
            sleep(10)
