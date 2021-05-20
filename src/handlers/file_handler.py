import functools
from typing import Dict, List, Union

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.exceptions import NoTactScenarioFoundException
from src.handlers.utility import mock_tact_scenario
from src.handlers.handler_base import HandlerBase
from src.models.dataframe_model import DataFrameModel
from src.tasks.convert_module import ConvertTask
from src.tasks.export_module import ExportTask
from src.tasks.import_module import ImportTask

from src.log import get_logger
from src.types import MerData
from src.views.bulk_export_dlg import BulkSettings


class FileHandler(HandlerBase):
    task_finished: pyqtSignal = pyqtSignal(object)

    logger = get_logger(__name__)

    def __init__(self, parent):
        super().__init__(parent)
        self.settings: Union[BulkSettings, None] = None

    def start_import(self, settings: BulkSettings):
        importer: ImportTask = ImportTask(settings.src)
        importer.task_finished.connect(self.start_convert)
        importer.task_failed.connect(self.on_task_failed)
        importer.task_busy.connect(self.on_task_busy)

        importer.task_finished.connect(functools.partial(self.remove_task, importer))

        self.add_task(importer)

        importer.start()

    def start_convert(self, _import: Dict) -> None:
        mer_data: MerData
        try:
            mer_data: MerData = self.verify_tact_scenarios(
                _import['unique_refs'],
                _import['mer_data']
            )
        except NoTactScenarioFoundException:
            self.task_failed.emit('Import Failed')
            return

        converter: ConvertTask = ConvertTask(mer_data)
        converter.task_finished.connect(self.on_task_finished)
        converter.task_failed.connect(self.on_task_failed)
        converter.task_busy.connect(self.on_task_busy)
        converter.task_finished.connect(functools.partial(self.remove_task, converter))

        self.add_task(converter)

        converter.start()

    def start_export(self, data: MerData):
        exporter: ExportTask = ExportTask(data, self.settings.dst)

        exporter.task_failed.connect(self.on_task_failed)
        exporter.task_busy.connect(self.on_task_busy)
        exporter.task_finished.connect(functools.partial(self.remove_task, exporter))

        self.add_task(exporter)

        exporter.start()

    def on_task_finished(self, converted_data: MerData) -> None:
        self.task_finished.emit(converted_data)

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: MerData) -> MerData:
        if 'TACTICAL_SCENARIO' not in mer_data \
                or len(unique_refs) > mer_data['TACTICAL_SCENARIO'].original_df['REFERENCE'].nunique():

            confirm: QMessageBox = QMessageBox.warning(self.parent().view, 'Warning',
                                                       'No Tactical Scenario found, continue?',
                                                       QMessageBox.No | QMessageBox.Yes)
            if confirm == QMessageBox.Yes:
                return mock_tact_scenario(mer_data, unique_refs)
            else:
                raise NoTactScenarioFoundException

        return mer_data
