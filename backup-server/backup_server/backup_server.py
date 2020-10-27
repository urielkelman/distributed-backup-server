import logging

from controllers.base_controller import BaseRegistrationController
from multiprocessing import Queue, Process, Manager
from backup_server.backup_scheduler import BackupScheduler
from controllers.query_backups_controller import QueryBackupsController


class BackupServer:
    def __init__(self, backup_request_port, listen_backlog, backuper_register_port, backup_info_port):
        self._backup_request_port = backup_request_port
        self._listen_backlog = listen_backlog
        self._node_register_port = backuper_register_port
        self._backup_info_port = backup_info_port
        self._backuper_registration_controller = BaseRegistrationController(backuper_register_port, listen_backlog)

    @staticmethod
    def _process_backups_requests(backup_requests_queue, port, listen_backlog):
        backup_registration_controller = BaseRegistrationController(port, listen_backlog)
        while True:
            backup_request = backup_registration_controller.get_registration_request()
            backup_requests_queue.put(backup_request)

    def _launch_backup_controller(self, backup_request_queue):
        backup_process_process = Process(target=self._process_backups_requests,
                                         args=(backup_request_queue, self._backup_request_port, self._listen_backlog))
        backup_process_process.start()

    def _launch_backup_scheduler(self, backup_request_queue, worker_registration_queue, backups_record):
        backup_scheduler_process = Process(target=BackupScheduler.start_backups, args=(backup_request_queue,
                                                                                       worker_registration_queue,
                                                                                       backups_record,))
        backup_scheduler_process.start()

    def _launch_query_controller(self, backup_records, query_port):
        query_controller = QueryBackupsController(query_port, self._listen_backlog, backup_records)
        query_controller_process = Process(target=query_controller.listen_to_queries)
        query_controller_process.start()

    def run(self):
        backups_record = Manager().dict()
        backup_request_queue = Queue()
        backuper_registration_queue = Queue()
        self._launch_query_controller(backups_record, self._backup_info_port)
        self._launch_backup_scheduler(backup_request_queue, backuper_registration_queue, backups_record)
        self._launch_backup_controller(backup_request_queue)
        while True:
            backuper_registration_request = self._backuper_registration_controller.get_registration_request()
            logging.info("Backuper registration request: {}".format(backuper_registration_request))
            backuper_registration_queue.put(backuper_registration_request)

