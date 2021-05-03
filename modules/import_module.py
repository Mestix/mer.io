from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
import pandas as pd

from exceptions import NoValidMerImportTypeException
from importers.binary_importer import BinaryImporter
from importers.text_importer import TextImporter
from models.dataframe_model import DataFrameModel
from utility.extractors import create_identifier_dict, create_mer_dict
from utility.utility import get_exception, get_all_paths


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, paths):
        QThread.__init__(self)
        self.paths: List[str] = paths
        self.text_importer = TextImporter()
        self.binary_importer = BinaryImporter()

    def run(self) -> None:
        try:
            self.import_from_paths(self.paths)
        except Exception as e:
            print('ImportModule.run: ' + get_exception(e))

    def import_from_paths(self, paths) -> None:
        self.task_busy.emit('Importing files...')

        all_paths: List[str] = get_all_paths(paths)
        dfs: list[DataFrame] = list()

        for path in all_paths:
            try:
                if path.endswith('.txt'):
                    dfs.append(self.text_importer.run(path))
                elif path.endswith('.mer'):
                    # Not implemented yet
                    dfs.append(self.binary_importer.run(path))
                else:
                    raise NoValidMerImportTypeException
            except Exception as e:
                all_paths.remove(path)
                print('ImportModule.import_from_paths: ' + get_exception(e))

        try:
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            mer_data: Dict[str, DataFrameModel] = create_mer_dict(create_identifier_dict(df.copy()))
            unique_refs: List[str] = df['REFERENCE'].unique()

            self.task_finished.emit(dict({
                'mer_data': mer_data,
                'unique_refs': unique_refs
            }))
        except Exception as e:
            print('ImportModule.import_from_paths: ' + get_exception(e))
            self.task_failed.emit('No data found')

