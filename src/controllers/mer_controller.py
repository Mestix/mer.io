import sys
from typing import List, Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet, QtStyleTools

from src.controllers.utility import remove_tempdir_contents
from src.handlers.bulk_handler import BulkHandler
from src.handlers.file_handler import FileHandler
from src.models.dataframe_model import DataFrameModel
from src.utility import get_exception
from src.views.bulk_export_dlg import BulkSettings
from src.views.mer_view import MerView


class MerController(QObject, QtStyleTools):
    def __init__(self):
        super().__init__()
        self.app: QApplication = QApplication(sys.argv)
        apply_stylesheet(self.app, theme='light_amber.xml', invert_secondary=True)

        self.mer_data: Dict[str, DataFrameModel] = dict()

        self.view: MerView = MerView()

        self.bulk_handler: BulkHandler = BulkHandler()
        self.file_handler: FileHandler = FileHandler(self)

        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.bulk_import_signal.connect(self.import_bulk)
        self.view.export_signal.connect(self.export)

        self.view.set_theme_signal.connect(self.set_theme)

        self.view.exit_signal.connect(self.exit_program)

        self.bulk_handler.task_busy.connect(self.view.task_busy)
        self.bulk_handler.task_failed.connect(self.on_task_failed)
        self.bulk_handler.task_finished.connect(self.on_bulk_success)
        self.bulk_handler.task_finished.connect(self.on_task_finished)

        self.file_handler.task_busy.connect(self.view.task_busy)
        self.file_handler.task_failed.connect(self.on_task_failed)
        self.file_handler.task_finished.connect(self.on_file_success)
        self.file_handler.task_finished.connect(self.on_task_finished)

    def import_file(self, paths: List[str]) -> None:
        self.reset_mer()

        self.view.toggle_progress(True)
        self.file_handler.start_import(BulkSettings(src=paths))

    def import_bulk(self, settings: BulkSettings):
        self.view.toggle_import_menu(False)

        self.bulk_handler.start_import(settings)

    def export(self, path: str) -> None:
        selected_items: List[str] = list(self.view.identifiers.selected_items())
        if len(selected_items) > 0:
            data = {key: value for key, value in self.mer_data.items() if key in selected_items}

            self.file_handler.start_export(data, path)
        else:
            self.view.import_failed('Select at least 1 Identifier')

    def on_task_failed(self, txt) -> None:
        self.reset_mer()

        self.view.toggle_progress(False)
        self.view.import_failed(txt)

    def on_task_finished(self):
        self.view.task_busy('Task success')

    def on_file_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.mer_data = converted_data
        self.set_mer_view(converted_data)

    def on_bulk_success(self):
        if self.bulk_handler.all_tasks_finished():
            self.view.toggle_import_menu(True)

    def set_mer_view(self, converted_data: Dict[str, DataFrameModel]) -> None:
        for name, idf in self.mer_data.items():
            self.view.add_widget(idf)

        tact_scenario_txt = 'Tactical Scenarios:'

        for index, row in converted_data['TACTICAL_SCENARIO'].original_df.iterrows():
            tact_scenario_txt += \
                ' {0}: Lat {1}, Long {2}'.format(
                    row['REFERENCE'],
                    row['GRID CENTER LAT'],
                    row['GRID CENTER LONG']
                )

        self.view.import_success(tact_scenario_txt)

    def reset_mer(self) -> None:
        if bool(self.mer_data):
            self.mer_data: Dict[str, DataFrameModel] = dict()
            self.view.reset_ui()

    def set_theme(self, theme: str):
        invert: bool = theme.startswith('light')
        apply_stylesheet(self.app, theme=theme.replace(' ', '_') + '.xml', invert_secondary=invert)

    def exit_program(self) -> None:
        try:
            remove_tempdir_contents()
        except Exception as E:
            print(get_exception(E))

        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()
