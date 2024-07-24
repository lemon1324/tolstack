import sys
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QTabWidget,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt, QItemSelectionModel

from PyQt5.QtGui import QFont, QKeySequence

from tolstack.compute_stack import process_data

import traceback

import markdown

import re

import os

from tolstack.AppConfig import AppConfig
from tolstack.GUIWidgets import *


class DataWidget(Enum):
    CONSTANTS = 0
    DIMENSIONS = 1
    EXPRESSIONS = 2


class MainWindow(QMainWindow):
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    SAVE_FILE = None
    CONTENTS_AT_SAVE = [[], [], []]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("tolstack")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout()

        self.main_splitter = QSplitter(
            Qt.Horizontal
        )  # This will allow resizing horizontally

        # Create Tab widget and add tabs
        self.tab_widget = QTabWidget()

        # First tab: Analysis Information
        analysis_widget = self.create_analysis_page()
        self.tab_widget.addTab(analysis_widget, "Analysis Information")

        # Second tab: Data definition
        data_widget = self.create_data_page()
        self.tab_widget.addTab(data_widget, "Data")

        output_widget = self.create_output_widget()

        self.main_splitter.addWidget(self.tab_widget)
        self.main_splitter.addWidget(output_widget)

        text_edit_width = self.text_edit.sizeHint().width()
        left_size = self.WINDOW_WIDTH - text_edit_width
        self.output_column_width = text_edit_width
        self.main_splitter.setSizes([left_size, self.output_column_width])

        main_layout.addWidget(self.main_splitter)
        central_widget.setLayout(main_layout)

        # Create Menu Bar
        self.setup_menu_bar()

        # Create a Status Bar
        self.statusBar().showMessage("Ready")

        # Standalone shortcuts
        self.setup_shortcuts()

        # Intercept window close to prompt for save
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.closeEvent = self.on_close_event

    def create_analysis_page(self):
        page = QWidget()
        analysis_layout = QVBoxLayout()
        analysis_layout.addWidget(QTextEdit("Placeholder"))
        analysis_layout.addWidget(QCheckBox("Checkbox 1"))
        analysis_layout.addWidget(QCheckBox("Checkbox 2"))
        analysis_layout.addWidget(QCheckBox("Checkbox 3"))
        page.setLayout(analysis_layout)

        return page

    def create_data_page(self):
        left_splitter = QSplitter(Qt.Vertical)

        groups_info = [
            ("CONSTANTS:", EditableConstantWidget, DataWidget.CONSTANTS),
            ("DIMENSIONS:", EditableDimensionWidget, DataWidget.DIMENSIONS),
            ("EXPRESSIONS:", EditableExpressionWidget, DataWidget.EXPRESSIONS),
        ]

        self.widgets = dict()

        for title, widget_class, key in groups_info:
            (group_widget, data_widget) = self.create_data_group(
                title,
                widget_class(),
            )
            left_splitter.addWidget(group_widget)
            self.widgets[key] = data_widget

        # Set default sizes: 25% for top, 40% for middle, and remainder for bottom
        total_height = self.height()
        constant_height = int(0.25 * total_height)
        dimension_height = int(0.4 * total_height)
        expression_height = total_height - constant_height - dimension_height
        left_splitter.setSizes([constant_height, dimension_height, expression_height])

        left_layout = QVBoxLayout()
        left_layout.addWidget(left_splitter)

        page = QWidget()
        page.setLayout(left_layout)

        return page

    def create_data_group(
        self,
        title,
        main_widget,
    ):
        add_button = QPushButton("+")
        add_button.clicked.connect(
            lambda: self.add_item(main_widget, InsertPosition.BELOW)
        )
        delete_button = QPushButton("-")
        delete_button.clicked.connect(lambda: self.delete_item(main_widget))

        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setFixedHeight(30)
        title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(add_button)
        header_layout.addWidget(delete_button)

        group_widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(main_widget)
        group_widget.setLayout(layout)

        return (group_widget, main_widget)

    def create_output_widget(self):
        layout = QVBoxLayout()

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

        layout.addLayout(checkbox_layout)  # Add the checkbox layout to the right layout

        # Text box
        fixed_font = QFont("Consolas")
        fixed_font.setStyleHint(QFont.Monospace)
        fixed_font.setFixedPitch(True)
        fixed_font.setPointSize(10)
        self.text_edit = EmWidthTextEdit(fixed_font, 85)
        layout.addWidget(self.text_edit)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def setup_shortcuts(self):
        """Setup standalone shortcuts."""
        constants_shortcut = QShortcut(QKeySequence("Ctrl+Shift+1"), self)
        constants_shortcut.activated.connect(
            lambda: self.switch_focus_to(DataWidget.CONSTANTS)
        )

        dimensions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+2"), self)
        dimensions_shortcut.activated.connect(
            lambda: self.switch_focus_to(DataWidget.DIMENSIONS)
        )

        expressions_shortcut = QShortcut(QKeySequence("Ctrl+Shift+3"), self)
        expressions_shortcut.activated.connect(
            lambda: self.switch_focus_to(DataWidget.EXPRESSIONS)
        )

        rename_shortcut = QShortcut(QKeySequence(Qt.Key_F2), self)
        rename_shortcut.activated.connect(lambda: self.rename_item(use_focused=True))

    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()

        file_options = [
            ("New", "Ctrl+N", "Open new analysis (Ctrl+N)", self.new_analysis),
            ("Open", "Ctrl+O", "Open input definitions (Ctrl+O)", self.open_file),
            ("Save", "Ctrl+S", "Save input definitions (Ctrl+S)", self.save_inputs),
            ("Save As...", "", "Save input definitions as...", self.save_as_inputs),
            ("Export", "Ctrl+E", "Export result to file (Ctrl+E)", self.save_outputs),
        ]

        edit_options = [
            ("Update", "Ctrl+R", "Update results pane (Ctrl+R)", self.update_results),
            ("SEP", "", "", None),
            (
                "Add constant",
                "Ctrl+1",
                "Add new constant (Ctrl+1)",
                lambda: self.add_item(self.widgets[DataWidget.CONSTANTS]),
            ),
            (
                "Add dimension",
                "Ctrl+2",
                "Add new constant (Ctrl+2)",
                lambda: self.add_item(self.widgets[DataWidget.DIMENSIONS]),
            ),
            (
                "Add expression",
                "Ctrl+3",
                "Add new expression (Ctrl+3)",
                lambda: self.add_item(self.widgets[DataWidget.EXPRESSIONS]),
            ),
            ("SEP", "", "", None),
            ("Rename item", "", "Rename a constant or dimension", self.rename_item),
        ]

        help_options = [
            ("Help", "F1", "Show help", self.display_help),
            ("About", "", "About this application", self.display_about),
        ]

        menus = {"File": file_options, "Edit": edit_options, "Help": help_options}

        for name, menu_items in menus.items():
            current_menu = menubar.addMenu(name)
            for menu_item in menu_items:
                if menu_item[0] == "SEP":
                    current_menu.addSeparator()
                    continue

                current_action = QAction(menu_item[0], self)
                if menu_item[1]:
                    current_action.setShortcut(menu_item[1])
                if menu_item[2]:
                    current_action.setStatusTip(menu_item[2])
                current_action.triggered.connect(menu_item[3])
                current_menu.addAction(current_action)

        return

    def add_item(
        self, widget: EditableTableWidget, position: InsertPosition = InsertPosition.ADD
    ):
        # switch so user can see the item they just added
        self.tab_widget.setCurrentIndex(1)
        widget.insert_row(position, select_after=True)

    def delete_item(self, widget):
        selected_rows = sorted(
            set(index.row() for index in widget.selectedIndexes()),
            reverse=True,
        )
        for row in selected_rows:
            widget.removeRow(row)

    def update_results(self):
        c_data = self.widgets[DataWidget.CONSTANTS].get_all_data()
        d_data = self.widgets[DataWidget.DIMENSIONS].get_all_data()
        e_data = self.widgets[DataWidget.EXPRESSIONS].get_all_data()

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

        self.widgets[DataWidget.CONSTANTS].clear_all_data()
        self.widgets[DataWidget.DIMENSIONS].clear_all_data()
        self.widgets[DataWidget.EXPRESSIONS].clear_all_data()

        self.text_edit.setText("")

        self.SAVE_FILE = None

        self.statusBar().showMessage("New analysis", 1500)

    def rename_item(self, selected_item=None, use_focused=False):
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
                self.widgets[DataWidget.CONSTANTS].has_key(new_name)
                or self.widgets[DataWidget.DIMENSIONS].has_key(new_name)
                or self.widgets[DataWidget.EXPRESSIONS].has_key(new_name)
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

        # pre-populate entries if operating in that mode
        if selected_item:  # called with a specific item to rename
            original_item = selected_item
        elif use_focused:
            original_item = (
                self.widgets[DataWidget.CONSTANTS].currentItem()
                or self.widgets[DataWidget.DIMENSIONS].currentItem()
            )
        if original_item:
            row = original_item.row()
            widget = original_item.tableWidget()
            original_item = widget.item(row, 0)
            old_name_input.setText(original_item.text())

            new_name_input.setFocus()  # place cursor in logcal spot when pre-filling

        if dialog.exec_() == QDialog.Accepted:
            old_name = old_name_input.text().strip()
            new_name = new_name_input.text().strip()

            renamed = False

            for widget in [
                self.widgets[DataWidget.CONSTANTS],
                self.widgets[DataWidget.DIMENSIONS],
            ]:
                for row in range(widget.rowCount()):
                    item = widget.item(row, 0)
                    if item and item.text() == old_name:
                        item.setText(new_name)
                        renamed = True

            if renamed:
                for row in range(self.widgets[DataWidget.EXPRESSIONS].rowCount()):
                    item = self.widgets[DataWidget.EXPRESSIONS].item(row, 1)
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
                file.write(
                    f"*VERSIONINFO, {AppConfig.app_version}, {AppConfig.file_format_version}"
                    + "\n",
                )
                file.write("*CONSTANTS, VALUE, NOTE" + "\n")
                for row_data in self.widgets[DataWidget.CONSTANTS].get_all_data():
                    file.write(",".join(row_data) + "\n")

                file.write(
                    "*DIMENSIONS, NOMINAL, PLUS, MINUS, DISTRIBUTION, PART NUMBER, NOTE"
                    + "\n"
                )
                for row_data in self.widgets[DataWidget.DIMENSIONS].get_all_data():
                    file.write(",".join(row_data) + "\n")

                file.write("*EXPRESSIONS, VALUE, LOWER, UPPER, METHOD, NOTE" + "\n")
                for row_data in self.widgets[DataWidget.EXPRESSIONS].get_all_data():
                    file.write(",".join(row_data) + "\n")

                self.store_state_at_save()
                self.statusBar().showMessage(f"Saved to {file_name}", 3000)

    def store_state_at_save(self):
        self.CONTENTS_AT_SAVE = self.get_current_state()

    def has_unsaved_changes(self):
        return self.CONTENTS_AT_SAVE != self.get_current_state()

    def get_current_state(self):
        return [
            self.widgets[DataWidget.CONSTANTS].get_all_data(),
            self.widgets[DataWidget.DIMENSIONS].get_all_data(),
            self.widgets[DataWidget.EXPRESSIONS].get_all_data(),
        ]

    def open_file(self):
        if self.has_unsaved_changes():
            proceed = self.ask_to_save()

            if not proceed:
                return

        options = QFileDialog.Options()
        self.SAVE_FILE, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options
        )
        self.open_file_from_name(self.SAVE_FILE)

    def open_file_from_name(self, file_name):
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.widgets[DataWidget.CONSTANTS].setRowCount(0)
                self.widgets[DataWidget.DIMENSIONS].setRowCount(0)
                self.widgets[DataWidget.EXPRESSIONS].setRowCount(0)

                current_widget = None
                split_limit = -1

                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("*CONSTANTS"):
                        current_widget = self.widgets[DataWidget.CONSTANTS]
                        split_limit = 2
                    elif line.startswith("*DIMENSIONS"):
                        current_widget = self.widgets[DataWidget.DIMENSIONS]
                        split_limit = 6
                    elif line.startswith("*EXPRESSIONS"):
                        current_widget = self.widgets[DataWidget.EXPRESSIONS]
                        split_limit = 5
                    else:
                        if current_widget is not None:
                            data = line.split(",", split_limit)
                            current_widget.insert_row(InsertPosition.ADD, data)
                self.store_state_at_save()

                self.text_edit.setText("")

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
            with open(AppConfig.path_to_help, "r", encoding="utf-8") as file:
                md_content = file.read()

            html_content = markdown.markdown(md_content, extensions=["extra"])

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
            error_msg_box.setInformativeText("\n".join(os.listdir(".")))
            error_msg_box.exec_()

    def display_about(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("About tolstack")

        text = (
            "<h3>tolstack</h3>"
            f"<p>Version: {AppConfig.app_version}<br>"
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

    def switch_focus_to(self, widget_type):
        """Switch focus to a specific widget based on WidgetType."""
        if widget_type == DataWidget.CONSTANTS:
            widget = self.widgets[DataWidget.CONSTANTS]
        elif widget_type == DataWidget.DIMENSIONS:
            widget = self.widgets[DataWidget.DIMENSIONS]
        elif widget_type == DataWidget.EXPRESSIONS:
            widget = self.widgets[DataWidget.EXPRESSIONS]
        else:
            raise ValueError("Invalid widget type for switch_focus_to method")

        widget.setFocus()
        widget.setCurrentCell(0, 0, QItemSelectionModel.ClearAndSelect)

    def keep_output_panel_width_fixed(self):
        left_size = self.width() - self.output_column_width
        right_size = self.output_column_width
        self.main_splitter.setSizes([left_size, right_size])

    def resizeEvent(self, event):
        self.keep_output_panel_width_fixed()
        super().resizeEvent(event)

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
