BYTES_AMOUNT_FILE_SIZE = 40
FILE_BUFFER_SIZE = 2048


class TgzFileSender:
    @staticmethod
    def send_file(connection, compressed_file_path):
