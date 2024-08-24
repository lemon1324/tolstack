import unittest
import toml
from tolstack.AppConfig import AppConfig

class TestVersionConsistency(unittest.TestCase):

    def test_version_consistency(self):
        # Load the pyproject.toml file
        with open('pyproject.toml', 'r') as file:
            pyproject_data = toml.load(file)

        # Extract the version from pyproject.toml
        pyproject_version = pyproject_data['tool']['poetry']['version']

        # Extract the version from AppConfig
        app_config_version = AppConfig.app_version

        # Assert both versions are the same
        self.assertEqual(pyproject_version, app_config_version, 
                         f"Version mismatch: pyproject.toml has {pyproject_version}, but AppConfig has {app_config_version}")
