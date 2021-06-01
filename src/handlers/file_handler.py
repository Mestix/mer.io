from typing import Dict, List, Union

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.exceptions import NoTactScenarioFoundException
from src.handlers.utility import mock_tact_scenario
from src.handlers.handler_base import HandlerBase
from src.tasks.convert_task import ConvertTask
from src.tasks.export_task import ExportTask
from src.tasks.import_task import ImportTask

from src.log import get_logger
from src.types import MerData
from src.views.bulk_export_dlg import Settings


class FileHandler(HandlerBase):
    task_finished: pyqtSignal = pyqtSignal(object)

    logger = get_logger(__name__)

    def __init__(self, parent):
        super().__init__(parent)
        self.settings: Union[Settings, None] = None

    def start_import(self, settings: Settings):
        # init task
        importer: ImportTask = ImportTask(settings.src)
        importer.task_failed.connect(self.on_task_failed)
        importer.task_busy.connect(self.on_task_busy)
        importer.task_finished.connect(lambda x:  [self.start_convert(x), self.remove_task(importer)])
        self.add_task(importer)

        # start task
        importer.start()

    def start_convert(self, _import: Dict) -> None:
        mer_data: MerData

        try:
            # verify if all imported Mers have a tactical scenario or else raise Exception
            mer_data: MerData = self.verify_tact_scenarios(
                _import['unique_refs'],
                _import['mer_data']
            )
        except NoTactScenarioFoundException:
            self.task_failed.emit('Import Failed')
            return

        # init task
        converter: ConvertTask = ConvertTask(mer_data)
        converter.task_failed.connect(self.on_task_failed)
        converter.task_busy.connect(self.on_task_busy)
        converter.task_finished.connect(lambda x: [self.on_task_finished(x), self.remove_task(converter)])
        self.add_task(converter)

        # start task
        converter.start()

    def start_export(self, data: MerData):
        # init task
        exporter: ExportTask = ExportTask(data, self.settings.dst)
        exporter.task_failed.connect(self.on_task_failed)
        exporter.task_busy.connect(self.on_task_busy)
        exporter.task_finished.connect(lambda x: self.remove_task(exporter))
        self.add_task(exporter)

        # start task
        exporter.start()

    def on_task_finished(self, converted_data: MerData) -> None:
        self.task_finished.emit(converted_data)

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: MerData) -> MerData:
        """
        Check if there is the amount of tactical scenarios is equal to the unique references in the data.
        If not, tactical scenario(s) is/are missing
        """
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
