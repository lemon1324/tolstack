import unittest
from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import QApplication
import os

from tolstack.gui.gui import MainWindow
from tolstack.AppConfig import AppConfig
from tolstack.gui.GUITypes import DataWidget, AnalysisWidget, OptionsWidget
from tolstack.gui.FileIO import *


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])  # Create an instance of the application

    def setUp(self):
        self.window = MainWindow()

        self.local_input_file_path = "validation_inputs/test_app_open_save.txt"

        with open(self.local_input_file_path, "r") as file:
            self.test_data = file.read()

    def test_open_and_save_file(self):
        temp_input_file = NamedTemporaryFile(delete=False, mode="w+t")
        temp_input_file.write(self.test_data)
        temp_input_file.close()

        # Open the temporary test file
        self.window.open_file(temp_input_file.name, forced=True)

        # Create another temporary file to save the output
        temp_output_file = NamedTemporaryFile(delete=False, mode="w+t")
        temp_output_file.close()

        # Save the inputs
        self.window.SAVE_FILE = temp_output_file.name
        self.window.save_inputs()

        # Read the contents of the saved file
        with open(temp_output_file.name, "r") as file:
            saved_data = file.read()

        # Clean up temporary files
        os.remove(temp_input_file.name)
        os.remove(temp_output_file.name)

        # Assert that the saved data matches the original test data
        self.assertEqual(saved_data.strip(), self.test_data.strip())


class TestFileIOFunctions(unittest.TestCase):

    def setUp(self):
        self.dummy_info = {
            OptionsWidget.UNITS: "inches",
            OptionsWidget.MAX_IMG_WIDTH: "6",
            OptionsWidget.MAX_IMG_HEIGHT: "4",
            OptionsWidget.FIND_IMAGES: False,
            OptionsWidget.WHERE_USED: True,
            OptionsWidget.SENSITIVITY: False,
            OptionsWidget.CONTRIBUTIONS: True,
            OptionsWidget.SHOW_PLOTS: False,
            OptionsWidget.IMAGE_FOLDER: "images",
            AnalysisWidget.TITLE: "Title",
            AnalysisWidget.DOCNO: "XXX-00000",
            AnalysisWidget.REVISION: "A",
            AnalysisWidget.DESCRIPTION: "Content\nwith\nmultiple\nlines.",
            DataWidget.CONSTANTS: [
                ["const1_name", "const1_value1", "const1_note"],
                ["const2_name", "const2_value1", "const2_note"],
            ],
            DataWidget.DIMENSIONS: [
                [
                    "dim1_name",
                    "dim1_nominal",
                    "dim1_plus",
                    "dim1_minus",
                    "dim1_distribution",
                    "dim1_part_number",
                    "dim1_note",
                ],
                [
                    "dim2_name",
                    "dim2_nominal",
                    "dim2_plus",
                    "dim2_minus",
                    "dim2_distribution",
                    "dim2_part_number",
                    "dim2_note",
                ],
            ],
            DataWidget.EXPRESSIONS: [
                [
                    "expr1_name",
                    "expr1_value",
                    "expr1_lower",
                    "expr1_upper",
                    "expr1_method",
                    "expr1_note",
                ],
                [
                    "expr2_name",
                    "expr2_value",
                    "expr2_lower",
                    "expr2_upper",
                    "expr2_method",
                    "expr2_note",
                ],
            ],
        }

    def test_save_open_functions(self):
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_filename = tmp_file.name

        try:
            save_to_name(tmp_filename, self.dummy_info)
            loaded_info = open_from_name(tmp_filename)

            self.assertEqual(self.dummy_info, loaded_info)
        finally:
            os.remove(tmp_filename)
