import logging
from time import sleep
from multiprocessing import Process
from backuper_requesters.worker_registration_requester import WorkerRegistrationRequester

class BackuperWorkerServer:
    def __init__(self, backup_server_ip: str, backup_server_port: int, worker_first_port: int,
                 worker_processes: int, listen_backlog: int):
        self._backup_server_ip = backup_server_ip
        self._backup_server_port = backup_server_port
        self._worker_first_port = worker_first_port
        self._worker_processes = worker_processes
        self._listen_backlog = listen_backlog

    @staticmethod
    def _start_worker(backup_server_ip, backup_server_port, worker_process_port, listen_backlog):
        WorkerRegistrationRequester.register_worker(backup_server_ip, backup_server_port, worker_process_port)

    def run(self):
        for i in range(self._worker_processes):
            worker_listen_port = self._worker_first_port + i
            worker_process = Process(target=self._start_worker, args=(self._backup_server_ip, self._backup_server_port,
                                                                      worker_listen_port, self._listen_backlog))
            worker_process.start()





