import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QTextEdit,
    QFileDialog,
    QSizePolicy,
    QSplitter,
    QHeaderView,
    QLabel,
    QShortcut,
    QAction,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QItemSelectionModel

from PyQt5.QtGui import QFont, QKeySequence

from tolstack.compute_stack import process_data

import traceback


class EditableTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

    def add_row(self, data):
        row_position = self.rowCount()
        self.insertRow(row_position)

        for column, item in enumerate(data):
            if column < self.columnCount():  # Ensure we don't exceed the column count
                table_item = QTableWidgetItem(str(item))
                self.setItem(row_position, column, table_item)
                self.item(row_position, column).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
                )

    def get_all_data(self):
        data_list = []
        for row in range(self.rowCount()):
            row_data = []
            for column in range(self.columnCount()):
                item = self.item(row, column)
                row_data.append(item.text().strip() if item else "")
            data_list.append(row_data)
        return data_list

    def clear_all_data(self):
        self.setRowCount(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                item.setText("")
        else:
            super().keyPressEvent(event)


class EditableConstantWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["Name", "Value", "Note"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Set default column sizes
        default_column_widths = [50, 55, 420]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class EditableDimensionWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 7, parent)
        self.setHorizontalHeaderLabels(
            ["Name", "Nominal", "Plus", "Minus", "D", "PN", "Note"]
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Set default column sizes
        default_column_widths = [50, 55, 55, 55, 10, 65, 210]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class EditableExpressionWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 6, parent)
        self.setHorizontalHeaderLabels(["Name", "Value", "Lower", "Upper", "M", "Note"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Set default column sizes
        default_column_widths = [50, 55, 55, 55, 10, 275]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class MainWindow(QMainWindow):
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    SAVE_FILE = None
    CONTENTS_AT_SAVE = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("tolstack")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout()

        splitter = QSplitter(Qt.Horizontal)  # This will allow resizing horizontally

        # Splitter for left layout
        left_splitter = QSplitter(Qt.Vertical)

        right_layout = QVBoxLayout()

        # Table widgets: Constants
        self.constants_widget = EditableConstantWidget()

        self.add_constant_button = QPushButton("+")
        self.delete_constant_button = QPushButton("-")
        self.add_constant_button.clicked.connect(self.add_constant)
        self.delete_constant_button.clicked.connect(self.delete_constant)

        # Horizontal layout for constants title and buttons
        constant_header_layout = QHBoxLayout()
        constant_title_label = QLabel("CONSTANTS:")
        constant_title_label.setFixedHeight(30)
        constant_title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        constant_header_layout.addWidget(constant_title_label)
        constant_header_layout.addStretch()
        constant_header_layout.addWidget(self.add_constant_button)
        constant_header_layout.addWidget(self.delete_constant_button)

        # Wrapper for constants group
        constants_group = QWidget()
        constants_layout = QVBoxLayout()
        constants_layout.addLayout(constant_header_layout)
        constants_layout.addWidget(self.constants_widget)
        constants_group.setLayout(constants_layout)

        # Table Widgets: Dimensions
        self.dimensions_widget = EditableDimensionWidget()

        self.add_dimension_button = QPushButton("+")
        self.delete_dimension_button = QPushButton("-")
        self.add_dimension_button.clicked.connect(self.add_dimension)
        self.delete_dimension_button.clicked.connect(self.delete_dimension)

        # Horizontal layout for dimensions title and buttons
        dimension_header_layout = QHBoxLayout()
        dimension_title_label = QLabel("DIMENSIONS:")
        dimension_title_label.setFixedHeight(30)
        dimension_title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        dimension_header_layout.addWidget(dimension_title_label)
        dimension_header_layout.addStretch()
        dimension_header_layout.addWidget(self.add_dimension_button)
        dimension_header_layout.addWidget(self.delete_dimension_button)

        # Wrapper for dimensions group
        dimensions_group = QWidget()
        dimensions_layout = QVBoxLayout()
        dimensions_layout.addLayout(dimension_header_layout)
        dimensions_layout.addWidget(self.dimensions_widget)
        dimensions_group.setLayout(dimensions_layout)

        # Table Widgets: Expressions
        self.expressions_widget = EditableExpressionWidget()

        self.add_expression_button = QPushButton("+")
        self.delete_expression_button = QPushButton("-")
        self.add_expression_button.clicked.connect(self.add_expression)
        self.delete_expression_button.clicked.connect(self.delete_expression)

        # Horizontal layout for expressions title and buttons
        expression_header_layout = QHBoxLayout()
        expression_title_label = QLabel("EXPRESSIONS:")
        expression_title_label.setFixedHeight(30)
        expression_title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        expression_header_layout.addWidget(expression_title_label)
        expression_header_layout.addStretch()
        expression_header_layout.addWidget(self.add_expression_button)
        expression_header_layout.addWidget(self.delete_expression_button)

        # Wrapper for expressions group
        expressions_group = QWidget()
        expressions_layout = QVBoxLayout()
        expressions_layout.addLayout(expression_header_layout)
        expressions_layout.addWidget(self.expressions_widget)
        expressions_group.setLayout(expressions_layout)

        # Add groups to left splitter
        left_splitter.addWidget(constants_group)
        left_splitter.addWidget(dimensions_group)
        left_splitter.addWidget(expressions_group)

        # Set default sizes: 25% for top, 40% for middle, and remainder for bottom
        total_height = self.height()
        constant_height = int(0.25 * total_height)
        dimension_height = int(0.4 * total_height)
        expression_height = total_height - constant_height - dimension_height
        left_splitter.setSizes(
            [
                constant_height,
                dimension_height,
                expression_height,
            ]
        )

        # Create a left widget to contain the left splitter
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(left_splitter)
        left_widget.setLayout(left_layout)

        # Checkboxes
        self.usage_checkbox = QCheckBox("Where Used")
        self.sensitivity_checkbox = QCheckBox("Sensitivity")
        self.contribution_checkbox = QCheckBox("Tolerance Contribution")

        # Update button
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_results)

        # Horizontal layout for checkboxes and update button
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.usage_checkbox)
        checkbox_layout.addWidget(self.sensitivity_checkbox)
        checkbox_layout.addWidget(self.contribution_checkbox)
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(update_button)

        right_layout.addLayout(
            checkbox_layout
        )  # Add the checkbox layout to the right layout

        # Text box
        self.text_edit = QTextEdit()
        fixed_font = QFont("Consolas")
        fixed_font.setStyleHint(QFont.Monospace)
        fixed_font.setFixedPitch(True)
        fixed_font.setPointSize(10)
        self.text_edit.setFont(fixed_font)
        right_layout.addWidget(self.text_edit)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        left_size = int(0.475 * self.WINDOW_WIDTH)
        right_size = self.WINDOW_WIDTH - left_size
        splitter.setSizes([left_size, right_size])

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

        # Create Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")

        # Add actions to the File menu
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Open new analysis (Ctrl+N)")
        new_action.triggered.connect(self.new_analysis)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open input definitions (Ctrl+O)")
        open_action.triggered.connect(self.open_file)

        save_inputs_action = QAction("Save", self)
        save_inputs_action.setShortcut("Ctrl+S")
        save_inputs_action.setStatusTip("Save input definitions (Ctrl+S)")
        save_inputs_action.triggered.connect(self.save_inputs)

        save_inputs_as_action = QAction("Save As...", self)
        save_inputs_as_action.setStatusTip("Save input definitions as...")
        save_inputs_as_action.triggered.connect(self.save_inputs)

        export_action = QAction("Export", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export result to file (Ctrl+E)")
        export_action.triggered.connect(self.save_outputs)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_inputs_action)
        file_menu.addAction(save_inputs_as_action)
        file_menu.addAction(export_action)

        # Add actions to the Edit menu
        add_constant_action = QAction("Add constant", self)
        add_constant_action.setShortcut("Ctrl+1")
        add_constant_action.setStatusTip("Add new constant (Ctrl+1)")
        add_constant_action.triggered.connect(self.add_constant)

        add_dimension_action = QAction("Add dimension", self)
        add_dimension_action.setShortcut("Ctrl+2")
        add_dimension_action.setStatusTip("Add new dimension (Ctrl+2)")
        add_dimension_action.triggered.connect(self.add_dimension)

        add_expression_action = QAction("Add expression", self)
        add_expression_action.setShortcut("Ctrl+3")
        add_expression_action.setStatusTip("Add new constant (Ctrl+3)")
        add_expression_action.triggered.connect(self.add_expression)

        update_action = QAction("Update", self)
        update_action.setShortcut("Ctrl+R")
        update_action.setStatusTip("Update results (Ctrl+R)")
        update_action.triggered.connect(self.update_results)

        edit_menu.addAction(add_constant_action)
        edit_menu.addAction(add_dimension_action)
        edit_menu.addAction(add_expression_action)
        edit_menu.addSeparator()
        edit_menu.addAction(update_action)

        # Create a Status Bar
        self.statusBar().showMessage("Ready")

        # Standalone shortcuts
        constants_shortcut = QShortcut(QKeySequence("Ctrl+Shift+1"), self)
        constants_shortcut.activated.connect(self.switch_focus_to_constants)

        dimensions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+2"), self)
        dimensions_shortcut.activated.connect(self.switch_focus_to_dimensions)

        expressions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+3"), self)
        expressions_shortcut.activated.connect(self.switch_focus_to_expressions)

    def update_table_display(self):
        sample_data = [
            "D1",
            0.1,
            0.002,
            -0.0005,
            "W",
            "PRT-00000",
            "Here's an example note.",
        ]
        self.constants_widget.add_row(sample_data)

    def add_constant(self):
        new_data = ["Cxx", 0.0, "-"]
        self.constants_widget.add_row(new_data)

        if self.constants_widget.rowCount() > 0:
            last_row_index = self.constants_widget.rowCount() - 1
            self.constants_widget.setCurrentCell(last_row_index, 0)
            self.constants_widget.editItem(
                self.constants_widget.item(last_row_index, 0)
            )

    def delete_constant(self):
        selected_rows = sorted(
            set(index.row() for index in self.constants_widget.selectedIndexes()),
            reverse=True,
        )
        for row in selected_rows:
            self.constants_widget.removeRow(row)

    def add_dimension(self):
        new_data = ["Dxx", 0.0, 0.0, 0.0, "U", "-", "-"]
        self.dimensions_widget.add_row(new_data)

        if self.dimensions_widget.rowCount() > 0:
            last_row_index = self.dimensions_widget.rowCount() - 1
            self.dimensions_widget.setCurrentCell(last_row_index, 0)
            self.dimensions_widget.editItem(
                self.dimensions_widget.item(last_row_index, 0)
            )

    def delete_dimension(self):
        selected_rows = sorted(
            set(index.row() for index in self.dimensions_widget.selectedIndexes()),
            reverse=True,
        )
        for row in selected_rows:
            self.dimensions_widget.removeRow(row)

    def add_expression(self):
        new_data = ["Exx", "-", "", "", "W", "-"]
        self.expressions_widget.add_row(new_data)

        if self.expressions_widget.rowCount() > 0:
            last_row_index = self.expressions_widget.rowCount() - 1
            self.expressions_widget.setCurrentCell(last_row_index, 0)
            self.expressions_widget.editItem(
                self.expressions_widget.item(last_row_index, 0)
            )

    def delete_expression(self):
        selected_rows = sorted(
            set(index.row() for index in self.expressions_widget.selectedIndexes()),
            reverse=True,
        )
        for row in selected_rows:
            self.expressions_widget.removeRow(row)

    def update_results(self):
        c_data = self.constants_widget.get_all_data()
        d_data = self.dimensions_widget.get_all_data()
        e_data = self.expressions_widget.get_all_data()

        U = self.usage_checkbox.isChecked()
        S = self.sensitivity_checkbox.isChecked()
        T = self.contribution_checkbox.isChecked()

        try:
            print_lines = process_data(
                constants_data=c_data,
                dimensions_data=d_data,
                expressions_data=e_data,
                print_usage=U,
                conduct_sensitivity_analysis=S,
                conduct_tolerance_contribution=T,
            )

            self.text_edit.setPlainText("\n".join(print_lines))
            self.statusBar().showMessage("Updated results", 1500)
        except RuntimeError as r:
            self.show_non_fatal_error(r)
        except ValueError as v:
            self.show_non_fatal_error(v)
        except Exception as e:
            self.show_non_fatal_error(e)

    def new_analysis(self):
        if self.has_unsaved_changes():
            proceed = self.ask_to_save()

            if not proceed:
                return

        self.constants_widget.clear_all_data()
        self.dimensions_widget.clear_all_data()
        self.expressions_widget.clear_all_data()

        self.text_edit.setText("")

        self.SAVE_FILE = None

        self.statusBar().showMessage("New analysis", 1500)

    def ask_to_save(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Unsaved Changes")
        msg_box.setText(
            "You have unsaved changes. Do you want to continue without saving?"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # Show the message box and get the user's response
        response = msg_box.exec_()

        # Return True if the user chooses 'Yes', otherwise return False
        return response == QMessageBox.Yes

    def save_as_inputs(self):
        options = QFileDialog.Options()
        self.SAVE_FILE, _ = QFileDialog.getSaveFileName(
            self,
            "Save Input Definition",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options,
        )
        self.save_inputs_to_name(self.SAVE_FILE)

    def save_inputs(self):
        if not self.SAVE_FILE:
            options = QFileDialog.Options()
            self.SAVE_FILE, _ = QFileDialog.getSaveFileName(
                self,
                "Save Input Definition",
                "",
                "All Files (*);;Text Files (*.txt)",
                options=options,
            )
        self.save_inputs_to_name(self.SAVE_FILE)

    def save_inputs_to_name(self, file_name):
        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write("*CONSTANTS, VALUE, NOTE" + "\n")
                for row_data in self.constants_widget.get_all_data():
                    file.write(",".join(row_data) + "\n")

                file.write(
                    "*DIMENSIONS, NOMINAL, PLUS, MINUS, DISTRIBUTION, PART NUMBER, NOTE"
                    + "\n"
                )
                for row_data in self.dimensions_widget.get_all_data():
                    file.write(",".join(row_data) + "\n")

                file.write("*EXPRESSIONS, VALUE, LOWER, UPPER, METHOD, NOTE" + "\n")
                for row_data in self.expressions_widget.get_all_data():
                    file.write(",".join(row_data) + "\n")

                self.store_state_at_save()

    def store_state_at_save(self):
        self.CONTENTS_AT_SAVE = self.get_current_state()

    def has_unsaved_changes(self):
        return self.CONTENTS_AT_SAVE != self.get_current_state()

    def get_current_state(self):
        return [
            self.constants_widget.get_all_data(),
            self.dimensions_widget.get_all_data(),
            self.expressions_widget.get_all_data(),
        ]

    def open_file(self):
        options = QFileDialog.Options()
        self.SAVE_FILE, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options
        )
        self.open_file_from_name(self.SAVE_FILE)

    def open_file_from_name(self, file_name):
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.constants_widget.setRowCount(0)
                self.dimensions_widget.setRowCount(0)
                self.expressions_widget.setRowCount(0)

                current_widget = None
                split_limit = -1

                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("*CONSTANTS"):
                        current_widget = self.constants_widget
                        split_limit = 2
                    elif line.startswith("*DIMENSIONS"):
                        current_widget = self.dimensions_widget
                        split_limit = 6
                    elif line.startswith("*EXPRESSIONS"):
                        current_widget = self.expressions_widget
                        split_limit = 5
                    else:
                        if current_widget is not None:
                            data = line.split(",", split_limit)
                            current_widget.add_row(data)
                self.store_state_at_save()

    def save_outputs(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Outputs",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options,
        )
        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())

    def show_non_fatal_error(self, e):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)  # Set the icon to Warning
        msg_box.setWindowTitle("Error")
        if isinstance(e, (ValueError, RuntimeError)) and len(e.args) > 1:
            msg_box.setText(e.args[0])
            msg_box.setInformativeText("\n".join(e.args[1:]))
        else:
            msg_box.setText(f"Unexpected error: {e.args[0]}")
            tb_str = traceback.format_exc()
            msg_box.setInformativeText(f"{tb_str}")
        msg_box.setStandardButtons(QMessageBox.Ok)  # Set a standard OK button

        # Show the message box
        msg_box.exec_()

    def switch_focus_to_constants(self):
        self.constants_widget.setFocus()
        self.constants_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def switch_focus_to_dimensions(self):
        self.constants_widget.setFocus()
        self.constants_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def switch_focus_to_expressions(self):
        self.constants_widget.setFocus()
        self.constants_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
