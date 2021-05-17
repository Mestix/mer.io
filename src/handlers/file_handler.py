from typing import Dict, List, Union

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.exceptions import NoTactScenarioFoundException
from src.handlers.utility import mock_tact_scenario
from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule
from src.modules.import_module import ImportModule

from src.log import get_logger


class FileHandler(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal(object)

    logger = get_logger(__name__)

    def __init__(self, parent):
        super().__init__(parent)

        self.tasks: List[Union[ImportModule, ConvertModule, ExportModule]] = list()

    def start_import(self, paths):
        importer: ImportModule = ImportModule(paths)
        importer.task_finished.connect(self.start_convert)
        importer.task_failed.connect(self.on_task_failed)
        importer.task_busy.connect(self.on_task_busy)

        self.tasks.append(importer)

        importer.start()

    def start_convert(self, _import: Dict) -> None:
        mer_data: Dict[str, DataFrameModel]
        try:
            mer_data: Dict[str, DataFrameModel] = self.verify_tact_scenarios(_import['unique_refs'], _import['mer_data'])
        except NoTactScenarioFoundException:
            self.task_failed.emit('Import Failed')
            return

        converter: ConvertModule = ConvertModule(mer_data)
        converter.task_finished.connect(self.on_convert_success)
        converter.task_failed.connect(self.on_task_failed)
        converter.task_busy.connect(self.on_task_busy)

        self.tasks.append(converter)

        converter.start()

    def start_export(self, data: Dict[str, DataFrameModel], dst: str):
        exporter: ExportModule = ExportModule(data, dst)

        exporter.task_failed.connect(self.on_task_failed)
        exporter.task_busy.connect(self.on_task_busy)

        self.tasks.append(exporter)

        exporter.start()

    def on_convert_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.task_finished.emit(converted_data)

    def on_task_busy(self, txt):
        self.task_busy.emit(txt)

    def on_task_failed(self, txt):
        self.task_failed.emit(txt)

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: Dict[str, DataFrameModel]) -> Dict[str, DataFrameModel]:
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
