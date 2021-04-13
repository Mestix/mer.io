import sys
from dataclasses import dataclass
from typing import Callable, Union
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QMessageBox, QDialog, QProgressBar, QStatusBar, QStackedWidget, QWidget, \
    QApplication, QSplitter, QAction

from mer_keeper import MerKeeper
from widgets.mer_tree import MerTree


class MerGui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        super().__init__(*args, **kwargs)

        self.splitter: Union[QSplitter, None] = None
        self.stacked_dfs: Union[QStackedWidget, None] = None
        self.tree: Union[MerTree, None] = None

        self.status_bar: Union[QStatusBar, None] = None
        self.status_bar_filename: Union[QWidget, None] = None
        self.status_bar_tactical_scenario: Union[QWidget, None] = None

        self.progress_bar: Union[QProgressBar, None] = None
        self.progress_window: Union[QDialog, None] = None
        self.progress_window_label: Union[str, None] = None

        self.mer_keeper = MerKeeper()
        self.mer_keeper.gui = self

        self.init_ui()

        self.show()
        self.app.exec_()

    def init_ui(self):
        self.splitter = QSplitter(self)
        self.tree = MerTree(self.mer_keeper)
        self.stacked_dfs = QStackedWidget()
        self.status_bar = self.statusBar()

        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.stacked_dfs)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        nav_width = self.tree.sizeHint().width()
        self.splitter.setSizes([nav_width, self.width() - nav_width])
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.splitter)

        self.create_menu_bar()
        self.create_progress_window()

        self.setGeometry(250, 150, 1500, 750)
        self.setWindowTitle('MER.io')
        self.setWindowIcon(QIcon('assets/copter_icon.png'))

    def reset_ui(self):
        self.tree = MerTree(self.mer_keeper)
        self.stacked_dfs = QStackedWidget()
        self.status_bar = self.statusBar()

        self.progress_window_label.setText('')
        self.progress_window_label.adjustSize()
        self.set_status_bar_right_widget('')
        self.set_status_bar_left_widget('')

        self.splitter.replaceWidget(0, self.tree)
        self.splitter.replaceWidget(1, self.stacked_dfs)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menus = {}

        @dataclass
        class MenuItem:
            name: str
            func: Callable
            shortcut: str = ''

        menu_bar_items = {"File": [MenuItem(name='Import',
                                            func=self.open_import_dialog,
                                            shortcut='Ctrl+O'),
                                   MenuItem(name='Exit',
                                            func=self.exit_program,
                                            shortcut='Ctrl+Q')]}

        for name in menu_bar_items:
            menu = menu_bar.addMenu(name)
            menus[name] = menu

            for item in menu_bar_items[name]:
                action = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                action.triggered.connect(item.func)
                menu.addAction(action)

    def create_progress_window(self):
        self.progress_window: QDialog = QDialog()
        self.progress_window.setWindowModality(Qt.ApplicationModal)
        self.progress_bar: QProgressBar = QProgressBar(self.progress_window)
        self.progress_window.resize(400, 100)
        self.progress_window.setFixedSize(self.progress_window.size())
        self.progress_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.progress_window.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.progress_window.setWindowTitle('Please wait')
        self.progress_window_label = QLabel(self.progress_window)
        self.progress_window_label.move(15, 18)
        self.progress_bar.resize(410, 25)
        self.progress_bar.move(15, 40)
        self.progress_bar.setRange(0, 0)

    def hide_progress_bar(self):
        self.progress_window.hide()

    def show_progress_bar(self):
        self.progress_window.show()

    def set_status_bar_left_widget(self, text):
        if self.status_bar_tactical_scenario is not None:
            self.status_bar.removeWidget(self.status_bar_tactical_scenario)

        self.status_bar_tactical_scenario = QLabel(text)
        self.status_bar.addPermanentWidget(self.status_bar_tactical_scenario)

    def set_status_bar_right_widget(self, text):
        if self.status_bar_filename is not None:
            self.status_bar.removeWidget(self.status_bar_filename)

        self.status_bar_filename = QLabel(text)
        self.status_bar.addWidget(self.status_bar_filename)

    def open_import_dialog(self):
        dialog = QtWidgets.QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter='*.txt *.zip', directory='test_mers')

        if len(paths) > 0:
            self.mer_keeper.import_from_paths(paths)
        else:
            pass

    def exit_program(self):
        confirm = QMessageBox.question(self, 'Warning', 'Close program?',
                                       QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.app.exit()
        else:
            return


if __name__ == "__main__":
    window = MerGui()
