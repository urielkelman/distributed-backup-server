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
        with open((destination_base_path + "/" + timestamp.replace("/", "_") + ".tgz"), "wb") as backup_file:
            already_received = 0
            i = 0
            while already_received < file_size:
                tgz_bytes = connection.recv(FILE_BUFFER_SIZE)
                backup_file.write(tgz_bytes)
                already_received += len(tgz_bytes)
                if i % 1000 == 0:
                    logging.info("Iteration {}, received: {}, percentage: {}".format(i, already_received, already_received*100/file_size))
                    logging.info("Alreday received {}, file size {}".format(already_received, file_size))
                i += 1

            logging.info("Finished receiving backup file.")
        return timestamp
