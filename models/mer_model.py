import os
from enum import Enum
from typing import Union, Dict, List, Generator

from PyQt5.QtCore import pyqtSignal, QObject
from pandas import DataFrame

from modules.import_module import ImportModule

from models.dataframe_model import DataFrameModel
from utility.extractors import extract_tactical_scenario
from utility.utility import get_exception


class ImportState(Enum):
    SUCCESS = 0
    FAILED = 1
    BUSY = 2


class MerModel(QObject):
    no_tact_signal: pyqtSignal = pyqtSignal(str)
    import_signal: pyqtSignal = pyqtSignal(ImportState, str)

    def __init__(self):
        super(MerModel, self).__init__()
        self.mer_data: Dict[str, DataFrameModel] = dict()
        self.selected_df: Union[DataFrameModel, None] = None

        self.tact_lat: float = float()
        self.tact_long: float = float()
        self.names: str = str()

        self.import_task: Union[ImportModule, None] = None

    def init_mer(self, mer_data: Dict[str, DataFrameModel]) -> None:
        self.mer_data = mer_data
        try:
            self.tact_lat, self.tact_long = extract_tactical_scenario(mer_data['TACTICAL_SCENARIO'].df_unfiltered)
            self.import_signal.emit(ImportState.SUCCESS, '')
        except KeyError as e:
            self.no_tact_signal.emit('No Tactical Scenario found, do you want to proceed?')
            print(get_exception(e))

    def mock_tact_scenario(self):
        self.tact_lat: float = 0
        self.tact_long: float = 0
        self.import_signal.emit(ImportState.SUCCESS, '')

    def start_task(self) -> None:
        self.reset_mer()
        self.import_task.start()

    def on_task_busy(self, txt: str) -> None:
        self.import_signal.emit(ImportState.BUSY, txt)

    def on_task_finished(self, mer_data: Dict[str, DataFrameModel]) -> None:
        self.init_mer(mer_data)

    def on_task_failed(self) -> None:
        self.import_signal.emit(ImportState.FAILED, 'Import Failed')

    def import_from_paths(self, paths: List[str]) -> None:
        self.names = ', '.join(map(os.path.basename, paths))
        self.import_task = ImportModule(paths)
        self.import_task.task_finished.connect(self.on_task_finished)
        self.import_task.task_failed.connect(self.on_task_failed)
        self.import_task.task_busy.connect(self.on_task_busy)
        self.start_task()

    def export(self, path: str, selected_items: Generator) -> None:
        import pandas as pd
        writer: pd.ExcelWriter = pd.ExcelWriter(path)

        for name in selected_items:
            df: DataFrame = self.get_df(name).df
            df.to_excel(writer, name)

        writer.save()

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        self.mer_data: Dict[str, DataFrame] = {}

    def has_mer(self) -> bool:
        return bool(self.mer_data)

