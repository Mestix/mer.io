import sys
from typing import List

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet, QtStyleTools

from src.controllers.utility import remove_tempdir_contents
from src.handlers.bulk_handler import BulkHandler
from src.handlers.file_handler import FileHandler
from src.types import MerData
from src.utility import get_exception
from src.views.bulk_export_dlg import Settings
from src.views.mer_view import MerView


class MerController(QObject, QtStyleTools):
    def __init__(self):
        super().__init__()
        self.app: QApplication = QApplication(sys.argv)
        apply_stylesheet(self.app, theme='light_amber.xml', invert_secondary=True)

        # model
        self.mer_data: MerData = dict()

        # view
        self.view: MerView = MerView()

        # handlers
        self.bulk_handler: BulkHandler = BulkHandler(self)
        self.file_handler: FileHandler = FileHandler(self)

        self.init()

    def init(self) -> None:
        # connect signals to slots
        self.view.import_signal.connect(self.import_file)
        self.view.bulk_import_signal.connect(self.import_bulk)
        self.view.export_signal.connect(self.export)
        self.view.set_theme_signal.connect(self.set_theme)
        self.view.exit_signal.connect(self.exit_program)

        for handler in [self.file_handler, self.bulk_handler]:
            handler.task_busy.connect(self.view.task_busy)
            handler.task_failed.connect(self.on_task_failed)
            handler.task_finished.connect(self.on_task_finished)

        self.bulk_handler.task_finished.connect(self.on_bulk_success)
        self.file_handler.task_finished.connect(self.on_file_success)

    def import_file(self, paths: List[str]) -> None:
        # reset view and data before importing new Mer
        self.reset_mer()

        # set busy state
        self.view.toggle_progress(True)

        # start import
        self.file_handler.start_import(Settings(src=paths))

    def import_bulk(self, settings: Settings):
        # reset busy state
        self.view.toggle_import_menu(False)

        # start bulk import
        self.bulk_handler.start_import(settings)

    def export(self, path: str) -> None:
        self.file_handler.settings = Settings(dst=path)

        # get currently selected items from IdentifierListView
        selected_items: List[str] = list(self.view.identifiers.selected_items())
        if len(selected_items) > 0:
            # subset MerData to get only selected dataframes
            data = {key: value for key, value in self.mer_data.items() if key in selected_items}

            # start exporting selected dataframes
            self.file_handler.start_export(data)
        else:
            # notify user to select at least 1 dataframe
            self.view.import_failed('Select at least 1 Identifier')

    def on_task_failed(self, txt) -> None:
        # reset view and data
        self.reset_mer()

        # reset busy state
        self.view.toggle_progress(False)

        # notify user from failure
        self.view.import_failed(txt)

    def on_task_finished(self):
        self.view.task_busy('Task success')

    def on_file_success(self, converted_data: MerData) -> None:
        # enable menu's when all tasks are finished
        if self.file_handler.all_tasks_finished():
            self.view.toggle_import_menu(True)

        # set model
        self.mer_data = converted_data

        # initiate view with mer data
        self.set_mer_view(converted_data)

    def on_bulk_success(self):
        # enable menu's when all tasks are finished
        if self.bulk_handler.all_tasks_finished():
            self.view.toggle_import_menu(True)

    def set_mer_view(self, converted_data: MerData) -> None:
        # for every dataframe model in mer data, add widget to stacked widget in view
        for name, idf in self.mer_data.items():
            self.view.add_widget(idf)

        tact_scenario_txt = 'Tactical Scenarios:'

        # get all tactical scenario's from importer mers, for showing in view
        for index, row in converted_data['TACTICAL_SCENARIO'].original_df.iterrows():
            tact_scenario_txt += \
                ' {0}: Lat {1}, Long {2}'.format(
                    row['REFERENCE'],
                    row['GRID CENTER LAT'],
                    row['GRID CENTER LONG']
                )

        self.view.import_success(tact_scenario_txt)

    def reset_mer(self) -> None:
        # reset view and data
        if bool(self.mer_data):
            self.mer_data: MerData = dict()
            self.view.reset_ui()

    def set_theme(self, theme: str):
        # set theme. When setting a light theme, the colors should be inverted
        invert: bool = theme.startswith('light')
        apply_stylesheet(self.app, theme=theme, invert_secondary=invert)

    def exit_program(self) -> None:
        # empty temporary files on clean exit
        try:
            remove_tempdir_contents()
        except Exception as E:
            print(get_exception(E))

        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()
