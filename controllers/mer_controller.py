import sys

from PyQt5.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem

from models.mer_model import MerModel
from views.mer_view import MerView
from utility.converters import convert_degrees_to_coordinate_lat, convert_degrees_to_coordinate_long
from utility.utility import get_exception


class MerController:
    def __init__(self):
        self.app: QApplication = QApplication(sys.argv)
        self.model: MerModel = MerModel()
        self.view: MerView = MerView()
        self.init()

    def init(self):
        self.view.tree.selection_changed_signal.connect(self.select_df)
        self.view.import_signal.connect(self.import_file)
        self.view.confirmed_yes_signal.connect(self.model.mock_tact_scenario)
        self.view.exit_signal.connect(self.exit_program)

        self.model.mer_set_signal.connect(self.set_dfs)
        self.model.progress_signal.connect(self.view.toggle_progress)
        self.model.confirm_signal.connect(self.view.show_confirm_dialog)
        self.model.yesno_signal.connect(self.view.show_yesno_dialog)
        self.model.import_busy_signal.connect(self.view.set_progress_text)

    def import_file(self):
        self.reset_mer()

        dialog = QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter='*.txt *.zip', directory='test_mers')

        if len(paths) > 0:
            try:
                self.model.import_from_paths(paths)
                self.view.background_label.hide()
            except Exception as e:
                self.view.show_confirm_dialog('Something went wrong')
                print(get_exception(e))
        else:
            pass

    def reset_mer(self):
        self.model.reset_mer()
        self.view.reset_ui()
        self.view.tree.selection_changed_signal.connect(self.select_df)

    def select_df(self, name):
        df = self.model.get_df(name)
        self.view.stacked_dfs.setCurrentWidget(df.explorer)

    def set_dfs(self):
        dfs = self.model.mer_data
        for name, idf in dfs.items():
            if idf.explorer is None:
                from views.explorer_view import ExplorerView
                idf.explorer = ExplorerView(idf)

            self.view.stacked_dfs.addWidget(idf.explorer)

            shape = idf.df.shape
            self.view.tree.addTopLevelItem(QTreeWidgetItem([name, str(shape[1]), str(shape[0])]))
            self.view.tree.setCurrentItem(self.view.tree.topLevelItem(0))
            self.view.tree.itemSelectionChanged.emit()

        self.view.tree.show()

        tactical_scenario_text = 'Tactical Scenario: Lat: {0}, Long: {1} '.format(
            convert_degrees_to_coordinate_lat(self.model.tact_lat), convert_degrees_to_coordinate_long(self.model.tact_long))

        self.view.set_mer_info((tactical_scenario_text, self.model.names))

    def exit_program(self):
        self.app.exit()

    def run(self):
        self.view.show()
        return self.app.exec_()


if __name__ == '__main__':
    controller = MerController()
    sys.exit(controller.run())
