# Standard Library Imports
import sys
import traceback
import re
import os

# Third-Party Library Imports
import markdown
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
    QFrame,
    QWidget,
)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QFont, QKeySequence

# Local Application Imports
from tolstack.compute_stack import process_info, process_info_to_pdf
from tolstack.AppConfig import AppConfig
from tolstack.gui.GUIWidgets import *
from tolstack.gui.FileIO import save_to_name, open_from_name
from tolstack.gui.GUITypes import *
from tolstack.gui.Qt5Utils import get_widget_text, set_widget_text


class MainWindow(QMainWindow):
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    SAVE_FILE = None
    CONTENTS_AT_SAVE = [[], [], []]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("tolstack")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.widgets = dict()

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

        # Third tab: Options definition
        options_widget = self.create_options_page()
        self.tab_widget.addTab(options_widget, "Options")

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

        # Store initial state to prevent spurious unsaved chages on start
        self.store_state_at_save()

    def create_analysis_page(self):
        page = QWidget()
        analysis_layout = QVBoxLayout()

        # Define a list of tuples with field specifications
        # label, input class, input reference, default input
        fields = [
            ("Title:", QLineEdit, AnalysisWidget.TITLE, ""),
            ("Document Number:", QLineEdit, AnalysisWidget.DOCNO, ""),
            ("Revision:", QLineEdit, AnalysisWidget.REVISION, ""),
        ]

        label_widgets = []

        # Loop through the defined fields and create layouts and widgets
        for label_text, label_class, widget_key, default_text in fields:
            layout = QHBoxLayout()
            label = QLabel(label_text)
            self.widgets[widget_key] = label_class()
            self.widgets[widget_key].setText(default_text)
            layout.addWidget(label)
            layout.addWidget(self.widgets[widget_key])

            analysis_layout.addLayout(layout)
            label_widgets.append(label)

        # Calculate the maximum label width
        max_label_width = max(label.sizeHint().width() for label in label_widgets)

        # Set all labels to this maximum width
        for label in label_widgets:
            label.setFixedWidth(max_label_width)

        # Description Field
        description_label = QLabel("Description:")
        self.widgets[AnalysisWidget.DESCRIPTION] = QTextEdit()

        # Adding description field to the main layout
        analysis_layout.addWidget(description_label)
        analysis_layout.addWidget(self.widgets[AnalysisWidget.DESCRIPTION])

        # Set the main layout to the page
        page.setLayout(analysis_layout)
        return page

    def create_data_page(self):
        left_splitter = QSplitter(Qt.Vertical)

        groups_info = [
            ("CONSTANTS:", EditableConstantWidget, DataWidget.CONSTANTS),
            ("DIMENSIONS:", EditableDimensionWidget, DataWidget.DIMENSIONS),
            ("EXPRESSIONS:", EditableExpressionWidget, DataWidget.EXPRESSIONS),
        ]

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

    def create_options_page(self):
        page = QWidget()
        options_layout = QVBoxLayout()
        options_layout.setAlignment(Qt.AlignTop)

        # Define a list of tuples with labeled field specifications:
        fields = [
            ("Units:", QLineEdit, OptionsWidget.UNITS, "inches"),
        ]

        # Define a list of tuples with labeled field specifications for checkboxes:
        checkboxes = [
            (
                "Include dimension images in report",
                QCheckBox,
                OptionsWidget.FIND_IMAGES,
            ),
        ]

        label_widgets = []

        # Loop through the defined fields and create layouts and widgets
        for item_label, item_class, widget_key, default_text in fields:
            layout = QHBoxLayout()
            label = QLabel(item_label)
            self.widgets[widget_key] = item_class()
            self.widgets[widget_key].setText(default_text)
            layout.addWidget(label)
            layout.addWidget(self.widgets[widget_key])

            options_layout.addLayout(layout)
            label_widgets.append(label)

        # Calculate the maximum label width
        max_label_width = max(label.sizeHint().width() for label in label_widgets)

        # Set all labels to this maximum width
        for label in label_widgets:
            label.setFixedWidth(max_label_width)

        options_layout.addSpacing(15)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        options_layout.addWidget(line)
        options_layout.addSpacing(10)

        # Checkbox Fields
        for item_label, item_class, widget_key in checkboxes:
            self.widgets[widget_key] = item_class(item_label)
            options_layout.addWidget(self.widgets[widget_key])

        # Set the main layout to the page
        page.setLayout(options_layout)
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
        self.widgets[OptionsWidget.WHERE_USED] = QCheckBox("Where Used")
        self.widgets[OptionsWidget.SENSITIVITY] = QCheckBox("Sensitivity")
        self.widgets[OptionsWidget.CONTRIBUTIONS] = QCheckBox("Tolerance Contribution")

        # Update button
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_results)

        # Horizontal layout for checkboxes and update button
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.widgets[OptionsWidget.WHERE_USED])
        checkbox_layout.addWidget(self.widgets[OptionsWidget.SENSITIVITY])
        checkbox_layout.addWidget(self.widgets[OptionsWidget.CONTRIBUTIONS])
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
            (
                "Open",
                "Ctrl+O",
                "Open input definitions (Ctrl+O)",
                lambda: self.open_file(),
            ),
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
        info = self.get_analysis_information()

        try:
            # TODO: progress bar so if this takes a long time it doesn't unnerve user.
            print_lines = process_info(info)

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

    def generate_pdf(self, filename):
        info = self.get_analysis_information()

        try:
            # TODO: progress bar so if this takes a long time it doesn't unnerve user.
            process_info_to_pdf(info, filename)

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

        self.widgets[AnalysisWidget.TITLE].setText("")
        self.widgets[AnalysisWidget.DOCNO].setText("")
        self.widgets[AnalysisWidget.REVISION].setText("")
        self.widgets[AnalysisWidget.DESCRIPTION].setText("")

        self.SAVE_FILE = None

        self.store_state_at_save()

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
        info = self.get_analysis_information()
        save_to_name(self.SAVE_FILE, info)
        self.update_save_info(self.SAVE_FILE)

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
        info = self.get_analysis_information()
        save_to_name(self.SAVE_FILE, info)
        self.update_save_info(self.SAVE_FILE)

    def update_save_info(self, file_name):
        self.store_state_at_save()
        self.statusBar().showMessage(f"Saved to {file_name}", 3000)

    def get_analysis_information(self):
        info = dict()

        # Collect actual data
        for key in DataWidget:
            info[key] = self.widgets[key].get_all_data()

        # Collect analysis information
        for key in AnalysisWidget:
            widget = self.widgets[key]
            info[key] = (
                get_widget_text(widget)
                if not is_boolean_option(key)
                else widget.isChecked()
            )

        # Collect options information
        for key in OptionsWidget:
            widget = self.widgets[key]
            info[key] = (
                get_widget_text(widget)
                if not is_boolean_option(key)
                else widget.isChecked()
            )

        return info

    def set_analysis_information(self, info):
        # Set data in widgets
        for key in DataWidget:
            self.widgets[key].setRowCount(0)
            for row in info[key]:
                self.widgets[key].insert_row(InsertPosition.ADD, row)

        self.store_state_at_save()

        self.text_edit.setText("")

        # Set the analysis information
        for key in AnalysisWidget:
            set_widget_text(self.widgets[key], info[key])

        # Set options (mostly checkboxes)
        for key in OptionsWidget:
            if is_boolean_option(key):
                self.widgets[key].setChecked(info[key])
            else:
                set_widget_text(self.widgets[key], info[key])

    def store_state_at_save(self):
        self.CONTENTS_AT_SAVE = self.get_current_state()

    def has_unsaved_changes(self):
        return self.CONTENTS_AT_SAVE != self.get_current_state()

    # This is the same as get_analysis_information, but in list form to allow comparison to the stored state
    def get_current_state(self):
        info = self.get_analysis_information()
        return [info[key] for key in info.keys()]

    def open_file(self, file_name=None, forced=False):
        if self.has_unsaved_changes() and not forced:
            proceed = self.ask_to_save()

            if not proceed:
                return

        if file_name is None:
            options = QFileDialog.Options()
            self.SAVE_FILE, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "",
                "All Files (*);;Text Files (*.txt)",
                options=options,
            )
        else:
            self.SAVE_FILE = file_name
        try:
            if not self.SAVE_FILE:
                return

            info = open_from_name(self.SAVE_FILE)
            self.set_analysis_information(info)
            self.store_state_at_save()
        except RuntimeError as r:
            self.show_non_fatal_error(r)
        except ValueError as v:
            self.show_non_fatal_error(v)
        except Exception as e:
            self.show_non_fatal_error(e)

    def save_outputs(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Outputs",
            "",
            "All Files (*);;Text Files (*.txt);;PDF Files (*.pdf)",
            options=options,
        )
        if file_name:
            if file_name.lower().endswith(".pdf"):
                self.generate_pdf(file_name)
                self.statusBar().showMessage(f"Saved output pdf to {file_name}", 3000)
                # TODO: for pdf output, add progress bar so we don't unnerve the user.
            else:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(self.text_edit.toPlainText())
                    self.statusBar().showMessage(
                        f"Saved output text to {file_name}", 3000
                    )

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
