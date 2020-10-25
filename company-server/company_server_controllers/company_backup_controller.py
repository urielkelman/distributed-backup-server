import json
import logging
import socket
import traceback
import os

from company_server_controllers.file_compressor import FileCompressor


class CompanyBackupMiddleware:
    PATH_NOT_FOUND_RESPONSE = bytes(json.dumps({
        "status": "ERROR",
        "cause": "Invalid path."
    }), encoding='utf-8')

    UNNECESSARY_BACKUP_RESPONSE = bytes(json.dumps({
        "status": "OK",
        "transfer": False
    }), encoding='utf-8')

    START_TRANSFER_RESPONSE = bytes(json.dumps({
        "status": "OK",
        "transfer": True
    }), encoding='utf-8')

    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    @staticmethod
    def padd_to_specific_size(bytes_data, size):
        if len(bytes_data) > size:
            raise ValueError("Final size should be larger than data size to padd.")
        return bytes("0" * (size - len(bytes_data)) + bytes_data, encoding='utf-8')

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
            request_size = int(connection.recv(CompanyBackupMiddleware.BYTES_AMOUNT_REQUEST_SIZE_INDICATION).decode('utf-8'))
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
                                                                                         connection.getpeername()[0])
            if new_compression:
                self._send_backup_to_server(connection, compressed_file_path)
            else:
                connection.sendall(self.padd_to_specific_size(str(len(self.UNNECESSARY_BACKUP_RESPONSE)),
                                                              self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
                connection.sendall(self.UNNECESSARY_BACKUP_RESPONSE)

        except FileNotFoundError:
            traceback.print_exc()
            connection.sendall(self.padd_to_specific_size(str(len(self.PATH_NOT_FOUND_RESPONSE)),
                                                          self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
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

    def _send_backup_to_server(self, connection, compressed_file_path):
        logging.info("New compression. Starting to send file.")
        connection.sendall(self.padd_to_specific_size(str(len(self.START_TRANSFER_RESPONSE)),
                                                      self.BYTES_AMOUNT_REQUEST_SIZE_INDICATION))
        connection.sendall(self.START_TRANSFER_RESPONSE)
        with open(compressed_file_path, "rb") as tar_gz_file:
            continue_reading = True
            i = 0
            while continue_reading:
                b = tar_gz_file.read(2047)
                b = bytes(1) + b

                if i == 72:
                    logging.info("Iteration 72. Len: {}".format(len(b)))

                connection.sendall(b)
                if len(b) < 2048:
                    logging.info("Finishing reading. Len: {}, Pid: {}, Iteration: {}".format(len(b), os.getpid(), i))
                    continue_reading = False
                i += 1

            logging.info("All the file has been transferred.")
