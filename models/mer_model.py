import os
import threading
from enum import Enum
from typing import Union, Dict, List, Tuple

from PyQt5.QtCore import pyqtSignal, QObject
from pandas import DataFrame

from modules.import_module import ImportModule

from models.dataframe_model import DataFrameModel
from utility.extractors import extract_identifiers, extract_tactical_scenario
from utility.utility import get_exception


class ImportState(Enum):
    SUCCESS = 1
    FAILED = 2
    BUSY = 3


class MerModel(QObject):
    no_tact_signal: pyqtSignal = pyqtSignal(str)
    progress_signal: pyqtSignal = pyqtSignal(bool)
    import_signal: pyqtSignal = pyqtSignal(ImportState, str)

    def __init__(self):
        super(MerModel, self).__init__()
        self.mer_df: Union[DataFrame, None] = None
        self.mer_data: Dict[str, DataFrameModel] = {}
        self.selected_df: Union[DataFrameModel, None] = None

        self.tact_lat: Union[float, None] = None
        self.tact_long: Union[float, None] = None
        self.names: Union[str, None] = None

        self.import_task: Union[ImportModule, None] = None

    def init_mer(self, df: DataFrame) -> None:
        self.mer_df: DataFrame = df

        try:
            self.tact_lat, self.tact_long = extract_tactical_scenario(df)
            self.set_mer_data(df)
        except IndexError:
            self.no_tact_signal.emit('No Tactical Scenario found, do you want to proceed?')

    def mock_tact_scenario(self):
        self.tact_lat: float = 0
        self.tact_long: float = 0
        self.set_mer_data(self.mer_df)

    def set_mer_data(self, df: DataFrame) -> None:
        grouped_by_identifier = extract_identifiers(df)

        for name, idf in grouped_by_identifier.items():
            idf = DataFrameModel(idf.copy(), name)

            from views.explorer_view import ExplorerView
            idf.explorer = ExplorerView(idf)

            self.mer_data[name] = idf

        self.selected_df = self.get_df(next(iter(grouped_by_identifier)))
        self.import_signal.emit(ImportState.SUCCESS, '')

    def on_task_busy(self, txt: str) -> None:
        self.import_signal.emit(ImportState.BUSY, txt)

    def start_task(self) -> None:
        self.reset_mer()
        self.progress_signal.emit(True)
        self.import_task.start()

    def on_task_finished(self, df: DataFrame) -> None:
        try:
            self.init_mer(df)
            self.progress_signal.emit(False)
        except Exception as e:
            self.import_signal.emit(ImportState.FAILED, 'Import Failed')
            print(get_exception(e))

    def on_task_failed(self) -> None:
        self.progress_signal.emit(False)
        self.import_signal.emit(ImportState.FAILED, 'Import Failed')

    def import_from_paths(self, paths: List[str]) -> None:
        self.names = ', '.join(map(os.path.basename, paths))
        self.import_task = ImportModule(paths)
        self.import_task.task_finished.connect(self.on_task_finished)
        self.import_task.task_failed.connect(self.on_task_failed)
        self.import_task.task_busy.connect(self.on_task_busy)
        self.start_task()

    def export_single_df(self, path: str) -> None:
        try:
            threading.Thread(target=self.selected_df.df.to_excel, args=(path, )).start()
        except Exception as e:
            print(get_exception(e))

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        self.mer_data: Dict[str, DataFrame] = {}

    def has_mer(self) -> bool:
        return bool(self.mer_data)

