import sys
import threading
from typing import List, Generator

from PyQt5.QtWidgets import QApplication

from models.mer_model import MerModel, ImportState
from views.mer_view import MerView
from utility.converters import convert_degrees_to_coordinate_lat, convert_degrees_to_coordinate_long


class MerController:
    def __init__(self):
        self.app: QApplication = QApplication(sys.argv)
        self.model: MerModel = MerModel()
        self.view: MerView = MerView()
        self.init()

    def init(self) -> None:
        self.view.import_signal.connect(self.import_file)
        self.view.export_signal.connect(self.export)

        self.view.continue_without_tact_signal.connect(self.model.mock_tact_scenario)
        self.view.exit_signal.connect(self.exit_program)

        self.view.tree.selection_changed_signal.connect(self.select_df)

        self.model.import_signal.connect(self.handle_import_signal)
        self.model.no_tact_signal.connect(self.view.no_tact_dialog)

    def import_file(self, paths: List[str]) -> None:
        self.view.toggle_progress(True)

        if self.model.has_mer():
            self.reset_mer()
        self.model.import_from_paths(paths)

    def export(self, path: str) -> None:
        selected_items: Generator = self.view.tree.selected_items()
        if len(list(selected_items)) > 0:
            threading.Thread(target=self.model.export, args=(path, self.view.tree.selected_items())).start()
        else:
            self.view.error_dialog('Select at least 1 Identifier')

    def handle_import_signal(self, state: ImportState, txt: str) -> None:
        if state is ImportState.SUCCESS:
            self.import_success()
        elif state is ImportState.FAILED:
            self.reset_mer()
            self.view.error_dialog(txt)
            self.view.toggle_progress(False)
        else:
            self.view.import_busy_txt(txt)

    def reset_mer(self) -> None:
        self.model.reset_mer()
        self.view.reset_ui()
        self.view.tree.selection_changed_signal.connect(self.select_df)

    def select_df(self, name: str) -> None:
        df = self.model.get_df(name)
        self.model.selected_df = df
        self.view.stacked_dfs.setCurrentWidget(df.explorer)

    def import_success(self) -> None:
        dfs = self.model.mer_data
        for name, idf in dfs.items():
            from views.explorer_view import ExplorerView
            idf.explorer = ExplorerView(idf)

            self.view.stacked_dfs.addWidget(idf.explorer)
            self.view.tree.add_tree_item(name)

        tactical_scenario_text = 'Tactical Scenario: Lat: {0}, Long: {1} '.format(
            convert_degrees_to_coordinate_lat(self.model.tact_lat), convert_degrees_to_coordinate_long(self.model.tact_long))

        self.view.set_mer_info((tactical_scenario_text, self.model.names))
        self.view.enable_export_menu()
        self.view.toggle_progress(False)
        self.view.tree.show()

    def exit_program(self) -> None:
        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()


if __name__ == '__main__':
    controller = MerController()
    sys.exit(controller.run())
