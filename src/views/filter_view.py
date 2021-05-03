import sys
from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QScrollArea, QWidget, \
    QPushButton, QApplication, QTabWidget, QListWidget, QListWidgetItem, QCheckBox

from src.models.dataframe_model import DataFrameModel
import pandas as pd

from src.models.field_model import FilterField, ColumnField


class FilterView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        dfm.filter = self
        self.dfm: DataFrameModel = dfm
        self.filter_fields: List[FilterField] = list()
        self.column_fields: List[ColumnField] = list()
        self.column_list: QListWidget = QListWidget()
        self.filter_form: Union[QFormLayout, None] = None
        self.select_all_box: Union[QCheckBox, None] = None

        self.set_fields()

        self.init_ui()

    def init_ui(self) -> None:
        tabs: QTabWidget = QTabWidget()
        filter_tab: QWidget = QWidget()
        column_tab: QWidget = QWidget()

        tabs.addTab(column_tab, 'Columns')
        tabs.addTab(filter_tab, 'Filters')

        reset_button: QPushButton = QPushButton('Reset Filters', filter_tab)
        reset_button.clicked.connect(self.reset_filters)

        filter_content: QVBoxLayout = QVBoxLayout()
        filter_tab.setLayout(filter_content)
        self.filter_form: QFormLayout = QFormLayout(filter_tab)

        filter_scroll: QScrollArea = QScrollArea()
        filter_widget: QWidget = QWidget()
        filter_widget.setLayout(self.filter_form)
        filter_scroll.setWidget(filter_widget)
        filter_scroll.setWidgetResizable(True)
        filter_content.addWidget(reset_button)
        filter_content.addWidget(filter_scroll)

        self.select_all_box: QCheckBox = QCheckBox('Select All')
        self.select_all_box.setCheckState(Qt.Checked)
        self.select_all_box.stateChanged.connect(self.select_box_checked)

        column_layout: QVBoxLayout = QVBoxLayout()
        column_layout.addWidget(self.select_all_box)
        column_layout.addWidget(self.column_list)
        column_tab.setLayout(column_layout)

        self.column_list.itemClicked.connect(self.set_column)

        self.create_filter_form()
        self.create_column_list()

        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_filter_form(self) -> None:
        for f in self.filter_fields:
            self.filter_form.addRow(f.checkbox, f.field)

    def create_column_list(self) -> None:
        for f in self.column_fields:
            item: QListWidgetItem = QListWidgetItem(f.name)
            item.setCheckState(Qt.Checked)
            self.column_list.addItem(item)

    def set_fields(self) -> None:
        for column in self.dfm.df.columns:
            self.filter_fields.append(FilterField(column, self))
            self.column_fields.append(ColumnField(column, self))

    def reset_filters(self) -> None:
        self.dfm.reset_filters()
        for f in self.filter_fields:
            f.reset_field()

    def select_box_checked(self, state: Qt.CheckState):
        if state == Qt.Checked:
            self.select_all_cols()
        else:
            self.deselect_all_cols()

    def deselect_all_cols(self) -> None:
        for i in range(self.column_list.count()):
            item: QListWidgetItem = self.column_list.item(i)
            item.setCheckState(Qt.Unchecked)
            self.set_column(item)

    def select_all_cols(self) -> None:
        for i in range(self.column_list.count()):
            item: QListWidgetItem = self.column_list.item(i)
            item.setCheckState(Qt.Checked)
            self.set_column(item)

    def set_column(self, item: QListWidgetItem) -> None:
        name: str = item.text()
        if item.checkState() == Qt.Checked:
            self.dfm.add_column(name)
        else:
            self.dfm.remove_column(name)

        self.dfm.apply_filters()
        self.check_all_checked()

    def check_all_checked(self) -> None:
        if self.is_all_checked():
            self.select_all_box.setCheckState(Qt.Checked)
        elif self.is_all_unchecked():
            self.select_all_box.setCheckState(Qt.Unchecked)

    def is_all_checked(self) -> bool:
        for i in range(self.column_list.count()):
            if self.column_list.item(i).checkState() == Qt.Unchecked:
                return False

        return True

    def is_all_unchecked(self) -> bool:
        for i in range(self.column_list.count()):
            if self.column_list.item(i).checkState() == Qt.Checked:
                return False

        return True

    def set_filter(self, f: FilterField) -> None:
        expr: str = f.field.text()
        if not expr == '':
            self.dfm.add_filter(f.name, expr, f.checkbox.isChecked())
        else:
            self.dfm.remove_filter(f.name)

        self.dfm.apply_filters()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dfe = FilterView(DataFrameModel(pd.DataFrame({'a': [1, 2], 'b': [3, 4]})))
    dfe.show()

    sys.exit(app.exec_())
