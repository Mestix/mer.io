from dataclasses import dataclass
from typing import Union, List, Dict

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QLabel, QStatusBar, QWidget, \
    QProgressBar, QDialog, QMainWindow, QAction, QMessageBox, QMenuBar, QMenu

from src.environment import environment
from src.utility.utility import save_file, open_file
from src.views.bulk_export_dlg import BulkExportDialog
from src.views.tree_view import TreeView


class MerView(QMainWindow):
    import_signal: pyqtSignal = pyqtSignal(list)
    export_signal: pyqtSignal = pyqtSignal(str)
    exit_signal: pyqtSignal = pyqtSignal()
    bulk_import_signal: pyqtSignal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.splitter: Union[QSplitter, None] = None
        self.stacked_dfs: Union[QStackedWidget, None] = None
        self.tree: Union[TreeView, None] = None

        self.status_bar: Union[QStatusBar, None] = None
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

        self.setWindowTitle('MER.io v{0}'.format(environment['version']))
        self.setWindowIcon(QIcon('./assets/copter_icon.png'))

    def reset_ui(self):
        self.toggle_progress(False)
        self.tree.hide()
        self.tree: TreeView = TreeView()
        self.stacked_dfs: QStackedWidget = QStackedWidget()

        self.import_busy('')
        self.set_tact_scenario('')
        self.enable_export_menu()

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
            shortcut: str = ''

        menu_bar_items: Dict[str, List[MenuItem]] = {'File': [MenuItem(name='Import',
                                                                       func=self.start_import,
                                                                       shortcut='Ctrl+O'),
                                                              MenuItem(name='Export',
                                                                       func=self.start_export,
                                                                       shortcut='Ctrl+E'),
                                                              MenuItem(name='Exit',
                                                                       func=self.exit_program,
                                                                       shortcut='Ctrl+Q')
                                                              ],
                                                     'Admin': [MenuItem(name='Bulk export',
                                                                        func=self.bulk_export),
                                                               ]
                                                     }

        for name in menu_bar_items:
            menu: QMenu = menu_bar.addMenu(name)

            for item in menu_bar_items[name]:
                action: QAction = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                action.triggered.connect(item.func)
                menu.addAction(action)

        self.menuBar().children()[1].actions()[1].setEnabled(False)

    def create_progress_window(self):
        self.progress_window: QDialog = QDialog(self)
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

    def add_widget(self, df):
        from src.views.explorer_view import ExplorerView
        df.explorer = ExplorerView(df)

        self.stacked_dfs.addWidget(df.explorer)
        self.tree.add_tree_item(df.name)

    def import_busy(self, txt: str):
        self.progress_window_label.setText(txt)
        self.progress_window_label.adjustSize()
        self.status_bar.showMessage(txt)

    def import_success(self, tact: str):
        self.set_tact_scenario(tact)

        self.enable_export_menu()
        self.toggle_progress(False)
        self.tree.show()

    def import_failed(self, txt: str):
        QMessageBox.warning(self, 'Error', txt, QMessageBox.Ok)

    def start_import(self):
        paths: List[str] = open_file()
        if len(paths) > 0:
            self.import_signal.emit(paths)

    def start_export(self):
        path: str = save_file()
        if path:
            self.export_signal.emit(path)

    def bulk_export(self):
        bulk_export_dialog: BulkExportDialog = BulkExportDialog(self)

        if bulk_export_dialog.exec() == QDialog.Accepted:
            self.bulk_import_signal.emit(bulk_export_dialog.get_info())

    def enable_export_menu(self):
        self.menuBar().children()[1].actions()[1].setEnabled(True)

    def exit_program(self):
        confirm = QMessageBox.warning(self, 'Warning', 'Close program?',
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.exit_signal.emit()
