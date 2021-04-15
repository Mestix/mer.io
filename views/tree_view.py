from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal


class TreeView(QtWidgets.QTreeWidget):
    selection_changed_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(['Identifier', 'Cols', 'Rows'])
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 35)
        self.setColumnWidth(2, 35)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(300, 500)

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection) -> None:
        super().selectionChanged(selected, deselected)

        if len(self.selectedItems()) > 0:
            item = self.selectedItems()[0]
            df_name = item.data(0, Qt.DisplayRole)
            self.selection_changed_signal.emit(df_name)
        else:
            pass
