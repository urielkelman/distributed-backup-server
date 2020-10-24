import logging
import tarfile
import hashlib

from pathlib import Path


class FileCompressor:
    def __init__(self, files_to_compress: int):
        logging.info("Initializing file compressor with {} files.".format(files_to_compress))
        self._last_backup_info_by_server_and_path = {}

    def _search_files_to_compress(self, parent_path, files_candidates):
        for child_path in parent_path.iterdir():
            if child_path.is_dir():
                self._search_files_to_compress(child_path, files_candidates)
            else:
                files_candidates.append(child_path)

    @staticmethod
    def _generate_checksum_for_files(file_paths):
        hash_md5 = hashlib.md5()
        for file_path in file_paths:
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(2048), b''):
                    hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def _backup_file_has_changed(self, files_candidates_to_compress, path, server_alias):
        files_candidates_to_compress.sort()
        if (server_alias, path) in self._last_backup_info_by_server_and_path and \
                files_candidates_to_compress == self._last_backup_info_by_server_and_path[(server_alias, path)]['files'] \
                and self._last_backup_info_by_server_and_path[(server_alias, path)]['checksum'] == \
                self._generate_checksum_for_files(files_candidates_to_compress):
            return False

        self._last_backup_info_by_server_and_path[(server_alias, path)] = {
            'files': files_candidates_to_compress,
            'checksum': self._generate_checksum_for_files(files_candidates_to_compress)
        }
        return True

    @staticmethod
    def _generate_tar_file(file_paths, server_alias, path):
        compressed_file_path = "backup-{}-{}.tar.gz".format(server_alias, path).replace("/", "")
        with tarfile.open(compressed_file_path, "w:gz") as tar:
            for file_path in file_paths:
                tar.add(file_path)

        return compressed_file_path

    def compress_files(self, path, server_alias):
        path = Path(path)
        if not path.is_dir():
            logging.info("Path {} doesn't exists.".format(path))
            raise FileNotFoundError(path)

        files_candidates_to_compress = []
        self._search_files_to_compress(path, files_candidates_to_compress)

        if self._backup_file_has_changed(files_candidates_to_compress, path, server_alias):
            return True, self._generate_tar_file(files_candidates_to_compress, server_alias, path)
        else:
            return False, []
