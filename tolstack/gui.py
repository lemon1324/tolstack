# gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QCheckBox,
)

from tolstack.compute_stack import process_files


class MyApp(QWidget):
    MIN_WINDOW_WIDTH = 400

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Processor")
        self.setMinimumWidth(self.MIN_WINDOW_WIDTH)  # Apply the minimum window width

        main_layout = QVBoxLayout()

        # Create a reference width based on the longest button text
        btn_width = (
            max(
                self.fontMetrics().boundingRect("Browse Input File").width(),
                self.fontMetrics().boundingRect("Browse Save File").width(),
            )
            + 20
        )  # Add extra padding for aesthetics

        input_file_layout = QHBoxLayout()
        self.input_file_text = QLineEdit()
        self.input_file_text.setPlaceholderText("No input file selected")
        self.btn_browse_input = QPushButton("Browse Input File")
        self.btn_browse_input.setFixedWidth(btn_width)
        self.btn_browse_input.clicked.connect(self.browse_input_file)
        input_file_layout.addWidget(self.input_file_text)
        input_file_layout.addWidget(self.btn_browse_input)

        save_file_layout = QHBoxLayout()
        self.save_file_text = QLineEdit()
        self.save_file_text.setPlaceholderText("No save file selected")
        self.btn_browse_save = QPushButton("Browse Save File")
        self.btn_browse_save.setFixedWidth(btn_width)
        self.btn_browse_save.clicked.connect(self.browse_save_file)
        save_file_layout.addWidget(self.save_file_text)
        save_file_layout.addWidget(self.btn_browse_save)

        checkbox_layout = QHBoxLayout()
        self.option_a_checkbox = QCheckBox("Sensitivity Analysis")
        self.option_b_checkbox = QCheckBox("Tolerance Contribution")
        checkbox_layout.addWidget(self.option_a_checkbox)
        checkbox_layout.addWidget(self.option_b_checkbox)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_processing)

        # Optionally set a fixed width for input fields to keep them consistent
        input_field_width = self.width() - 2 * btn_width - 40  # Adjust as necessary
        self.input_file_text.setFixedWidth(input_field_width)
        self.save_file_text.setFixedWidth(input_field_width)

        main_layout.addLayout(input_file_layout)
        main_layout.addLayout(save_file_layout)
        main_layout.addLayout(checkbox_layout)
        main_layout.addWidget(self.run_button)

        self.setLayout(main_layout)

    def browse_input_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if fname:
            self.input_file_text.setText(fname)

    def browse_save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)")
        if fname:
            self.save_file_text.setText(fname)

    def run_processing(self):
        input_file = self.input_file_text.text()
        save_file = self.save_file_text.text()
        option_a = self.option_a_checkbox.isChecked()
        option_b = self.option_b_checkbox.isChecked()

        process_files(input_file, save_file, option_a, option_b)


def run_app():
    app = QApplication(sys.argv)
    app.setStyle("Cleanlooks")
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
