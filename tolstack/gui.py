import sys
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QItemSelectionModel, QPoint

from PyQt5.QtGui import QFont, QKeySequence, QFontMetrics

from tolstack.compute_stack import process_data

import traceback

import markdown

import re

from enum import Enum


class InsertPosition(Enum):
    ADD = 1
    ABOVE = 2
    BELOW = 3


class EditableTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

        self.DEFAULT_DATA = [""] * columns
        self.ITEM_NAME = "item"
        self.WORD_WRAP = False

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos: QPoint):
        index = self.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()

        # Create the context menu
        context_menu = QMenu(self)

        # Create actions for inserting rows
        insert_above_action = QAction(f"Insert {self.ITEM_NAME} above", self)
        insert_below_action = QAction(f"Insert {self.ITEM_NAME} below", self)

        # Connect the actions to slots
        insert_above_action.triggered.connect(
            lambda: self.insert_row(
                position=InsertPosition.ABOVE, target_row=row, select_after=True
            )
        )
        insert_below_action.triggered.connect(
            lambda: self.insert_row(
                position=InsertPosition.BELOW, target_row=row, select_after=True
            )
        )

        # Add actions to the context menu
        context_menu.addAction(insert_above_action)
        context_menu.addAction(insert_below_action)

        # Add separator
        context_menu.addSeparator()

        # Create actions for moving rows up and down
        move_to_top_action = QAction("Move to top", self)
        move_up_action = QAction("Move up", self)
        move_down_action = QAction("Move down", self)
        move_to_bottom_action = QAction("Move to bottom", self)

        # Connect the actions to slots
        move_to_top_action.triggered.connect(lambda: self.move_row(row, 0))
        move_up_action.triggered.connect(lambda: self.move_row(row, row - 1))
        move_down_action.triggered.connect(lambda: self.move_row(row, row + 1))
        move_to_bottom_action.triggered.connect(
            lambda: self.move_row(row, self.rowCount() - 1)
        )

        # Add actions to the context menu
        context_menu.addAction(move_to_top_action)
        context_menu.addAction(move_up_action)
        context_menu.addAction(move_down_action)
        context_menu.addAction(move_to_bottom_action)

        # Show the context menu at the cursor position
        context_menu.exec_(self.viewport().mapToGlobal(pos))

    def insert_row(
        self,
        position: InsertPosition = InsertPosition.ADD,
        data=None,
        target_row=-1,
        select_after=False,
    ):
        if data is None:
            data = self.DEFAULT_DATA

        # If the table is empty, always insert at position 0
        if self.rowCount() == 0:
            row_position = 0
            self.insertRow(row_position)
        else:
            if target_row == -1:
                target_row = self.currentRow()

            row_position = None  # Initialize row_position to None

            match position:
                case InsertPosition.ADD:
                    row_position = self.rowCount()
                    self.insertRow(row_position)
                case InsertPosition.ABOVE:
                    if target_row != -1:
                        self.insertRow(target_row)
                        row_position = target_row
                    else:
                        return  # No row selected
                case InsertPosition.BELOW:
                    if target_row != -1:
                        self.insertRow(target_row + 1)
                        row_position = target_row + 1
                    else:
                        return  # No row selected
                case _:
                    raise ValueError(f"Invalid position: {position}")

        self._set_row_data(row_position, data)
        if select_after:
            if self.rowCount() > 0:
                self.setCurrentCell(row_position, 0)
                self.editItem(self.item(row_position, 0))

        return row_position

    def move_row(self, source_row: int, target_row: int):
        if (
            source_row == target_row
            or source_row < 0
            or target_row < 0
            or source_row >= self.rowCount()
            or target_row >= self.rowCount()
        ):
            return  # Invalid parameters or no movement needed

        # Get data from the source row
        source_data = [
            self.item(source_row, col).text() if self.item(source_row, col) else ""
            for col in range(self.columnCount())
        ]

        self.insert_row(
            position=(
                InsertPosition.BELOW
                if target_row > source_row
                else InsertPosition.ABOVE
            ),
            data=source_data,
            target_row=target_row,
        )

        # Remove the original row (adjust the index if necessary)
        self.removeRow(source_row if target_row > source_row else source_row + 1)

    def _set_row_data(self, row_position, data):
        for column, item in enumerate(data):
            if column < self.columnCount():  # Ensure we don't exceed the column count
                table_item = QTableWidgetItem(str(item))
                self.setItem(row_position, column, table_item)
                self.item(row_position, column).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
                )

                # Enable word wrapping for the last column if set
                if column == self.columnCount() - 1 and self.WORD_WRAP:
                    table_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    self._adjustRowHeight(row_position)

    def _adjustRowHeight(self, row_position):
        max_height = 0
        for column in range(self.columnCount()):
            table_item = self.item(row_position, column)
            if table_item is not None:
                text = table_item.text()
                font_metrics = QFontMetrics(table_item.font())
                rect = font_metrics.boundingRect(
                    0, 0, self.columnWidth(column), 0, Qt.TextWordWrap, text
                )
                max_height = max(max_height, rect.height())

        self.setRowHeight(row_position, max_height)

    def has_key(self, key: str) -> bool:
        """
        Check if any cell in the first column contains the exact string 'key'.
        :param key: The string to search for.
        :return: True if found, False otherwise.
        """
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and item.text() == key:
                return True
        return False

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
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            selected_items = self.selectedItems()
            if selected_items:
                first_selected_item = selected_items[0]
                if self.state() != QAbstractItemView.EditingState:
                    self.editItem(first_selected_item)
        else:
            super().keyPressEvent(event)


class EditableConstantWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)

        self.DEFAULT_DATA = ["Cxx", 0.0, "-"]
        self.ITEM_NAME = "constant"

        self.setHorizontalHeaderLabels(["Name", "Value", "Note"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            self.columnCount() - 1, QHeaderView.Stretch
        )

        # Set default column sizes
        default_column_widths = [50, 55, 420]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class EditableDimensionWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 7, parent)

        self.DEFAULT_DATA = ["Dxx", 0.0, 0.0, 0.0, "U", "-", "-"]
        self.ITEM_NAME = "dimension"

        self.setHorizontalHeaderLabels(
            ["Name", "Nominal", "Plus", "Minus", "D", "PN", "Note"]
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            self.columnCount() - 1, QHeaderView.Stretch
        )

        # Set default column sizes
        default_column_widths = [50, 55, 55, 55, 10, 65, 210]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class EditableExpressionWidget(EditableTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 6, parent)

        self.DEFAULT_DATA = ["Exx", "-", "", "", "W", "-"]
        self.ITEM_NAME = "expression"

        self.setHorizontalHeaderLabels(["Name", "Value", "Lower", "Upper", "M", "Note"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            self.columnCount() - 1, QHeaderView.Stretch
        )

        # Set default column sizes
        default_column_widths = [50, 55, 55, 55, 10, 275]
        for column, width in enumerate(default_column_widths):
            self.setColumnWidth(column, width)


class EmWidthTextEdit(QTextEdit):
    def __init__(self, font, em_width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(font)
        self.setEmWidth(em_width)

    def setEmWidth(self, em_width):
        # Get the default font metrics
        font_metrics = QFontMetrics(self.font())

        # Width of one em in pixels
        em_pixel_width = font_metrics.width("m")

        # Calculate the total width in pixels
        total_width = em_pixel_width * em_width

        # Set the fixed width
        self.setFixedWidth(total_width)


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
        self.add_constant_button.clicked.connect(
            lambda: self.add_item(self.constants_widget, InsertPosition.BELOW)
        )
        self.delete_constant_button.clicked.connect(
            lambda: self.delete_item(self.constants_widget)
        )

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
        self.add_dimension_button.clicked.connect(
            lambda: self.add_item(self.dimensions_widget, InsertPosition.BELOW)
        )
        self.delete_dimension_button.clicked.connect(
            lambda: self.delete_item(self.dimensions_widget)
        )

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
        self.add_expression_button.clicked.connect(
            lambda: self.add_item(self.expressions_widget, InsertPosition.BELOW)
        )
        self.delete_expression_button.clicked.connect(
            lambda: self.delete_item(self.expressions_widget)
        )

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
        fixed_font = QFont("Consolas")
        fixed_font.setStyleHint(QFont.Monospace)
        fixed_font.setFixedPitch(True)
        fixed_font.setPointSize(10)
        self.text_edit = EmWidthTextEdit(fixed_font, 85)
        text_edit_width = self.text_edit.sizeHint().width()
        right_layout.addWidget(self.text_edit)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        left_size = self.WINDOW_WIDTH - text_edit_width
        right_size = text_edit_width
        splitter.setSizes([left_size, right_size])

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

        # Create Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        help_menu = menubar.addMenu("Help")

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
        save_inputs_as_action.triggered.connect(self.save_as_inputs)

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
        update_action = QAction("Update", self)
        update_action.setShortcut("Ctrl+R")
        update_action.setStatusTip("Update results (Ctrl+R)")
        update_action.triggered.connect(self.update_results)

        add_constant_action = QAction("Add constant", self)
        add_constant_action.setShortcut("Ctrl+1")
        add_constant_action.setStatusTip("Add new constant (Ctrl+1)")
        add_constant_action.triggered.connect(
            lambda: self.add_item(self.constants_widget)
        )

        add_dimension_action = QAction("Add dimension", self)
        add_dimension_action.setShortcut("Ctrl+2")
        add_dimension_action.setStatusTip("Add new dimension (Ctrl+2)")
        add_dimension_action.triggered.connect(
            lambda: self.add_item(self.dimensions_widget)
        )

        add_expression_action = QAction("Add expression", self)
        add_expression_action.setShortcut("Ctrl+3")
        add_expression_action.setStatusTip("Add new expression (Ctrl+3)")
        add_expression_action.triggered.connect(
            lambda: self.add_item(self.expressions_widget)
        )

        rename_action = QAction("Rename item", self)
        # rename_action.setShortcut("Ctrl+R")
        rename_action.setStatusTip("Rename a constant or dimension.")
        rename_action.triggered.connect(self.rename_item)

        edit_menu.addAction(update_action)
        edit_menu.addSeparator()
        edit_menu.addAction(add_constant_action)
        edit_menu.addAction(add_dimension_action)
        edit_menu.addAction(add_expression_action)
        edit_menu.addSeparator()
        edit_menu.addAction(rename_action)

        # Add actions to the Help menu
        help_action = QAction("Help", self)
        help_action.setStatusTip("Show help")
        help_action.triggered.connect(self.display_help)

        about_action = QAction("About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.display_about)

        help_menu.addAction(help_action)
        help_menu.addAction(about_action)

        # Create a Status Bar
        self.statusBar().showMessage("Ready")

        # Standalone shortcuts
        constants_shortcut = QShortcut(QKeySequence("Ctrl+Shift+1"), self)
        constants_shortcut.activated.connect(self.switch_focus_to_constants)

        dimensions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+2"), self)
        dimensions_shortcut.activated.connect(self.switch_focus_to_dimensions)

        expressions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+3"), self)
        expressions_shortcut.activated.connect(self.switch_focus_to_expressions)

        # Intercept window close to prompt for save
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.closeEvent = self.on_close_event

    # def update_table_display(self):
    #     sample_data = [
    #         "D1",
    #         0.1,
    #         0.002,
    #         -0.0005,
    #         "W",
    #         "PRT-00000",
    #         "Here's an example note.",
    #     ]
    #     self.constants_widget.add_row(sample_data)

    def add_item(
        self, widget: EditableTableWidget, position: InsertPosition = InsertPosition.ADD
    ):
        widget.insert_row(position, select_after=True)

    def delete_item(self, widget):
        selected_rows = sorted(
            set(index.row() for index in widget.selectedIndexes()),
            reverse=True,
        )
        for row in selected_rows:
            widget.removeRow(row)

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

            saved_scroll = self.text_edit.verticalScrollBar().value()
            self.text_edit.setPlainText("\n".join(print_lines))
            self.text_edit.verticalScrollBar().setValue(saved_scroll)

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

    def rename_item(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Rename Item")

        layout = QVBoxLayout()

        old_name_label = QLabel("Enter old name:")
        old_name_input = QLineEdit()
        layout.addWidget(old_name_label)
        layout.addWidget(old_name_input)

        new_name_label = QLabel("Enter new name:")
        new_name_input = QLineEdit()
        layout.addWidget(new_name_label)
        layout.addWidget(new_name_input)

        button_layout = QHBoxLayout()

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def on_ok_clicked():
            old_name = old_name_input.text().strip()
            new_name = new_name_input.text().strip()

            if not old_name:
                QMessageBox.warning(
                    self, "Invalid Operation", "Old name cannot be empty."
                )
                return

            if not new_name:
                QMessageBox.warning(
                    self, "Invalid Operation", "New name cannot be empty."
                )
                return

            # Check if new_name already exists in any of the three widgets
            if (
                self.constants_widget.has_key(new_name)
                or self.dimensions_widget.has_key(new_name)
                or self.expressions_widget.has_key(new_name)
            ):

                reply = QMessageBox.question(
                    self,
                    "Name Conflict",
                    "The new name already exists. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    return

            # If both inputs are valid and user chooses to proceed, accept the dialog
            dialog.accept()

        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            old_name = old_name_input.text().strip()
            new_name = new_name_input.text().strip()

            renamed = False

            for widget in [self.constants_widget, self.dimensions_widget]:
                for row in range(widget.rowCount()):
                    item = widget.item(row, 0)
                    if item and item.text() == old_name:
                        item.setText(new_name)
                        renamed = True

            if renamed:
                for row in range(self.expressions_widget.rowCount()):
                    item = self.expressions_widget.item(row, 1)
                    if item:
                        item_text = item.text()
                        new_item_text = re.sub(
                            rf"\b{re.escape(old_name)}\b", new_name, item_text
                        )
                        item.setText(new_item_text)

            if renamed:
                QMessageBox.information(
                    self, "Success", f"{old_name} successfully renamed to {new_name}."
                )
            else:
                QMessageBox.warning(self, "Error", f"{old_name} not found.")

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
                self.statusBar().showMessage(f"Saved to {file_name}", 3000)

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
                            current_widget.insert_row(InsertPosition.ADD, data)
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

    def display_help(self):
        try:
            with open("tolstack/help.md", "r") as file:
                md_content = file.read()

            html_content = markdown.markdown(md_content)

            # Create a custom dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Help")

            dialog.resize(800, 600)

            layout = QVBoxLayout(dialog)

            # Add QTextEdit to handle HTML content
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setHtml(html_content)
            layout.addWidget(text_edit)

            # Add a button to close the dialog
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec_()
        except Exception as e:
            error_msg_box = QMessageBox(self)
            error_msg_box.setIcon(QMessageBox.Critical)
            error_msg_box.setWindowTitle("Error")
            error_msg_box.setText(f"Error loading help content:\n{e}")
            error_msg_box.exec_()

    def display_about(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("About tolstack")

        text = (
            "<h3>tolstack</h3>"
            "<p>Version: 0.4.0<br>"
            "Author: S.A. Suresh (lemon1324)<br>"
            "License: MIT</p>"
            "<p>This application is licensed under the MIT License.</p>"
            "<p>For more information, visit the <a href='https://github.com/lemon1324/tolstack'>GitHub repository</a>.</p>"
            "<p><b>Submitting Bug Reports:</b></p>"
            "<ul>"
            "<li>Check if the issue has already been reported.</li>"
            "<li>Provide a clear description of the problem.</li>"
            "<li>Include steps to reproduce the issue.</li>"
            "<li>Attach relevant input files, logs, or screenshots if applicable.</li>"
            "</ul>"
        )

        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def switch_focus_to_constants(self):
        self.constants_widget.setFocus()
        self.constants_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def switch_focus_to_dimensions(self):
        self.dimensions_widget.setFocus()
        self.dimensions_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def switch_focus_to_expressions(self):
        self.expressions_widget.setFocus()
        self.expressions_widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def on_close_event(self, event):
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to exit without saving?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                self.save_inputs()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
