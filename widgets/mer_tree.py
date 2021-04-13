from typing import List

from PyQt5 import QtCore, QtWidgets, sip
from PyQt5.QtCore import Qt


class MerTree(QtWidgets.QTreeWidget):
    def __init__(self, mer_keeper: 'MerKeeper'):
        super().__init__()
        mer_keeper.tree = self
        self.mer_keeper = mer_keeper

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
            self.mer_keeper.select_df(df_name)
        else:
            pass

    def get_tree_items(self) -> List[QtWidgets.QTreeWidgetItem]:
        tree = self.invisibleRootItem()
        items = []

        for i in range(tree.childCount()):
            items.append(tree.child(i))

        return items

    def remove_items(self) -> None:
        for item in self.get_tree_items():
            sip.delete(item)
