import functools
from dataclasses import dataclass
from typing import Union, List, Dict

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QLabel, QStatusBar, \
    QProgressBar, QDialog, QMainWindow, QAction, QMessageBox, QMenuBar, QMenu, QFileDialog

from src.environment import environment
from src.views.bulk_export_dlg import BulkExportDialog
from src.views.explorer_view import ExplorerView
from src.views.identifier_view import IdentifierView

themes = ['dark_amber.xml',
          'dark_blue.xml',
          'dark_cyan.xml',
          'dark_lightgreen.xml',
          'dark_pink.xml',
          'dark_purple.xml',
          'dark_red.xml',
          'dark_teal.xml',
          'dark_yellow.xml',
          'light_amber.xml',
          'light_blue.xml',
          'light_cyan.xml',
          'light_cyan_500.xml',
          'light_lightgreen.xml',
          'light_pink.xml',
          'light_purple.xml',
          'light_red.xml',
          'light_teal.xml',
          'light_yellow.xml']


class MerView(QMainWindow):
    import_signal: pyqtSignal = pyqtSignal(list)
    export_signal: pyqtSignal = pyqtSignal(str)
    exit_signal: pyqtSignal = pyqtSignal()
    bulk_import_signal: pyqtSignal = pyqtSignal(object)
    set_theme_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.splitter: Union[QSplitter, None] = None
        self.stacked_dfs: Union[QStackedWidget, None] = None
        self.identifiers: Union[IdentifierView, None] = None

        self.status_bar: Union[QStatusBar, None] = None
        self.status_bar_tactical_scenario: Union[QLabel, None] = None
        self.status_bar_label: Union[QLabel, None] = None

        self.progress_bar: Union[QProgressBar, None] = None
        self.progress_window: Union[QDialog, None] = None
        self.progress_window_label: Union[QLabel, None] = None

        self.explorers: Dict[str, ExplorerView] = dict()

        self.init_ui()

    def init_ui(self):
        self.splitter: QSplitter = QSplitter(self)
        self.identifiers: IdentifierView = IdentifierView(self)
        self.stacked_dfs: QStackedWidget = QStackedWidget()

        self.splitter.addWidget(self.identifiers)
        self.splitter.addWidget(self.stacked_dfs)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.status_bar: QStatusBar = self.statusBar()
        self.status_bar_tactical_scenario = QLabel()
        self.status_bar_label = QLabel()
        self.status_bar.addWidget(self.status_bar_label)
        self.status_bar.addPermanentWidget(self.status_bar_tactical_scenario)

        self.splitter.setSizes([300, 1000])
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.splitter)

        self.create_menu_bar()
        self.create_progress_window()

        self.setGeometry(250, 150, 1500, 750)

        self.setWindowTitle('MER.io v{0}'.format(environment['version']))
        self.setWindowIcon(QIcon('./assets/icons/copter_icon.png'))

    def reset_ui(self):
        self.toggle_progress(False)
        self.identifiers.hide()

        self.identifiers: IdentifierView = IdentifierView(self)
        self.stacked_dfs: QStackedWidget = QStackedWidget(self)

        self.explorers: Dict[str, ExplorerView] = dict()

        self.task_busy('')
        self.set_tact_scenario('')
        self.toggle_export_menu(False)

        self.splitter.replaceWidget(0, self.identifiers)
        self.splitter.replaceWidget(1, self.stacked_dfs)
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
                                                               ],
                                                     'Theme': map(lambda x: MenuItem(name=x
                                                                                     .replace('.xml', '')
                                                                                     .replace('_', ' '),
                                                                                     func=self.set_theme)
                                                                  , themes)
                                                     }

        for name in menu_bar_items:
            menu: QMenu = menu_bar.addMenu(name)

            for item in menu_bar_items[name]:
                action: QAction = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                action.triggered.connect(functools.partial(item.func, item.name))
                menu.addAction(action)

        self.toggle_export_menu(False)

    def create_progress_window(self):
        self.progress_window: QDialog = QDialog(self)
        self.progress_window.setWindowModality(Qt.ApplicationModal)
        self.progress_window.resize(400, 100)

        self.progress_bar: QProgressBar = QProgressBar(self.progress_window)
        self.progress_window.setFixedSize(self.progress_window.size())
        self.progress_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.progress_window.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.progress_window.setWindowTitle('Please wait')
        self.progress_window_label = QLabel(self.progress_window)
        self.progress_window_label.move(15, 18)
        self.progress_bar.resize(370, 25)
        self.progress_bar.move(15, 40)
        self.progress_bar.setRange(0, 0)

    def toggle_progress(self, show: bool):
        if show:
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def add_widget(self, df):
        from src.views.explorer_view import ExplorerView
        explorer: ExplorerView = ExplorerView(df)

        self.explorers[df.name] = explorer
        self.stacked_dfs.addWidget(explorer)

        self.identifiers.add_tree_item(df.name)

    def task_busy(self, txt: str):
        self.progress_window_label.setText(txt)
        self.progress_window_label.adjustSize()
        self.show_status_message(txt)

    def import_success(self, tact: str):
        self.status_bar_tactical_scenario.setText(tact)

        self.toggle_export_menu(True)
        self.toggle_progress(False)
        self.identifiers.show()

    def import_failed(self, txt: str):
        self.show_status_message(txt)
        QMessageBox.critical(self, 'Error', txt, QMessageBox.Ok)

    def show_status_message(self, txt: str):
        self.status_bar_label.setText('Status: {0} '.format(txt))

    def set_tact_scenario(self, txt: str):
        self.status_bar_tactical_scenario.setText(txt)

    def start_import(self, *args):
        paths, _ = QFileDialog().getOpenFileNames(filter='*.txt *.zip')
        if len(paths) > 0:
            self.import_signal.emit(paths)

    def start_export(self, *args):
        path, _ = QFileDialog().getSaveFileName(filter="*.xlsx")
        if path:
            self.export_signal.emit(path)

    def bulk_export(self, *args):
        bulk_export_dialog: BulkExportDialog = BulkExportDialog(self)

        if bulk_export_dialog.exec() == QDialog.Accepted:
            self.bulk_import_signal.emit(bulk_export_dialog.get_info())

    def toggle_import_menu(self, enable: bool):
        if enable:
            self.menuBar().children()[1].actions()[0].setEnabled(True)
        else:
            self.menuBar().children()[1].actions()[0].setEnabled(False)

    def toggle_export_menu(self, enable: bool):
        self.menuBar().children()[1].actions()[1].setEnabled(enable)

    def set_theme(self, *args):
        self.set_theme_signal.emit(args[0])

    def set_identifier(self, name: str):
        self.stacked_dfs.setCurrentWidget(self.explorers[name])

    def exit_program(self, *args):
        confirm = QMessageBox.warning(self, 'Warning', 'Close program?',
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.exit_signal.emit()
