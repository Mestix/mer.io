from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
import pandas as pd

from models.converter_model import Converter
from utility.cleaners import clean_datetime_columns, clean_scientific_columns, sort_on_datetime
from utility.importers import get_all_paths, import_and_transpose_df
from utility.utility import get_exception

converters: List[Converter] = [
    Converter(name='clean_datetime_columns', func=clean_datetime_columns, active=True),
    Converter(name='clean_scientific_columns', func=clean_scientific_columns, active=True),
    Converter(name='sort_on_datetime', func=sort_on_datetime, active=True)
]


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(DataFrame)
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
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            self.apply_converters(df)
        else:
            self.task_failed.emit()

    def apply_converters(self, df: DataFrame) -> None:
        self.task_busy.emit('Converting data...')

        new_data: DataFrame = df.copy()
        for converter in converters:
            if converter.active:
                new_data = converter.convert(new_data)

        self.task_finished.emit(new_data)
