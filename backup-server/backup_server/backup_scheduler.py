class BackupScheduler:
    def __init__(self, backup_request_queue):
        self._backup_request_queue = backup_request_queue

    def start_backups(self):
        pass