import os
from typing import Union, Dict

from PyQt5.QtCore import pyqtSignal, QObject
from pandas import DataFrame

from modules.import_module import ImportModule

from models.dataframe_model import DataFrameModel
from utility.extractors import extract_identifiers, extract_tactical_scenario
from utility.utility import get_exception


class MerModel(QObject):
    mer_set_signal: pyqtSignal = pyqtSignal()

    progress_signal: pyqtSignal = pyqtSignal(bool)
    confirm_signal: pyqtSignal = pyqtSignal(str)
    yesno_signal: pyqtSignal = pyqtSignal(str)

    import_fail_signal: pyqtSignal = pyqtSignal(str)
    import_busy_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super(MerModel, self).__init__()
        self.mer_df: Union[DataFrame, None] = None
        self.mer_data: Dict[str, DataFrameModel] = {}

        self.tact_lat: Union[float, None] = None
        self.tact_long: Union[float, None] = None
        self.names: Union[str, None] = None

        self.import_task: Union[ImportModule, None] = None

    def init_mer(self, df: DataFrame) -> None:
        self.mer_df = df

        try:
            self.tact_lat, self.tact_long = extract_tactical_scenario(df)
            self.set_mer_data(df)
        except IndexError:
            self.yesno_signal.emit('No Tactical Scenario found, do you want to proceed?')
            pass

    def mock_tact_scenario(self):
        self.tact_lat = 0
        self.tact_long = 0
        self.set_mer_data(self.mer_df)

    def set_mer_data(self, df: DataFrame) -> None:
        grouped_by_identifier = extract_identifiers(df)

        for name, idf in grouped_by_identifier.items():
            idf = DataFrameModel(idf.copy(), name)
            self.mer_data[name] = idf

        self.mer_set_signal.emit()

    def on_task_busy(self, text) -> None:
        self.import_busy_signal.emit(text)

    def start_task(self) -> None:
        self.reset_mer()
        self.progress_signal.emit(True)
        self.import_task.start()

    def on_task_finished(self, df: DataFrame) -> None:
        try:
            self.init_mer(df)
            self.progress_signal.emit(False)
        except Exception as e:
            self.confirm_signal.emit('Import failed')
            print(get_exception(e))

    def on_task_failed(self) -> None:
        self.progress_signal.emit(False)
        self.confirm_signal.emit('Import failed')

    def import_from_paths(self, paths) -> None:
        self.names = ', '.join(map(os.path.basename, paths))
        self.import_task = ImportModule(paths)
        self.import_task.task_finished.connect(self.on_task_finished)
        self.import_task.task_failed.connect(self.on_task_failed)
        self.import_task.task_busy.connect(self.on_task_busy)
        self.start_task()

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        if bool(self.mer_data):
            self.mer_data = {}
        else:
            pass

