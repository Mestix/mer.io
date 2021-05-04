import sys
import threading
from typing import List, Generator, Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from pandas import DataFrame
import pandas as pd

from src.importers.bulk_importer import BulkImporter
from src.importers.mer_importer import MerImporter
from src.models.dataframe_model import DataFrameModel
from src.models.mer_model import MerModel
from src.utility.utility import get_exception, get_files_from_folder
from src.views.bulk_export_dlg import BulkSettings
from src.views.mer_view import MerView


class MerController(QObject):
    def __init__(self):
        super().__init__()
        self.app: QApplication = QApplication(sys.argv)
        self.model: MerModel = MerModel()
        self.view: MerView = MerView()

        self.bulk_importer: BulkImporter = BulkImporter()
        self.mer_importer: MerImporter = MerImporter(parent=self)

        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.bulk_import_signal.connect(self.import_bulk)

        self.view.export_signal.connect(self.export)
        self.view.tree.selection_changed_signal.connect(self.select_df)
        self.view.exit_signal.connect(self.exit_program)

        self.bulk_importer.import_busy.connect(self.view.import_busy)
        self.bulk_importer.import_failed.connect(self.on_task_failed)

        self.mer_importer.task_busy.connect(self.view.import_busy)
        self.mer_importer.task_failed.connect(self.on_task_failed)
        self.mer_importer.task_finished.connect(self.on_task_success)

    def import_file(self, paths: List[str]) -> None:
        self.reset_mer()

        self.view.toggle_progress(True)
        self.mer_importer.import_and_convert(paths)

    def import_bulk(self, info: BulkSettings):
        self.bulk_importer.import_and_convert(list(get_files_from_folder(info.src)), info)

    def on_task_failed(self, txt) -> None:
        self.reset_mer()

        self.view.toggle_progress(False)
        self.view.import_failed(txt)

    def on_task_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.model.mer_data = converted_data
        try:
            self.set_mer_view(converted_data)
        except Exception as e:
            print('MerController.on_convert_success: ' + get_exception(e))

    def set_mer_view(self, converted_data: Dict[str, DataFrameModel]) -> None:
        for name, idf in self.model.mer_data.items():
            self.view.add_widget(idf)

        tact_scenario_txt = 'Tactical Scenarios:'

        for index, row in converted_data['TACTICAL_SCENARIO'].df_unfiltered.iterrows():
            tact_scenario_txt += \
                ' {0}: Lat {1}, Long {2}'.format(
                    row['REFERENCE'],
                    row['GRID CENTER LAT'],
                    row['GRID CENTER LAT']
                )

        self.view.import_success(tact_scenario_txt)

    def export(self, path: str) -> None:
        selected_items: Generator = self.view.tree.selected_items()
        if len(list(selected_items)) > 0:
            threading.Thread(target=self.export_to_xls, args=(path, self.view.tree.selected_items())).start()
        else:
            self.view.import_failed('Select at least 1 Identifier')

    def export_to_xls(self, path: str, selected_items: Generator) -> None:
        writer: pd.ExcelWriter = pd.ExcelWriter(path)

        for name in selected_items:
            df: DataFrame = self.model.get_df(name).df
            df.to_excel(writer, name)

        writer.save()

    def reset_mer(self) -> None:
        if self.model.has_mer():
            self.model.reset_mer()
            self.view.reset_ui()
            self.view.tree.selection_changed_signal.connect(self.select_df)

    def select_df(self, name: str) -> None:
        df: DataFrameModel = self.model.select_df(name)
        self.view.stacked_dfs.setCurrentWidget(df.explorer)

    def exit_program(self) -> None:
        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()
