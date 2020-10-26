import logging
import socket
import traceback

import network.responses as responses

from network.tgz_file_sender import TgzFileSender
from company_server_controllers.file_compressor import FileCompressor
from network.json_receiver import JsonReceiver
from network.json_sender import JsonSender


class CompanyBackupMiddleware:
    def __init__(self, port: int, listen_backlog: int, files_to_compress: int):
        logging.info("Initializing backup middleware.")
        self._backup_requests_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._backup_requests_socket.bind(('', port))
        self._backup_requests_socket.listen(listen_backlog)
        self._file_compressor = FileCompressor(files_to_compress)
        self._handle_backup_requests()

    def _process_backup_request(self, connection, backup_request):
        logging.info("Starting to process backup request.")
        try:
            new_compression, compressed_file_path = self._file_compressor.compress_files(backup_request['path'],
                                                                                         connection.getpeername()[0])
            if new_compression:
                self._send_backup_to_server(connection, compressed_file_path)
            else:
                JsonSender.send_json(connection, responses.UNNECESSARY_BACKUP_RESPONSE)

        except FileNotFoundError:
            traceback.print_exc()
            JsonSender.send_json(connection, responses.PATH_NOT_FOUND_RESPONSE)

        except:
            traceback.print_exc()
            JsonSender.send_json(connection, responses.UNKNOWN_ERROR_RESPONSE)

        finally:
            connection.close()

    def _handle_backup_requests(self):
        while True:
            logging.info("Proceed to receive backup request.")
            connection, address = self._backup_requests_socket.accept()
            logging.info("Address: {}".format(address))
            backup_request = JsonReceiver.receive_json(connection)
            self._process_backup_request(connection, backup_request)

    def _send_backup_to_server(self, connection, compressed_file_path):
        logging.info("New compression. Starting to send file.")
        JsonSender.send_json(connection, responses.START_TRANSFER_RESPONSE)
        TgzFileSender.send_file(connection, compressed_file_path)
