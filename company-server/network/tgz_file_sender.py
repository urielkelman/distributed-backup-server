import logging

from pathlib import Path
from network.json_sender import JsonSender

FILE_BUFFER_SIZE = 2048

class TgzFileSender:
    @staticmethod
    def _send_fixed_file_size(connection, file_size):
        JsonSender.send_json(connection, {'file_size': file_size})

    @staticmethod
    def send_file(connection, compressed_file_path):
        file_size = Path(compressed_file_path).stat().st_size
        TgzFileSender._send_fixed_file_size(connection, file_size)
        logging.info("Starting to send file in {} iterations.".format(int(file_size/FILE_BUFFER_SIZE)))
        with open(compressed_file_path, "rb") as tar_gz_file:
            continue_reading = True
            total_bytes_sent = 0
            while continue_reading:
                b = tar_gz_file.read(FILE_BUFFER_SIZE)
                if len(b) > 0:
                    connection.sendall(b)
                if len(b) < 2048:
                    continue_reading = False
                total_bytes_sent += len(b)
            logging.info("All the file has been transferred. Total bytes: {}".format(total_bytes_sent))
