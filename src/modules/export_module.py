from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal

import pandas as pd

from src.models.dataframe_model import DataFrameModel
from src.utility.utility import get_exception


class ExportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal()
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, data: Dict[str, DataFrameModel], dst: str):
        QThread.__init__(self)
        self.data: Dict[str, DataFrameModel] = data
        self.writer: pd.ExcelWriter = pd.ExcelWriter(dst)

    def run(self) -> None:
        try:
            self.task_busy.emit('Start export')
            self.export()
        except Exception as e:
            print('ExportModule.run: ' + get_exception(e))
            self.task_failed.emit()

    def export(self) -> None:
        self.task_busy.emit('Exporting...')
        df: DataFrameModel
        for name, dfm in self.data.items():
            dfm.df.to_excel(self.writer, name)

        self.writer.save()
        self.task_finished.emit()
        self.task_busy.emit('Export finished')
