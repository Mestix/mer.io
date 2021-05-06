import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QAbstractItemModel, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QAbstractItemView, QCheckBox, QListView, QLabel, \
    QHBoxLayout


class IdentifierView(QWidget):
    selection_changed_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.hide()
        self.identifiers: QListView = QListView()
        self.identifiers.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.identifiers.clicked.connect(self.select_item)

        self.model: QStandardItemModel = QStandardItemModel(self.identifiers)
        self.model.setHorizontalHeaderLabels(['Identifiers'])

        self.proxy_model = QSortFilterProxyModel(self.identifiers)
        self.proxy_model.setSourceModel(self.model)

        self.identifiers.setModel(self.proxy_model)
        self.select_all_box: QCheckBox = QCheckBox('Select All')

        self.init_ui()

    def init_ui(self):
        self.select_all_box.setCheckState(Qt.Checked)
        self.select_all_box.stateChanged.connect(self.select_box_checked)

        searchbar: QLineEdit = QLineEdit('')
        searchbar.setPlaceholderText('Search')
        searchbar.textChanged.connect(self.on_search)

        info_box: QHBoxLayout = QHBoxLayout()
        identifier_label: QLabel = QLabel('Identifiers')
        identifier_label.setFont(QFont('Arial', 10))
        info_box.addWidget(identifier_label)
        info_box.addWidget(self.select_all_box)
        info_widget: QWidget = QWidget()
        info_widget.setLayout(info_box)

        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(info_widget)
        layout.addWidget(self.identifiers)
        layout.addWidget(searchbar)

        self.setLayout(layout)

    def select_item(self, index: QModelIndex) -> None:
        name: str = self.identifiers.model().data(index)
        self.selection_changed_signal.emit(name)
        self.check_all_checked()

    def on_search(self, text):
        self.proxy_model.setFilterRegExp(text.replace(' ', '_').upper())

    def add_tree_item(self, name: str) -> None:
        item: QStandardItem = QStandardItem(name)
        item.setCheckable(True)
        item.setCheckState(Qt.Checked)
        self.model.appendRow(item)

    def selected_items(self) -> typing.Generator:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            if item.checkState() == Qt.Checked:
                yield item.text()

    def get_root(self) -> QAbstractItemModel:
        return self.identifiers.model().sourceModel().invisibleRootItem()

    def get_item_count(self) -> int:
        return self.get_root().rowCount()

    def select_box_checked(self, state: Qt.CheckState) -> None:
        if state == Qt.Checked:
            self.select_all()
        else:
            self.deselect_all()

    def select_all(self) -> None:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            item.setCheckState(Qt.Checked)

    def deselect_all(self) -> None:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            item.setCheckState(Qt.Unchecked)

    def filter_list(self, txt: str) -> None:
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(txt, Qt.CaseInsensitive, QtCore.QRegExp.FixedString))

    def check_all_checked(self) -> None:
        if self.is_all_checked():
            self.select_all_box.setCheckState(Qt.Checked)
        elif self.is_all_unchecked():
            self.select_all_box.setCheckState(Qt.Unchecked)

    def is_all_checked(self) -> bool:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            if item.checkState() == Qt.Unchecked:
                return False

        return True

    def is_all_unchecked(self) -> bool:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            if item.checkState() == Qt.Checked:
                return False

        return True



