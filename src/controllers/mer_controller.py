import sys
import threading
from typing import List, Generator, Union, Dict

from PyQt5.QtWidgets import QApplication, QMessageBox
from pandas import DataFrame
import pandas as pd

from src.models.dataframe_model import DataFrameModel
from src.models.mer_model import MerModel
from src.modules.convert_module import ConvertModule
from src.modules.import_module import ImportModule
from src.utility.utility import get_exception, get_files_from_folder
from src.views.bulk_export_dlg import BulkSettings
from src.views.mer_view import MerView


class MerController:
    def __init__(self):
        self.app: QApplication = QApplication(sys.argv)
        self.model: MerModel = MerModel()
        self.view: MerView = MerView()

        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None

        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.bulk_import_signal.connect(self.import_bulk)
        self.view.export_signal.connect(self.export)
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

        self.start_task()

    def import_bulk(self, info: BulkSettings):
        paths = list(get_files_from_folder(info.src))
        self.info = info

        self.importer = ImportModule(paths, info.skip)
        self.importer.task_finished.connect(self.on_bulk_import_success)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.view.import_busy)

        self.start_task()

    def on_bulk_import_success(self, _import: Dict):
        print('bulk success')
        mer_data: Dict[str, DataFrameModel] = _import['mer_data']

        if not self.info.skip:
            mock_tact_scenario(mer_data, _import['unique_refs'])

        self.converter = ConvertModule(mer_data)
        self.converter.task_finished.connect(self.on_bulk_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.view.import_busy)
        self.converter.start()

    def on_bulk_convert_success(self, mer_data: Dict):
        print('convert success')
        try:
            writer: pd.ExcelWriter = pd.ExcelWriter(self.info.dst)

            dfm: DataFrameModel
            for key, dfm in mer_data.items():
                dfm.df.to_excel(writer, dfm.name)

            writer.save()
        except Exception as e:
            print(get_exception(e))

    def start_task(self) -> None:
        self.importer.start()

    def on_task_failed(self, txt) -> None:
        self.view.toggle_progress(False)
        self.view.import_failed(txt)

    def on_import_success(self, _import: Dict) -> None:
        self.model.mer_data = _import['mer_data']

        _continue = self.verify_tact_scenarios(_import['unique_refs'], _import['mer_data'])

        self.convert_data() if _continue else self.reset_mer()

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: Dict[str, DataFrameModel]) -> bool:
        if 'TACTICAL_SCENARIO' not in mer_data \
                or len(unique_refs) > mer_data['TACTICAL_SCENARIO'].df_unfiltered['REFERENCE'].nunique():

            confirm: QMessageBox = QMessageBox.warning(self.view, 'Warning',
                                                       'No Tactical Scenario found, continue?',
                                                       QMessageBox.No | QMessageBox.Yes)
            if confirm == QMessageBox.Yes:
                try:
                    self.model.mer_data = mock_tact_scenario(mer_data, unique_refs)
                except Exception as e:
                    print(get_exception(e))
                return True
            else:
                return False
        return True

    def convert_data(self) -> None:
        self.converter = ConvertModule(self.model.mer_data)
        self.converter.task_finished.connect(self.on_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.view.import_busy)
        self.converter.start()

    def on_convert_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
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


def mock_tact_scenario(mer_data: Dict[str, DataFrameModel], unique_refs: List[str]) -> Dict[str, DataFrameModel]:
    if 'TACTICAL_SCENARIO' not in mer_data:
        mer_data['TACTICAL_SCENARIO'] = DataFrameModel(DataFrame({'REFERENCE': []}), 'TACTICAL_SCENARIO')
    for ref in unique_refs:
        tact_scenario: DataFrame = mer_data['TACTICAL_SCENARIO'].df_unfiltered
        if ref not in list(tact_scenario['REFERENCE'].unique()):
            mer_data['TACTICAL_SCENARIO'].df_unfiltered = \
                mer_data['TACTICAL_SCENARIO'].df_unfiltered.append(
                    pd.DataFrame({
                        'GRID CENTER LAT': [0],
                        'GRID CENTER LONG': [0],
                        'REFERENCE': [ref]
                    }), ignore_index=True)

    return mer_data
