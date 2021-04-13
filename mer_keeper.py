import os
from typing import Union, Dict

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from pandas import DataFrame

from modules.import_module import ImportModule

from models.dataframe_model import DataFrameModel
from utility.converters import convert_degrees_to_coordinate_lat, convert_degrees_to_coordinate_long
from utility.extractors import extract_identifiers, extract_tactical_scenario
from utility.utility import get_exception
from widgets.mer_tree import MerTree


class MerKeeper:
    def __init__(self):
        self.mer_data: Dict[str, DataFrameModel] = {}
        self.mer_df: Union[DataFrame, None] = None
        self.gui: Union['MerGui', None] = None
        self.tree: Union[MerTree, None] = None

        self.tact_lat: Union[float, None] = None
        self.tact_long: Union[float, None] = None
        self.names: Union[str, None] = None

        self.import_task: Union[ImportModule, None] = None

    def init_mer(self, df: DataFrame) -> None:
        try:
            self.tact_lat, self.tact_long = extract_tactical_scenario(df)
        except IndexError:
            confirm = QMessageBox.warning(self.gui, 'Warning', 'No Tactical Scenario found, do you want to proceed?',
                                          QMessageBox.No | QMessageBox.Yes)
            if confirm == QMessageBox.Yes:
                self.tact_lat = 0
                self.tact_long = 0
            else:
                return

        self.mer_df = df
        self.set_mer_data()
        self.set_mer_info()

    def set_mer_data(self) -> None:
        grouped_by_identifier = extract_identifiers(self.mer_df)

        for name, idf in grouped_by_identifier.items():
            idf = DataFrameModel(idf.copy(), name)
            self.mer_data[name] = idf

            if idf.explorer is None:
                from widgets.mer_explorer import MerExplorer
                idf.explorer = MerExplorer(idf)

            self.gui.stacked_dfs.addWidget(idf.explorer)

            shape = idf.df.shape
            self.tree.addTopLevelItem(QTreeWidgetItem([name, str(shape[1]), str(shape[0])]))
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
            self.tree.itemSelectionChanged.emit()

    def on_task_busy(self, text) -> None:
        self.gui.progress_window_label.setText(text)
        self.gui.progress_window_label.adjustSize()

    def start_task(self) -> None:
        self.reset_mer()
        self.gui.show_progress_bar()
        self.import_task.start()

    def on_task_finished(self, df) -> None:
        self.gui.hide_progress_bar()
        try:
            self.init_mer(df)
        except Exception as e:
            print(get_exception(e))

    def on_task_failed(self) -> None:
        self.gui.hide_progress_bar()
        QMessageBox.warning(self.gui, 'Error', 'No valid MER files found',
                                      QMessageBox.Ok)

    def import_from_paths(self, paths) -> None:
        self.names = ', '.join(map(os.path.basename, paths))
        self.import_task = ImportModule(paths)
        self.import_task.task_finished.connect(self.on_task_finished)
        self.import_task.task_failed.connect(self.on_task_failed)
        self.import_task.task_busy.connect(self.on_task_busy)
        self.start_task()

    def set_mer_info(self) -> None:
        tactical_scenario_text = 'Tactical Scenario: Lat: {0}, Long: {1} '.format(
            convert_degrees_to_coordinate_lat(self.tact_lat), convert_degrees_to_coordinate_long(self.tact_long))
        self.gui.set_status_bar_right_widget(tactical_scenario_text)
        self.gui.set_status_bar_left_widget(self.names)

    def select_df(self, name) -> None:
        df = self.get_df(name)
        self.gui.stacked_dfs.setCurrentWidget(df.explorer)

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        self.gui.reset_ui()
        self.mer_data = {}

