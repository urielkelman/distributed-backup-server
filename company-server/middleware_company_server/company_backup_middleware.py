import socket
import logging
import json
import traceback

from multiprocessing import Process
from middleware_company_server.file_compressor import FileCompressor


class CompanyBackupMiddleware:
    HEALTH_CHECK_REQUEST_TYPE = 'HEALTH_CHECK_REQUEST_TYPE'
    HEALTH_CHECK_RESPONSE = json.dumps({
        "status": "OK"
    })
    PATH_NOT_FOUND_RESPONSE = json.dumps({
        "status": "ERROR",
        "cause": "Invalid path."
    })

    def __init__(self, port: int, listen_backlog: int, files_to_compress: int):
        logging.info("initializing backup middleware.")
        self._backup_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._backup_requests_socket.bind(('', port))
        self._backup_requests_socket.listen(listen_backlog)
        self._file_compressor = FileCompressor(files_to_compress)
        self._handle_backup_requests()

    def _wait_for_backup_request(self, connection):
        try:
            external_request = connection.recv(1024).rstrip()
            logging.info('Request received from connection {}. Msg: {}'.format(connection.getpeername(),
                                                                               external_request))
            return external_request.decode('utf-8')
        except OSError:
            logging.error("Error reading socket {}".format(connection))
            connection.send('There was an error reading the socket'.encode('utf-8'))



    def _process_backup_request(self, connection, backup_request):
        backup_request = json.loads(backup_request)
        if backup_request['type'] == self.HEALTH_CHECK_REQUEST_TYPE:
            logging.info("Answering health check request.")
            connection.sendall(bytes(self.HEALTH_CHECK_RESPONSE, encoding='utf-8'))
        else:
            logging.info("Starting to process backup request.")
            try:
                compressed_file_path = self._file_compressor.compress_files(backup_request['path'],
                                                     backup_request['server_alias'])
                sending_process = Process(target=self._send_backup_to_server, args=(connection, compressed_file_path,))
                sending_process.start()

            except FileNotFoundError:
                traceback.print_exc()
                connection.sendall(bytes(self.PATH_NOT_FOUND_RESPONSE, encoding='utf-8'))
            #Sacar este finally que si no le va a cerrar la conexion.
            finally:
                logging.info("Closing connection.")
                connection.close()

    def _handle_backup_requests(self):
        while True:
            logging.info("Proceed to receive backup request.")
            connection, address = self._backup_requests_socket.accept()
            logging.info("Address: {}".format(address))
            backup_request = self._wait_for_backup_request(connection)
            self._process_backup_request(connection, backup_request)

    def _send_backup_to_server(self, connection, compressed_file_path):
        with open(compressed_file_path, "rb") as tar_gz_file:
            continue_reading = True
            while continue_reading:
                b = tar_gz_file.read(2047)
                b = bytes(1) + b
                print("Byte lentgh", len(b))
                connection.sendall(b)
                if len(b) < 2048:
                    continue_reading = False




