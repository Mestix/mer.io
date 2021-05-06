import sys
from typing import List, Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet, QtStyleTools

from src.handlers.bulk_handler import BulkHandler
from src.handlers.file_handler import FileHandler
from src.models.dataframe_model import DataFrameModel
from src.models.mer_model import MerModel
from src.views.bulk_export_dlg import BulkSettings
from src.views.mer_view import MerView


class MerController(QObject, QtStyleTools):
    def __init__(self):
        super().__init__()
        self.app: QApplication = QApplication(sys.argv)
        apply_stylesheet(self.app, theme='light_amber.xml', invert_secondary=True)
        self.model: MerModel = MerModel()

        self.view: MerView = MerView()

        self.bulk_handler: BulkHandler = BulkHandler()
        self.file_handler: FileHandler = FileHandler(parent=self)

        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.bulk_import_signal.connect(self.import_bulk)

        self.view.export_signal.connect(self.export)
        self.view.identifiers.selection_changed_signal.connect(self.select_df)
        self.view.exit_signal.connect(self.exit_program)
        self.view.set_theme_signal.connect(self.set_theme)

        self.bulk_handler.task_busy.connect(self.view.import_busy)
        self.bulk_handler.task_failed.connect(self.on_task_failed)
        self.bulk_handler.task_finished.connect(self.on_task_finished)

        self.file_handler.task_busy.connect(self.view.import_busy)
        self.file_handler.task_finished.connect(self.on_import_success)
        self.file_handler.task_failed.connect(self.on_task_failed)

    def import_file(self, paths: List[str]) -> None:
        self.reset_mer()

        self.view.toggle_progress(True)
        self.file_handler.start_import(paths)

    def import_bulk(self, info: BulkSettings):
        self.view.toggle_import_menu(False)

        self.bulk_handler.start_import(info)

    def export(self, path: str) -> None:
        selected_items: List[str] = list(self.view.identifiers.selected_items())
        if len(selected_items) > 0:
            data = dict()
            for name in selected_items:
                dfm = self.model.get_df(name)
                data[name] = dfm

            self.file_handler.start_export(data, path)
        else:
            self.view.import_failed('Select at least 1 Identifier')

    def on_task_failed(self, txt) -> None:
        self.reset_mer()

        self.view.toggle_progress(False)
        self.view.import_failed(txt)

    def on_import_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.model.mer_data = converted_data
        self.set_mer_view(converted_data)

    def on_task_finished(self):
        self.view.toggle_import_menu(True)

    def set_mer_view(self, converted_data: Dict[str, DataFrameModel]) -> None:
        for name, idf in self.model.mer_data.items():
            self.view.add_widget(idf)

        tact_scenario_txt = 'Tactical Scenarios:'

        for index, row in converted_data['TACTICAL_SCENARIO'].df_unfiltered.iterrows():
            tact_scenario_txt += \
                ' {0}: Lat {1}, Long {2}'.format(
                    row['REFERENCE'],
                    row['GRID CENTER LAT'],
                    row['GRID CENTER LONG']
                )

        self.view.import_success(tact_scenario_txt)

    def reset_mer(self) -> None:
        if self.model.has_mer():
            self.model.reset_mer()
            self.view.reset_ui()
            self.view.identifiers.selection_changed_signal.connect(self.select_df)

    def select_df(self, name: str) -> None:
        df: DataFrameModel = self.model.select_df(name)
        self.view.stacked_dfs.setCurrentWidget(df.explorer)

    def set_theme(self, theme: str):
        invert: bool = theme.startswith('light')
        apply_stylesheet(self.app, theme=theme + '.xml', invert_secondary=invert)

    def exit_program(self) -> None:
        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()
