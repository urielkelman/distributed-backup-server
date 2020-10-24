import socket
import logging
import json
import traceback

from multiprocessing import Process
from company_server_controllers.file_compressor import FileCompressor


class CompanyBackupMiddleware:
    PATH_NOT_FOUND_RESPONSE = json.dumps({
        "status": "ERROR",
        "cause": "Invalid path."
    })

    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    def __init__(self, port: int, listen_backlog: int, files_to_compress: int):
        logging.info("Initializing backup middleware.")
        self._backup_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._backup_requests_socket.bind(('', port))
        self._backup_requests_socket.listen(listen_backlog)
        self._file_compressor = FileCompressor(files_to_compress)
        self._handle_backup_requests()

    @staticmethod
    def _wait_for_backup_request(connection):
        try:
            request_size = int(connection.recv(1024).rstrip().decode('utf'))
            logging.info("Ready to receive {} bytes.".format(request_size))
            external_request = connection.recv(request_size)
            logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                               external_request))
            return external_request.decode('utf-8')
        except OSError:
            logging.error("Error reading socket {}".format(connection))
            connection.send('There was an error reading the socket'.encode('utf-8'))
            connection.close()

    def _process_backup_request(self, connection, backup_request):
        backup_request = json.loads(backup_request)

        logging.info("Starting to process backup request.")
        try:
            new_compression, compressed_file_path = self._file_compressor.compress_files(backup_request['path'],
                                                                                         backup_request['server_alias'])
            if new_compression:
                self._send_backup_to_server(connection, compressed_file_path)
            else:
                connection.sendall(bytes([0]))

        except FileNotFoundError:
            traceback.print_exc()
            connection.sendall(bytes(self.PATH_NOT_FOUND_RESPONSE, encoding='utf-8'))

        finally:
            connection.close()

    def _handle_backup_requests(self):
        while True:
            logging.info("Proceed to receive backup request.")
            connection, address = self._backup_requests_socket.accept()
            logging.info("Address: {}".format(address))
            backup_request = self._wait_for_backup_request(connection)
            self._process_backup_request(connection, backup_request)

    @staticmethod
    def _send_backup_to_server(connection, compressed_file_path):
        logging.info("New compression. Starting to send file.")
        connection.sendall(bytes([1]))
        with open(compressed_file_path, "rb") as tar_gz_file:
            continue_reading = True
            while continue_reading:
                b = tar_gz_file.read(2047)
                b = bytes(1) + b
                print("Byte lentgh", len(b))
                connection.sendall(b)
                if len(b) < 2048:
                    continue_reading = False
