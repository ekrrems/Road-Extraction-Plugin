# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QPixmap

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'road_extractor_dialog_base.ui'))


class RoadExtractorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(RoadExtractorDialog, self).__init__(parent)
        self.setupUi(self)
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # Add a QLabel for the screenshot
        self.screenshot_label = QtWidgets.QLabel()
        layout.addWidget(self.screenshot_label)

        # Add a QTextEdit for printing results
        self.results_text_edit = QtWidgets.QTextEdit()
        layout.addWidget(self.results_text_edit)

        # Create Apply and Cancel buttons
        self.apply_button = QtWidgets.QPushButton("Apply")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        # Connect the buttons to their respective functions
        self.apply_button.clicked.connect(self.apply_function)
        self.cancel_button.clicked.connect(self.close)

        # Add the buttons to the layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def set_screenshot(self, pixmap):
        self.screenshot_label.setPixmap(pixmap)

    def apply_function(self):
        # Define your "Apply" button function here
        print("Apply button clicked")

        # Example: Append text to the results text edit
        self.results_text_edit.append("Apply button clicked")
