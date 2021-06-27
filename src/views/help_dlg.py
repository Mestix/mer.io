from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextEdit


class HelpDialog(QDialog):

    def __init__(self, parent):
        super(HelpDialog, self).__init__(parent)

        self.setWindowTitle('Help')
        self.setGeometry(750, 200, 500, 450)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.size())

        self.help_text: QTextEdit = QTextEdit(self)
        self.help_text.setReadOnly(True)
        self.help_text.textCursor().insertHtml(help_text)
        self.help_text.moveCursor(QTextCursor.Start)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.help_text)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)
        self.hide()


help_text = """
<p><b>Import Mer</b></p>
<ul>
    <li>File &gt; Import</li>
    <li>Select 1 or more .txt or .zip files</li>
    <li>Wait until the program initializes the data</li>
</ul>
<p><b>Toggle Columns</b></p>
<ul>
    <li>Select &lsquo;Column&rsquo; tab from filter panel (right)</li>
    <li>Select or deselect the column&rsquo;s checkbox to show or hide it</li>
    <li>Select or deselect the &lsquo;Select all&rsquo; checkbox to show or hide all columns</li>
</ul>
<p><b>Search specific data</b></p>
<ul>
    <li>Select &lsquo;Filter&rsquo; tab from filter panel (right)</li>
    <li>Enter search term(s) to filter the data</li>
    <li>Press &lsquo;Reset filters&rsquo; to undo all filters</li>
    <li>Select or deselect a filter&rsquo;s checkbox to enable or disable it</li>
</ul>
<p><b>Search identifiers</b></p>
<ul>
    <li>Enter search term in the search box of the identifier panel (left) to search for identifiers</li>
</ul>
<p><b>Copy data</p>
<ul>
    <li>Select data to copy</b></li>
    <li>Select &gt; Copy with headers; to copy data with column names</li>
    <li>Edit &gt; Copy without headers; to only copy selected data&nbsp;</li>
</ul>
<p><b>Bulk export</b></p>
<ul>
    <li>File &gt; Bulk export</li>
    <li>The bulk dialog should open</li>
    <li>Fill the required fields (source directory, destination file)</li>
    <li>Optionally fill the optional fields (preset, skip mers)</li>
    <li>Press &lsquo;OK&rsquo;</li>
    <li>Wait until the task finishes. The current status of the program is shown in the status bar at the bottom of the screen</li>
</ul>
<p><b>Change theme</b></p>
<ul>
    <li>Settings &gt; Theme &gt; choose theme</li>
</ul>
"""