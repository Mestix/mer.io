import os
import sys
import threading
from typing import List, Generator, Union, Dict

from PyQt5.QtWidgets import QApplication
from pandas import DataFrame
import pandas as pd

from exceptions import NoTactScenarioFoundException
from models.dataframe_model import DataFrameModel
from models.mer_model import MerModel
from modules.convert_module import ConvertModule
from modules.import_module import ImportModule
from utility.utility import get_exception
from views.mer_view import MerView
from utility.formatters import format_degrees_to_coordinate_lat, format_degrees_to_coordinate_long


class MerController:
    def __init__(self):
        self.app: QApplication = QApplication(sys.argv)
        self.model: MerModel = MerModel()
        self.view: MerView = MerView()
        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None
        self.unconverted_data = dict()

        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.export_signal.connect(self.export)
        self.view.continue_without_tact_signal.connect(self.continue_without_tact)
        self.view.tree.selection_changed_signal.connect(self.select_df)
        self.view.exit_signal.connect(self.exit_program)

    def import_file(self, paths: List[str]) -> None:
        if self.model.has_mer():
            self.reset_mer()

        self.view.toggle_progress(True)

        self.importer = ImportModule(paths)
        self.importer.task_finished.connect(self.on_import_success)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.view.import_busy)

        self.model.names = ', '.join(map(os.path.basename, paths))
        self.start_task()

    def start_task(self) -> None:
        self.importer.start()

    def on_task_failed(self, txt) -> None:
        self.view.toggle_progress(False)
        self.view.import_failed(txt)

    def on_import_success(self, mer_data: Dict[str, DataFrameModel]) -> None:
        self.unconverted_data = mer_data
        try:
            self.model.set_tactical_scenario(mer_data)
            self.convert_data()
        except NoTactScenarioFoundException:
            self.view.import_no_tact()
        except Exception as e:
            print(get_exception(e))

    def convert_data(self):
        self.converter = ConvertModule(self.unconverted_data, self.model.tactical_scenario)
        self.converter.task_finished.connect(self.on_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.view.import_busy)
        self.converter.start()

    def on_convert_success(self, converted_data):
        self.model.init_mer(converted_data)
        self.set_mer_view()

    def continue_without_tact(self):
        self.model.mock_tact_scenario()
        self.convert_data()

    def set_mer_view(self):
        dfs = self.model.mer_data
        for name, idf in dfs.items():
            self.view.add_widget(idf)

        tactical_scenario_text = 'Tactical Scenario: Lat: {0}, Long: {1} '.format(
            format_degrees_to_coordinate_lat(self.model.tactical_scenario['tact_lat']),
            format_degrees_to_coordinate_long(self.model.tactical_scenario['tact_long']))

        self.view.import_success(tactical_scenario_text, self.model.names)

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
        self.model.reset_mer()
        self.view.reset_ui()
        self.view.tree.selection_changed_signal.connect(self.select_df)

    def select_df(self, name: str) -> None:
        df = self.model.get_df(name)
        self.model.selected_df = df
        self.view.stacked_dfs.setCurrentWidget(df.explorer)

    def exit_program(self) -> None:
        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()
