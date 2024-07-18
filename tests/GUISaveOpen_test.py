import unittest
from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import QApplication
import os

from tolstack.gui import MainWindow
from tolstack.AppConfig import AppConfig


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])  # Create an instance of the application

    def setUp(self):
        self.window = MainWindow()

    def test_open_and_save_file(self):
        test_data = f"""*VERSIONINFO, {AppConfig.app_version}, {AppConfig.file_format_version}
*CONSTANTS, VALUE, NOTE
name1,10,note1
name2,20,note2
*DIMENSIONS, NOMINAL, PLUS, MINUS, DISTRIBUTION, PART NUMBER, NOTE
dim1,1.0,0.1,-0.1,D,PN001,noteA
dim2,2.0,0.2,-0.2,D,PN002,noteB
*EXPRESSIONS, VALUE, LOWER, UPPER, METHOD, NOTE
exp1,100,90,110,M,noteX
exp2,200,180,220,M,noteY
"""

        # Create a temporary file with test data
        temp_input_file = NamedTemporaryFile(delete=False, mode="w+t")
        temp_input_file.write(test_data)
        temp_input_file.close()

        # Open the temporary test file
        self.window.open_file_from_name(temp_input_file.name)

        # Create another temporary file to save the output
        temp_output_file = NamedTemporaryFile(delete=False, mode="w+t")
        temp_output_file.close()

        # Save the inputs
        self.window.save_inputs_to_name(temp_output_file.name)

        # Read the contents of the saved file
        with open(temp_output_file.name, "r") as file:
            saved_data = file.read()

        # Clean up temporary files
        os.remove(temp_input_file.name)
        os.remove(temp_output_file.name)

        # Assert that the saved data matches the original test data
        self.assertEqual(saved_data.strip(), test_data.strip())
