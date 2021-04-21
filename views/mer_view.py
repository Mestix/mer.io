from dataclasses import dataclass
from typing import Union, List, Dict, Tuple

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QLabel, QStatusBar, QWidget, \
    QProgressBar, QDialog, QMainWindow, QAction, QMessageBox, QFileDialog, QMenuBar, QMenu

from utility.utility import get_exception, get_path
from views.tree_view import TreeView


class MerView(QMainWindow):
    import_signal: pyqtSignal = pyqtSignal(list)
    export_signal: pyqtSignal = pyqtSignal(str)
    continue_without_tact_signal: pyqtSignal = pyqtSignal()
    exit_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.splitter: Union[QSplitter, None] = None
        self.stacked_dfs: Union[QStackedWidget, None] = None
        self.tree: Union[TreeView, None] = None

        self.status_bar: Union[QStatusBar, None] = None
        self.status_bar_filename: Union[QWidget, None] = None
        self.status_bar_tactical_scenario: Union[QWidget, None] = None

        self.progress_bar: Union[QProgressBar, None] = None
        self.progress_window: Union[QDialog, None] = None
        self.progress_window_label: Union[QLabel, None] = None

        self.init_ui()

    def init_ui(self):
        self.splitter: QSplitter = QSplitter(self)
        self.tree: TreeView = TreeView()

        self.stacked_dfs: QStackedWidget = QStackedWidget()

        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.stacked_dfs)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.status_bar: QStatusBar = self.statusBar()

        self.splitter.setSizes([300, 1000])
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.splitter)

        self.create_menu_bar()
        self.create_progress_window()

        self.setGeometry(250, 150, 1500, 750)

        self.setWindowTitle('MER.io')
        self.setWindowIcon(QIcon('../assets/copter_icon.png'))

    def reset_ui(self):
        self.tree.hide()
        self.tree: TreeView = TreeView()
        self.stacked_dfs: QStackedWidget = QStackedWidget()

        self.import_busy_txt('')
        self.set_mer_info(('', ''))

        self.splitter.replaceWidget(0, self.tree)
        self.splitter.replaceWidget(1, self.stacked_dfs)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.menuBar().children()[1].actions()[1].setEnabled(False)

    def create_menu_bar(self):
        menu_bar: QMenuBar = self.menuBar()

        @dataclass
        class MenuItem:
            name: str
            func: callable
            shortcut: str

        menu_bar_items: Dict[str, List[MenuItem]] = {'File': [MenuItem(name='Import',
                                                                       func=self.import_file,
                                                                       shortcut='Ctrl+O'),
                                                              MenuItem(name='Export',
                                                                       func=self.export,
                                                                       shortcut='Ctrl+E'),
                                                              MenuItem(name='Exit',
                                                                       func=self.exit_program,
                                                                       shortcut='Ctrl+Q')
                                                              ]}

        for name in menu_bar_items:
            menu: QMenu = menu_bar.addMenu(name)

            for item in menu_bar_items[name]:
                action: QAction = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                action.triggered.connect(item.func)
                menu.addAction(action)

        self.menuBar().children()[1].actions()[1].setEnabled(False)

    def create_progress_window(self):
        self.progress_window: QDialog = QDialog()
        self.progress_window.setWindowModality(Qt.ApplicationModal)
        self.progress_bar: QProgressBar = QProgressBar(self.progress_window)
        self.progress_bar.setWindowIcon(QIcon('../assets/copter_icon.png'))
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

    def toggle_progress(self, show: bool):
        if show:
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def set_tact_scenario(self, text: str):
        if self.status_bar_tactical_scenario is not None:
            self.status_bar.removeWidget(self.status_bar_tactical_scenario)

        self.status_bar_tactical_scenario = QLabel(text)
        self.status_bar.addPermanentWidget(self.status_bar_tactical_scenario)

    def set_filename(self, text: str):
        if self.status_bar_filename is not None:
            self.status_bar.removeWidget(self.status_bar_filename)

        self.status_bar_filename = QLabel(text)
        self.status_bar.addWidget(self.status_bar_filename)

    def error_dialog(self, txt: str):
        QMessageBox.warning(self, 'Error', txt, QMessageBox.Ok)

    def no_tact_dialog(self, txt: str):
        confirm = QMessageBox.warning(self, 'Warning', txt,
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.continue_without_tact_signal.emit()
        else:
            self.reset_ui()

    def import_busy_txt(self, txt: str):
        self.progress_window_label.setText(txt)
        self.progress_window_label.adjustSize()

    def set_mer_info(self, info: Tuple):
        self.set_filename(info[0])
        self.set_tact_scenario(info[1])

    def import_file(self):
        dialog = QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter='*.txt *.zip', directory='../test_mers')

        if len(paths) > 0:
            try:
                self.import_signal.emit(paths)
            except Exception as e:
                self.error_dialog('Something went wrong...')
                print(get_exception(e))

    def export(self):
        path = get_path()
        if path:
            self.export_signal.emit(path)

    def enable_export_menu(self):
        self.menuBar().children()[1].actions()[1].setEnabled(True)

    def exit_program(self):
        confirm = QMessageBox.warning(self, 'Warning', 'Close program?',
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.exit_signal.emit()
