import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QAbstractItemModel, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeView, QAbstractItemView, QCheckBox


class TreeView(QWidget):
    selection_changed_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.hide()
        self.tree: QTreeView = QTreeView()
        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree.clicked.connect(self.select_item)

        self.model: QStandardItemModel = QStandardItemModel(self.tree)
        self.model.setHorizontalHeaderLabels(['Identifiers'])

        self.proxy_model = QSortFilterProxyModel(self.tree)
        self.proxy_model.setSourceModel(self.model)

        self.tree.setModel(self.proxy_model)

        self.init_ui()

    def init_ui(self):
        self.tree.setAlternatingRowColors(True)

        select_all_box: QCheckBox = QCheckBox('Select All')
        select_all_box.stateChanged.connect(self.select_box_checked)

        searchbar: QLineEdit = QLineEdit('')
        searchbar.setPlaceholderText('Search')
        searchbar.textChanged.connect(self.on_search)

        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(select_all_box)
        layout.addWidget(self.tree)
        layout.addWidget(searchbar)

        self.setLayout(layout)

    def select_item(self, index: QModelIndex) -> None:
        name: str = self.tree.model().data(index)
        self.selection_changed_signal.emit(name)

    def on_search(self, text):
        self.proxy_model.setFilterRegExp(text.upper())

    def add_tree_item(self, name: str) -> None:
        item: QStandardItem = QStandardItem(name)
        item.setCheckable(True)
        item.setCheckState(Qt.Unchecked)
        self.model.appendRow(item)

    def selected_items(self) -> typing.Generator:
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            if item.checkState() == Qt.Checked:
                yield item.text()

    def get_root(self) -> QAbstractItemModel:
        return self.tree.model().sourceModel().invisibleRootItem()

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



