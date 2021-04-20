from typing import Tuple

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem

from utility.utility import get_exception


class TreeView(QtWidgets.QTreeWidget):
    selection_changed_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(['Identifier', 'Cols', 'Rows'])
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 35)
        self.setColumnWidth(2, 35)

        self.hide()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(300, 500)

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection) -> None:
        super().selectionChanged(selected, deselected)

        if len(self.selectedItems()) > 0:
            item = self.selectedItems()[0]
            df_name = item.data(0, Qt.DisplayRole)
            self.selection_changed_signal.emit(df_name)

    def add_tree_item(self, name: str, shape: Tuple[int, int]) -> None:
        self.addTopLevelItem(QTreeWidgetItem([name, str(shape[1]), str(shape[0])]))
        self.setCurrentItem(self.topLevelItem(0))
        self.itemSelectionChanged.emit()
