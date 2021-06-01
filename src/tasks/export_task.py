import os
from typing import Dict

from PyQt5.QtCore import QThread

from src.exporters.ExcelExporter import ExcelExporter
from src.interfaces.exporter_interface import IExporter
from src.tasks.TaskBase import TaskBase
from src.types import MerData
from src.utility import get_exception

from src.log import get_logger


class ExportTask(TaskBase):
    logger = get_logger(__name__)

    def __init__(self, data: MerData, dst: str):
        QThread.__init__(self)
        self.data: MerData = data
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

    def add_exporter(self, name: str, exporter: IExporter):
        self.exporters[name] = exporter
