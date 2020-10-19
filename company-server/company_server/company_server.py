import logging
from multiprocessing import Process
from time import sleep

from middleware_company_server.company_backup_middleware import CompanyBackupMiddleware


class CompanyServer:
    def __init__(self, backup_request_port: int, listen_backlog: int):
        new_process = Process(target=self._launch_backup_middleware, args=(backup_request_port, listen_backlog,))
        new_process.start()

    def _launch_backup_middleware(self, backup_request_port: int, listen_backlog: int):
        CompanyBackupMiddleware(backup_request_port, listen_backlog)

    def run(self):
        while True:
            logging.info("To sleep")
            sleep(60)




