from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
import pandas as pd

from models.dataframe_model import DataFrameModel
from utility.extractors import create_identifier_dict, create_mer_dict, apply_converters
from utility.importers import get_all_paths, import_and_transpose_df
from utility.utility import get_exception


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal()
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, paths):
        QThread.__init__(self)
        self.paths: List[str] = paths

    def run(self) -> None:
        self.import_from_paths(self.paths)

    def import_from_paths(self, paths) -> None:
        self.task_busy.emit('Importing files...')

        all_paths: List[str] = get_all_paths(paths)
        dfs: list[DataFrame] = []

        for path in all_paths:
            try:
                dfs.append(import_and_transpose_df(path))
            except Exception as e:
                all_paths.remove(path)
                print(get_exception(e))

        if len(dfs) > 0:
            self.task_busy.emit('Converting data...')
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            converted_df: DataFrame = apply_converters(df)
            identifier_dict: Dict[str, DataFrame] = create_identifier_dict(converted_df)
            mer_data: Dict[str, DataFrameModel] = create_mer_dict(identifier_dict)
            self.task_finished.emit(mer_data)
        else:
            self.task_failed.emit()


