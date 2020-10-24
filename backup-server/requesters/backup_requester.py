import logging
import os
from time import sleep


class BackupRequester:
    STATUS_NOT_RUNNING_BACKUP = 'STATUS_NOT_RUNNING_BACKUP'
    STATUS_RUNNING_BACKUP = 'STATUS_RUNNING_BACKUP'

    @staticmethod
    def request_backup(node, node_port, path, backup_tasks):
        while True:
            backup_task = backup_tasks[(node, node_port, path)]
            backup_task['status'] = BackupRequester.STATUS_RUNNING_BACKUP
            backup_tasks[(node, node_port, path)] = backup_task
            logging.info("Launched backup request for node {} at port {} for path {}.".format(node, node_port, path))
            logging.info("Process id: {}".format(os.getpid()))
            sleep(3)
