import logging

from datetime import datetime
from network.json_receiver import JsonReceiver

FILE_BUFFER_SIZE = 2048
DATETIME_FORMAT = "%m/%d/%Y-%H:%M:%S"


class TgzFileReceiver:
    @staticmethod
    def receive_file(connection, destination_base_path):
        file_size_response = JsonReceiver.receive_json(connection)
        file_size = file_size_response['file_size']
        logging.info("Starting to receive file of {} bytes".format(file_size))
        now = datetime.now()
        timestamp = now.strftime(DATETIME_FORMAT)
        already_received = 0
        file_name = destination_base_path + "/" + timestamp.replace("/", "_") + ".tgz"
        with open(file_name, "wb") as backup_file:
            while already_received < file_size:
                tgz_bytes = connection.recv(FILE_BUFFER_SIZE)
                backup_file.write(tgz_bytes)
                already_received += len(tgz_bytes)
            logging.info("Finished receiving backup file.")
        return timestamp, already_received, file_name
