from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal

import pandas as pd

from src.models.dataframe_model import DataFrameModel
from src.utility.utility import get_exception

from src.log import get_logger


class ExportModule(QtCore.QThread):
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger('ExportModule')

    def __init__(self, data: Dict[str, DataFrameModel], dst: str):
        QThread.__init__(self)
        self.data: Dict[str, DataFrameModel] = data
        self.dst: str = dst
        self.writer: pd.ExcelWriter = pd.ExcelWriter(dst)

    def run(self) -> None:
        try:
            self.emit_busy('Start export')
            self.export()
        except Exception as e:
            self.emit_failed(get_exception(e))

    def export(self) -> None:
        self.emit_busy('Exporting to {0}'.format(self.dst))

        df: DataFrameModel
        for name, dfm in self.data.items():
            dfm.df.to_excel(self.writer, name)

        self.writer.save()
        self.emit_busy('Export success')
        self.task_finished.emit()

    def emit_busy(self, txt: str):
        self.task_busy.emit(txt)
        self.logger.info(txt)

    def emit_failed(self, txt: str):
        self.task_failed.emit(txt)
        self.logger.error(txt)

