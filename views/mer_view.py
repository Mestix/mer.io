from dataclasses import dataclass
from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QLabel, QStatusBar, QWidget, \
    QProgressBar, QDialog, QMainWindow, QAction, QMessageBox

from views.tree_view import TreeView


class MerView(QMainWindow):
    import_signal: pyqtSignal = pyqtSignal()
    confirmed_yes_signal: pyqtSignal = pyqtSignal()
    exit_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.splitter: Union[QSplitter, None] = None
        self.stacked_dfs: Union[QStackedWidget, None] = None
        self.tree: Union[TreeView, None] = None
        self.background_label: Union[QLabel, None] = None

        self.status_bar: Union[QStatusBar, None] = None
        self.status_bar_filename: Union[QWidget, None] = None
        self.status_bar_tactical_scenario: Union[QWidget, None] = None

        self.progress_bar: Union[QProgressBar, None] = None
        self.progress_window: Union[QDialog, None] = None
        self.progress_window_label: Union[str, None] = None

        self.init_ui()

    def init_ui(self):
        self.splitter = QSplitter(self)
        self.tree = TreeView()
        self.tree.hide()

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

        self.background_label = QLabel('Nothing to see here...', self)
        self.background_label.setStyleSheet("QLabel { color : gray; }")
        self.background_label.adjustSize()
        self.set_background_lbl_to_centre()

        self.setWindowTitle('MER.io')
        self.setWindowIcon(QIcon('../assets/copter_icon.png'))

    def reset_ui(self):
        self.tree = TreeView()
        self.tree.hide()
        self.stacked_dfs = QStackedWidget()

        self.progress_window_label.setText('')
        self.progress_window_label.adjustSize()
        self.background_label.show()
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

        @dataclass
        class MenuItem:
            name: str
            func: callable
            shortcut: str = ''

        menu_bar_items = {'File': [MenuItem(name='Import',
                                            func=self.import_file,
                                            shortcut='Ctrl+O'),
                                   MenuItem(name='Exit',
                                            func=self.exit_program,
                                            shortcut='Ctrl+Q')
            ,
                                   ]}

        for name in menu_bar_items:
            menu = menu_bar.addMenu(name)

            for item in menu_bar_items[name]:
                action = QAction(item.name, self)
                action.setShortcut(item.shortcut)
                action.triggered.connect(item.func)
                menu.addAction(action)

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

    def toggle_progress(self, show):
        if show:
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def set_background_lbl_to_centre(self):
        self.background_label.show()
        width = round((self.width() - self.background_label.width()) / 2)
        height = round((self.height() - self.background_label.height()) / 2)
        self.background_label.move(width, height)

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

    def show_confirm_dialog(self, txt):
        QMessageBox.warning(self, 'Error', txt, QMessageBox.Ok)
        self.reset_ui()

    def show_yesno_dialog(self, txt):
        confirm = QMessageBox.warning(self, 'Warning', txt,
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.background_label.hide()
            self.confirmed_yes_signal.emit()
        else:
            self.reset_ui()

    def set_progress_text(self, txt):
        self.progress_window_label.setText(txt)
        self.progress_window_label.adjustSize()

    def set_mer_info(self, info):
        self.set_status_bar_right_widget(info[0])
        self.set_status_bar_left_widget(info[1])

    def import_file(self):
        self.import_signal.emit()

    def exit_program(self):
        confirm = QMessageBox.warning(self, 'Warning', 'Close program?',
                                      QMessageBox.No | QMessageBox.Yes)
        if confirm == QMessageBox.Yes:
            self.exit_signal.emit()
        else:
            pass

