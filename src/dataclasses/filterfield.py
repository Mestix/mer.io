from dataclasses import dataclass

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QListWidgetItem


@dataclass
class Field(QObject):
    def __init__(self, name: str, parent):
        super().__init__(parent)
        self.name: str = name

        self.filter_field: QLineEdit = QLineEdit('')
        self.filter_field.textChanged.connect(lambda x: parent.set_filter(self))

        self.column_field: QListWidgetItem = QListWidgetItem(name)
        self.column_field.setCheckState(Qt.Checked)

        self.filter_active = QCheckBox(self.name)
        self.filter_active.setChecked(True)
        self.filter_active.stateChanged.connect(self.toggle_enabled)
        self.filter_active.stateChanged.connect(lambda x: parent.set_filter(self))

    def toggle_enabled(self, value: int) -> None:
        self.filter_field.setEnabled(value == Qt.Checked)

    def reset_field(self) -> None:
        self.filter_field.setText('')
        self.filter_field.setEnabled(True)
        self.filter_active.setChecked(True)
