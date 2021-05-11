from typing import Union, Dict, List

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.exceptions import NoTactScenarioFoundException
from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule
from src.modules.import_module import ImportModule

from src.log import get_logger
from src.utility.dataframemodel_operations import mock_tact_scenario


class FileHandler(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal(object)

    logger = get_logger(__name__)
    importer: ImportModule
    converter: ConvertModule
    exporter: ExportModule

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def start_import(self, paths):
        self.importer: ImportModule = ImportModule(paths)
        self.importer.task_finished.connect(self.start_convert)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.on_task_busy)

        self.importer.start()

    def start_convert(self, _import: Dict) -> None:
        try:
            data: Dict[str, DataFrameModel] = self.verify_tact_scenarios(_import['unique_refs'], _import['mer_data'])

            self.converter = ConvertModule(data)
            self.converter.task_finished.connect(self.on_convert_success)
            self.converter.task_failed.connect(self.on_task_failed)
            self.converter.task_busy.connect(self.on_task_busy)
            self.converter.start()
        except NoTactScenarioFoundException:
            self.task_failed.emit('Import Failed')

    def start_export(self, data: Dict[str, DataFrameModel], dst: str):
        self.exporter: ExportModule = ExportModule(data, dst)
        self.exporter.task_busy.connect(self.on_task_busy)
        self.exporter.task_failed.connect(self.on_task_failed)
        self.exporter.start()

    def on_convert_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.task_finished.emit(converted_data)

    def on_task_busy(self, txt):
        self.task_busy.emit(txt)

    def on_task_failed(self, txt):
        self.task_failed.emit(txt)

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: Dict[str, DataFrameModel]) -> Dict[str, DataFrameModel]:
        if 'TACTICAL_SCENARIO' not in mer_data \
                or len(unique_refs) > mer_data['TACTICAL_SCENARIO'].df_unfiltered['REFERENCE'].nunique():

            confirm: QMessageBox = QMessageBox.warning(self.parent.view, 'Warning',
                                                       'No Tactical Scenario found, continue?',
                                                       QMessageBox.No | QMessageBox.Yes)
            if confirm == QMessageBox.Yes:
                return mock_tact_scenario(mer_data, unique_refs)
            else:
                raise NoTactScenarioFoundException

        return mer_data
