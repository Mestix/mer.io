import os
from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal

from src.exceptions import ColumnNotFoundException, IdentifierNotFoundException
from src.exporters.ExcelExporter import ExcelExporter
from src.interfaces.exporter_interface import IExporter
from src.models.dataframe_model import DataFrameModel
from src.modules.utility import retrieve_preset
from src.utility import get_exception

from src.log import get_logger


class ExportModule(QtCore.QThread):
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger(__name__)

    def __init__(self, data: Dict[str, DataFrameModel], dst: str):
        QThread.__init__(self)
        self.data: Dict[str, DataFrameModel] = data
        self.dst: str = dst

        self.exporters: Dict[str, IExporter] = dict()
        self.add_exporter('xlsx', ExcelExporter())

    def run(self) -> None:
        try:
            self.emit_busy('Start export')
            self.export()
        except Exception as e:
            self.emit_failed(get_exception(e))

    def export(self) -> None:
        self.emit_busy('Exporting to {0}'.format(self.dst))

        exporter: str = os.path.splitext(self.dst)[1][1:].lower()

        self.exporters[exporter].export(self.data, self.dst)

        self.emit_busy('Export success')
        self.task_finished.emit()

    def emit_busy(self, txt: str):
        self.task_busy.emit(txt)
        self.logger.info(txt)

    def emit_failed(self, txt: str):
        self.task_failed.emit(txt)
        self.logger.error(txt)

    def add_exporter(self, name: str, exporter: IExporter):
        self.exporters[name] = exporter


def apply_preset(mer_data: Dict[str, DataFrameModel], preset: str):
    preset = retrieve_preset(preset)
    data: Dict[str, DataFrameModel] = dict()

    for identifier, columns in preset.items():
        if identifier not in mer_data:
            raise IdentifierNotFoundException(identifier)
        else:
            data[identifier]: DataFrameModel = mer_data[identifier]

        for col in columns:
            if col not in data[identifier].original_df:
                raise ColumnNotFoundException(col)
            else:
                continue

        data[identifier].original_df = data[identifier].original_df[columns]
    return data
