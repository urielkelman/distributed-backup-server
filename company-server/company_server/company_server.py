import logging
from multiprocessing import Process
from time import sleep

from company_server_controllers.company_backup_controller import CompanyBackupMiddleware


class CompanyServer:
    def __init__(self, backup_request_port: int, listen_backlog: int):
        new_process = Process(target=self._launch_backup_middleware, args=(backup_request_port, listen_backlog, 10,))
        new_process.start()

    def _launch_backup_middleware(self, backup_request_port: int, listen_backlog: int, files_to_compress: int):
        CompanyBackupMiddleware(backup_request_port, listen_backlog, files_to_compress)

    def run(self):
        while True:
            logging.info("To sleep")
            sleep(60)




