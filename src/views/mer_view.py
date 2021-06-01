from dataclasses import dataclass
from typing import Union, List, Dict

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QLabel, QStatusBar, \
    QProgressBar, QDialog, QMainWindow, QAction, QMessageBox, QMenuBar, QMenu, QFileDialog

from src.dataclasses.menuitem import MenuItem
from src.environment import environment
from src.views.bulk_export_dlg import BulkExportDialog
from src.views.explorer_view import ExplorerView
from src.views.identifier_view import IdentifierListView

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
        self.splitter: QSplitter = QSplitter(self)
        self.stacked_dfs: QStackedWidget = QStackedWidget(self)
        self.identifiers: IdentifierListView = IdentifierListView(self)

        self.splitter.addWidget(self.identifiers)
        self.splitter.addWidget(self.stacked_dfs)

        self.status_bar: QStatusBar = self.statusBar()
        self.status_bar_tactical_scenario: QLabel = QLabel()
        self.status_bar_label: QLabel = QLabel()

        self.status_bar.addWidget(self.status_bar_label)
        self.status_bar.addPermanentWidget(self.status_bar_tactical_scenario)

        self.progress_window: QDialog = QDialog(self)
        self.progress_window_label: QLabel = QLabel()
        self.progress_bar: QProgressBar = QProgressBar(self.progress_window)

        self.explorers: Dict[str, ExplorerView] = dict()

        self.init_ui()

    def init_ui(self):
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter.setSizes([300, 1000])
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.splitter)

        self.create_menu_bar()
        self.create_progress_window()

        self.setGeometry(250, 150, 1500, 750)

        self.setWindowTitle('MER.io v{0}'.format(environment['version']))
        self.setWindowIcon(QIcon('./assets/icons/copter_icon.png'))

    def reset_ui(self):
        """
        Completely reset the mer view
        """

        # disable progress dialog
        self.toggle_progress(False)

        # first hide the identifier List view or it will remain somewhere in the view
        self.identifiers.hide()

        # let the garbage collector reset the widgets,
        # because it takes too many time to remove all widgets separately
        self.identifiers: IdentifierListView = IdentifierListView(self)
        self.stacked_dfs: QStackedWidget = QStackedWidget(self)

        self.explorers: Dict[str, ExplorerView] = dict()

        self.task_busy('')
        self.set_tact_scenario('')

        self.splitter.replaceWidget(0, self.identifiers)
        self.splitter.replaceWidget(1, self.stacked_dfs)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.toggle_menus(False)

    def create_menu_bar(self):
        menu_bar: QMenuBar = self.menuBar()

        menu_bar_items: Dict[str, List[MenuItem]] = \
            {'File': [MenuItem(name='Import',
                               func=self.start_import,
                               shortcut='Ctrl+O',
                               items=[]),
                      MenuItem(name='Export',
                               func=self.start_export,
                               shortcut='Ctrl+E',
                               items=[]),
                      MenuItem(name='Bulk export',
                               func=self.start_bulk_export,
                               shortcut='Ctrl+B',
                               items=[]),
                      MenuItem(name='Exit',
                               func=self.exit_program,
                               shortcut='Ctrl+Q',
                               items=[])
                      ],
             'Edit': [MenuItem(name='Copy',
                               func=lambda x: self.copy(False),
                               shortcut='Ctrl+C',
                               items=[]),
                      MenuItem(name='Copy with header',
                               func=lambda x: self.copy(True),
                               shortcut='Ctrl+shift+C',
                               items=[])
                      ],
             'Settings': [MenuItem(name='Theme',
                                   func=None,
                                   shortcut='',
                                   items=list(map(lambda x: MenuItem(name=x
                                                                     .replace('.xml', '')
                                                                     .replace('_', ' '),
                                                                     func=lambda y: self.set_theme(x),
                                                                     shortcut='',
                                                                     items=[]), themes))),
                          MenuItem(name='Help',
                                   func=callable,
                                   shortcut='',
                                   items=[])
                          ]}

        for name in menu_bar_items:
            menu: QMenu = menu_bar.addMenu(name)
            item: MenuItem
            for item in menu_bar_items[name]:
                action: QAction = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                if item.func:
                    action.triggered.connect(item.func)
                    menu.addAction(action)

                if item.items:
                    sub_menu: QMenu = menu.addMenu(item.name)

                    sub_item: MenuItem
                    for sub_item in item.items:
                        action: QAction = QAction(sub_item.name, self)
                        action.setShortcut(sub_item.shortcut)
                        action.triggered.connect(sub_item.func)
                        sub_menu.addAction(action)

        self.toggle_menus(False)

    def create_progress_window(self):
        self.progress_window.setWindowModality(Qt.ApplicationModal)
        self.progress_window.resize(400, 100)

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
        """
        Show or hide progress dialog
        """
        if show:
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def add_widget(self, df):
        """
        For every dataframe model, add a explorer view to the stacked widget
        """
        from src.views.explorer_view import ExplorerView
        explorer = ExplorerView(df)

        self.explorers[df.name] = explorer
        self.stacked_dfs.addWidget(explorer)

        self.identifiers.add_tree_item(df.name)

    def task_busy(self, txt: str):
        """
        Set status message and progress dialog text
        """
        self.progress_window_label.setText(txt)
        self.progress_window_label.adjustSize()
        self.show_status_message(txt)

    def import_success(self, tact: str):
        self.status_bar_tactical_scenario.setText(tact)

        self.toggle_menus(True)
        self.toggle_progress(False)
        self.identifiers.show()

    def import_failed(self, txt: str):
        self.show_status_message(txt)
        QMessageBox.critical(self, 'Error', txt, QMessageBox.Ok)

    def show_status_message(self, txt: str):
        """
        Updates status bar left widget when any busy signal is emitted from controller
        """
        self.status_bar_label.setText('Status: {0} '.format(txt))

    def set_tact_scenario(self, txt: str):
        """
        Set status bar right widget to tactical scenario(s)
        """
        self.status_bar_tactical_scenario.setText(txt)

    def start_import(self):
        paths, _ = QFileDialog().getOpenFileNames(filter='*.txt *.zip')
        if len(paths) > 0:
            self.import_signal.emit(paths)

    def start_export(self):
        path, _ = QFileDialog().getSaveFileName(filter="*.xlsx")
        if path:
            self.export_signal.emit(path)

    def start_bulk_export(self):
        bulk_export_dialog: BulkExportDialog = BulkExportDialog(self)

        if bulk_export_dialog.exec() == QDialog.Accepted:
            self.bulk_import_signal.emit(bulk_export_dialog.get_info())

    def toggle_import_menu(self, enable: bool):
        """
        Some menu's are disabled when running a long task
        """
        # file > import
        self.menuBar().children()[1].actions()[0].setEnabled(enable)

    def toggle_menus(self, enable: bool):
        """
        Some menu's are disabled when running a long task
        """
        # file > export
        self.menuBar().children()[1].actions()[1].setEnabled(enable)

        # edit > copy
        self.menuBar().children()[2].actions()[0].setEnabled(enable)

        # edit > copy with header
        self.menuBar().children()[2].actions()[1].setEnabled(enable)

    def set_theme(self, name: str):
        """
        Apply theme stylesheet
        """
        self.set_theme_signal.emit(name)

    def set_identifier(self, name: str):
        """
        Select a identifier from the IdentifierListview. Puts the selected Explorer on top of the stacked widget.
        """
        self.stacked_dfs.setCurrentWidget(self.explorers[name])

    def copy(self, header):
        """
        According to the selected menu item (with or without header) execute copying in DataFrameViewer
        """
        current_dfm: ExplorerView = self.stacked_dfs.currentWidget()
        if current_dfm:
            current_dfm.viewer.copy(header)
        else:
            return

    def exit_program(self):
        confirm = QMessageBox.warning(self, 'Warning', 'Close program?',
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.exit_signal.emit()
