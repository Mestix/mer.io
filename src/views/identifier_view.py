import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QAbstractItemModel, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QAbstractItemView, QCheckBox, QListView, QLabel, \
    QHBoxLayout


class IdentifierListView(QWidget):
    selection_changed_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.hide()

        # view
        self.identifiers: QListView = QListView()
        self.identifiers.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.identifiers.clicked.connect(self.select_item)

        # model
        self.model: QStandardItemModel = QStandardItemModel(self.identifiers)
        self.model.setHorizontalHeaderLabels(['Identifiers'])

        # filter model
        self.proxy_model = QSortFilterProxyModel(self.identifiers)
        self.proxy_model.setSourceModel(self.model)

        self.identifiers.setModel(self.proxy_model)

        self.select_all_box: QCheckBox = QCheckBox('Select All')

        self.selection_changed_signal.connect(self.parent().set_identifier)

        self.init_ui()

    def init_ui(self) -> None:
        self.select_all_box.setCheckState(Qt.Checked)
        self.select_all_box.stateChanged.connect(self.toggle_select_all)

        # identifier search
        searchbar: QLineEdit = QLineEdit('')
        searchbar.setPlaceholderText('Search')
        searchbar.textChanged.connect(self.filter_list)

        # layout
        info_box: QHBoxLayout = QHBoxLayout()
        identifier_label: QLabel = QLabel('Identifiers')
        identifier_label.setFont(QFont('Arial', 10))
        info_box.addWidget(identifier_label)
        info_box.addWidget(self.select_all_box)
        info_widget: QWidget = QWidget()
        info_widget.setLayout(info_box)

        # layout
        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(info_widget)
        layout.addWidget(self.identifiers)
        layout.addWidget(searchbar)

        self.setLayout(layout)

    def select_item(self, index: QModelIndex) -> None:
        # select an item from the IdentifierListView
        name: str = self.identifiers.model().data(index)
        self.selection_changed_signal.emit(name)
        self.check_all_checked()

    def filter_list(self, txt):
        # filter listview according to given expression
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(txt.replace(' ', '_').upper(), Qt.CaseInsensitive, QtCore.QRegExp.FixedString))

    def add_tree_item(self, name: str) -> None:
        # add an item to the listview
        item: QStandardItem = QStandardItem(name)
        item.setCheckable(True)
        item.setCheckState(Qt.Checked)
        self.model.appendRow(item)

    def selected_items(self) -> typing.Generator:
        """
        Returns all selected items in the ListView
        """
        root: QAbstractItemModel = self.get_root()
        item_count: int = self.get_item_count()

        for i in range(item_count):
            item: QStandardItem = root.child(i)
            if item.checkState() == Qt.Checked:
                yield item.text()

    def get_root(self) -> QAbstractItemModel:
        """
        Return the invisible root item
        """
        return self.identifiers.model().sourceModel().invisibleRootItem()

    def get_item_count(self) -> int:
        """
        Return the count of identifiers
        """
        return self.get_root().rowCount()

    def toggle_select_all(self, state: Qt.CheckState) -> None:
        """
        select all identifiers
        """
        for i in range(self.get_item_count()):
            self.get_root().child(i).setCheckState(state)

    def check_all_checked(self) -> None:
        """
        Check if all identifiers are selected or not
        """
        if self.is_all_checked():
            self.select_all_box.setCheckState(Qt.Checked)
        elif self.is_all_unchecked():
            self.select_all_box.setCheckState(Qt.Unchecked)

    def is_all_checked(self) -> bool:
        """
        Check if all identifiers are selected
        """
        for i in range(self.get_item_count()):
            if self.get_root().child(i).checkState() == Qt.Unchecked:
                return False

        return True

    def is_all_unchecked(self) -> bool:
        """
        Check if all identifiers are unselected
        """
        for i in range(self.get_item_count()):
            if self.get_root().child(i).checkState() == Qt.Checked:
                return False

        return True
