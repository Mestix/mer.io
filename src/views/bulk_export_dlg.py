from dataclasses import dataclass
from typing import List
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGroupBox, QComboBox, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QFormLayout, QLabel, QFileDialog, QPushButton, QMessageBox, QCheckBox

preset_path = './assets/presets'


@dataclass
class BulkSettings:
    src: str
    dst: str
    preset: str
    skip: bool


class BulkExportDialog(QDialog):

    def __init__(self, parent):
        super(BulkExportDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle('Bulk Export')
        self.setGeometry(750, 200, 500, 450)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.size())

        self.form_groupbox = QGroupBox()

        self.preset_box = QComboBox()

        self.preset_box.addItems([''] + get_available_presets())

        self.format_box = QComboBox()
        self.format_box.addItems(['.xlsx'])

        self.src_dir: QLineEdit = QLineEdit()
        self.src_dir.setDisabled(True)

        self.dst_dir = QLineEdit()
        self.dst_dir.setDisabled(True)

        self.skip_checkbox: QCheckBox = QCheckBox('Skip Mers without tactical scenario')
        self.skip_checkbox.setCheckState(Qt.Checked)

        self.create_form()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.verify_input)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_groupbox)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def create_form(self):
        layout = QFormLayout()

        source_btn: QPushButton = QPushButton('Pick')
        source_btn.clicked.connect(self.select_src_dir)
        source_btn.setMaximumWidth(100)
        self.src_dir.setMinimumWidth(350)
        layout.addRow(QLabel('Source folder'))
        layout.addRow(self.src_dir, source_btn)

        dst_btn: QPushButton = QPushButton('Pick')
        dst_btn.clicked.connect(self.select_dst_dir)
        layout.addRow(QLabel('Destination file'))
        dst_btn.setMaximumWidth(100)
        self.dst_dir.setMinimumWidth(350)
        layout.addRow(self.dst_dir, dst_btn)

        layout.addRow(QLabel('Format'))
        layout.addRow(self.format_box)
        layout.addRow(QLabel('Preset'))
        layout.addRow(self.preset_box)
        layout.addRow(self.skip_checkbox)

        self.form_groupbox.setLayout(layout)

    def select_src_dir(self):
        file = str(QFileDialog.getExistingDirectory(self.parent, 'Select source directory'))
        if file:
            self.src_dir.setText(file)

    def select_dst_dir(self):
        path, _ = QFileDialog().getSaveFileName(self.parent, 'Select destination file', filter='*.xlsx')
        if path:
            self.dst_dir.setText(path)

    def verify_input(self):
        if self.src_dir.text() == '' or self.dst_dir.text() == '':
            QMessageBox.information(self, 'Notification', 'Source and Destination are required', QMessageBox.Ok)

        else:
            self.accept()

    def get_info(self) -> BulkSettings:
        return BulkSettings(
            src=self.src_dir.text(),
            dst=self.dst_dir.text(),
            preset=str(self.preset_box.currentText()),
            skip=self.skip_checkbox.checkState()
        )


def get_available_presets() -> List[str]:
    presets: List[str] = list()
    for root, dirs, files in os.walk(preset_path):
        for file in files:
            if file.endswith('.json'):
                presets.append(os.path.splitext(os.path.basename(file))[0])

    return presets
