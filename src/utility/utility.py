import fnmatch
import os
import shutil
import zipfile
from typing import List, Generator

from PyQt5.QtWidgets import QFileDialog


def get_exception(ex: Exception) -> str:
    return 'An exception of type {0} occurred. Arguments: {1!r}'.format(type(ex).__name__, ex.args)


def save_file() -> str:
    dialog = QFileDialog()
    path, _ = dialog.getSaveFileName(filter="*.xlsx")
    return path


def open_file() -> List[str]:
    dialog = QFileDialog()
    paths, _ = dialog.getOpenFileNames(filter='*.txt *.zip')

    return paths


def get_all_paths(paths: List[str]) -> List[str]:
    all_paths = []

    for path in paths:
        if path.endswith('.txt'):
            all_paths.append(path)
        elif path.endswith('.zip'):
            all_paths.extend(get_paths_from_zip(path))
        elif path.endswith('.mer'):
            all_paths.append(path)
        else:
            raise TypeError('Can only import .txt, .zip & .mer. Invalid file: ' + path)
    return all_paths


def get_paths_from_zip(path: str) -> List[str]:
    dir_path = 'temp'
    remove_tempdir_contents()

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

    txt_files = find_txt_files(dir_path)

    return list(txt_files)


def find_txt_files(path: str) -> Generator:
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, '*.txt'):
            yield os.path.join(root, file)


def get_files_from_folder(path: str) -> Generator:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.txt', '.zip')):
                yield os.path.join(root, file)


def remove_tempdir_contents() -> None:
    for root, dirs, files in os.walk('temp'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


