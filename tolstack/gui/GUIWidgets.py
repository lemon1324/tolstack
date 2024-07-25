from PyQt5.QtWidgets import (
    QAction,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QPoint

from PyQt5.QtGui import QFontMetrics

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
