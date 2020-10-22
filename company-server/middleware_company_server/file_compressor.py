import logging
import tarfile

from pathlib import Path


class FileCompressor:

    def __init__(self, files_to_compress: int):
        logging.info("Initializing file compressor with {} files.".format(files_to_compress))
        self._files_to_compress = files_to_compress
        self._last_backup_for_file_by_server_and_path = {}

    def _search_files_to_compress(self, parent_path, files_candidates):
        for child_path in parent_path.iterdir():
            if child_path.is_dir():
                self._search_files_to_compress(child_path, files_candidates)
            else:
                files_candidates.append((str(child_path), child_path.stat().st_mtime))
                logging.info(child_path.stat())

    def _filter_unchanged_files(self, files_candidates_to_compress, path, server_alias):
        changed_files = []
        if (server_alias, path) in self._last_backup_for_file_by_server_and_path:
            for file_candidate_path, last_update in files_candidates_to_compress:
                if file_candidate_path in self._last_backup_for_file_by_server_and_path[(server_alias, path)] \
                and last_update != self._last_backup_for_file_by_server_and_path[(server_alias, path)][file_candidate_path]:
                    self._last_backup_for_file_by_server_and_path[(server_alias, path)][file_candidate_path] = last_update
                    # Quiza aca solamente ya se puede retornar el path sin la fecha.
                    changed_files.append(file_candidate_path)

        else:
            self._last_backup_for_file_by_server_and_path[(server_alias, path)] = {}
            for file_candidate_path, last_update in files_candidates_to_compress:
                self._last_backup_for_file_by_server_and_path[(server_alias, path)][file_candidate_path] = last_update
                changed_files.append(file_candidate_path)

        return changed_files

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

        files_candidates_to_compress.sort(key=lambda x: x[1], reverse=True)
        changed_files = self._filter_unchanged_files(files_candidates_to_compress, path, server_alias)
        files_to_compress = changed_files[:self._files_to_compress]

        return self._generate_tar_file(files_to_compress, server_alias, path)
