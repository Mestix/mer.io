import fnmatch
import json
import os
import shutil
import zipfile
from typing import List, Generator


def get_exception(ex: Exception) -> str:
    return 'An exception of type {0} occurred. Arguments: {1!r}'.format(type(ex).__name__, ex.args)


def get_valid_files(paths: List[str]) -> List[str]:
    all_paths = []

    for path in paths:
        if path.endswith('.txt'):
            all_paths.append(path)
        elif path.endswith('.zip'):
            all_paths.extend(get_txt_files_from_zip(path))
        elif path.endswith('.mer'):
            all_paths.append(path)
        else:
            raise TypeError('Can only import .txt, .zip & .mer. Invalid file: ' + path)
    return all_paths


def get_txt_files_from_zip(path: str) -> List[str]:
    dir_path = 'temp'

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

    txt_files = find_txt_files(dir_path)

    return list(txt_files)


def find_txt_files(path: str) -> Generator:
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, '*.txt'):
            yield os.path.join(root, file)


def get_valid_files_from_folder(path: str) -> Generator:
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


def retrieve_preset(preset: str):
    with open('assets/presets/' + preset + '.json') as f:
        contents = f.read()
        preset = json.loads(contents)

    return dict(preset)



