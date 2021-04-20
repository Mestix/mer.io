import sys
from typing import List

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
        self.view.export_single_signal.connect(self.export_single_df)

        self.view.continue_without_tact_signal.connect(self.model.mock_tact_scenario)
        self.view.exit_signal.connect(self.exit_program)

        self.view.tree.selection_changed_signal.connect(self.select_df)

        self.model.progress_signal.connect(self.view.toggle_progress)
        self.model.import_signal.connect(self.handle_import_signal)
        self.model.no_tact_signal.connect(self.view.no_tact_dialog)

    def import_file(self, paths: List[str]) -> None:
        if self.model.has_mer():
            self.reset_mer()
        self.model.import_from_paths(paths)

    def export_single_df(self, path: str) -> None:
        self.model.export_single_df(path)

    def handle_import_signal(self, state: ImportState, txt: str) -> None:
        if state is ImportState.SUCCESS:
            self.import_success()
        elif state is ImportState.FAILED:
            self.view.import_failed_dialog(txt)
        else:
            self.view.set_progress_text(txt)

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
            self.view.stacked_dfs.addWidget(idf.explorer)
            self.view.tree.add_tree_item(name, idf.df.shape)

        tactical_scenario_text = 'Tactical Scenario: Lat: {0}, Long: {1} '.format(
            convert_degrees_to_coordinate_lat(self.model.tact_lat), convert_degrees_to_coordinate_long(self.model.tact_long))

        self.view.set_mer_info((tactical_scenario_text, self.model.names))
        self.view.enable_export_menu()
        self.view.tree.show()

    def exit_program(self) -> None:
        self.app.exit()

    def run(self) -> int:
        self.view.show()
        return self.app.exec_()


if __name__ == '__main__':
    controller = MerController()
    sys.exit(controller.run())
