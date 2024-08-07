from tolstack.AppConfig import AppConfig
from tolstack.gui.GUITypes import (
    DataWidget,
    AnalysisWidget,
    OptionsWidget,
    is_boolean_option,
    get_default_options,
)

from distutils.util import strtobool
from packaging.version import Version

import re
import os


def save_to_name(file_name, info):
    if file_name:
        with open(file_name, "w", encoding="utf-8") as file:
            # Versions
            file.write(
                f"*VERSIONINFO, {AppConfig.app_version}, {AppConfig.file_format_version}"
                + "\n",
            )

            # Options
            option_strings = [str(info[key]) for key in OptionsWidget]
            file.write(f"*OPTIONS,{','.join(option_strings)}" + "\n")

            # Analysis Information
            file.write("*ANALYSISINFO" + "\n")
            for key in AnalysisWidget:
                raw_text = info[key]
                escaped_text = raw_text.replace("\n", "\\n")
                file.write(f"{key.value:d},{escaped_text}" + "\n")

            # Data
            file.write("*CONSTANTS, VALUE, NOTE" + "\n")
            for row_data in info[DataWidget.CONSTANTS]:
                file.write(",".join(row_data) + "\n")

            file.write(
                "*DIMENSIONS, NOMINAL, PLUS, MINUS, DISTRIBUTION, PART NUMBER, NOTE"
                + "\n"
            )
            for row_data in info[DataWidget.DIMENSIONS]:
                file.write(",".join(row_data) + "\n")

            file.write("*EXPRESSIONS, VALUE, LOWER, UPPER, METHOD, NOTE" + "\n")
            for row_data in info[DataWidget.EXPRESSIONS]:
                file.write(",".join(row_data) + "\n")


def open_from_name(file_name):
    if not file_name:
        raise ValueError("Attempting to open file but no file name provivded.")

    info = {}

    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Parse VERSIONINFO - always the first line in the file
    version_info_line = lines.pop(0).strip()
    match = re.match(r"\*VERSIONINFO,\s*(\S+),\s*(\S+)", version_info_line)
    if match:
        app_version, file_format_version = match.groups()
    else:
        raise ValueError("Attempting to open file but no version information present.")

    default_options = False
    if Version(file_format_version) < Version(AppConfig.file_format_version):
        if file_format_version in ["2.0", "3.0"] and AppConfig.file_format_version in [
            "3.0",
            "4.0",
        ]:
            default_options = True
            info.update(get_default_options())
        else:  # change outside options line, so can't just use defaults
            raise RuntimeError(
                "File is from an older version of tolstack, please edit file or manually copy entries."
            )

    # Initialize other sections
    analysis_info = {}
    constants = []
    dimensions = []
    expressions = []

    current_section = None
    split_limit = -1

    for line in lines:
        line = line.strip()

        # TODO: add possibility for comment lines in an input file?

        if line.startswith("*OPTIONS") and not default_options:
            options = line.replace("*OPTIONS,", "").split(
                ",", maxsplit=len(OptionsWidget) - 1
            )
            for idx, key in enumerate(OptionsWidget):
                if is_boolean_option(key):
                    info[key] = True if strtobool(options[idx]) else False
                else:
                    info[key] = options[idx]
        elif line.startswith("*ANALYSISINFO"):
            current_section = "analysis"
            split_limit = 1
            continue
        elif line.startswith("*CONSTANTS"):
            current_section = "constants"
            split_limit = 2
            continue
        elif line.startswith("*DIMENSIONS"):
            current_section = "dimensions"
            split_limit = 6
            continue
        elif line.startswith("*EXPRESSIONS"):
            current_section = "expressions"
            split_limit = 5
            continue
        elif line.startswith("*"):
            current_section = None
            split_limit = -1
            continue

        if current_section == "analysis":
            key, escaped_text = line.split(",", split_limit)
            clean_text = escaped_text.replace("\\n", "\n")
            analysis_info[AnalysisWidget(int(key))] = clean_text

        elif current_section == "constants":
            constants.append(line.split(",", split_limit))

        elif current_section == "dimensions":
            dimensions.append(line.split(",", split_limit))

        elif current_section == "expressions":
            expressions.append(line.split(",", split_limit))

    # Assign parsed data back to info
    info.update(analysis_info)
    info[DataWidget.CONSTANTS] = constants
    info[DataWidget.DIMENSIONS] = dimensions
    info[DataWidget.EXPRESSIONS] = expressions

    return info


def get_absolute_path(file_str, relative_str):
    # Get the directory name of the file (i.e., the folder containing the file)
    parent_directory = os.path.dirname(file_str)

    # Combine the parent directory with the relative path
    combined_path = os.path.join(parent_directory, relative_str)

    # Resolve the combined path to an absolute path
    absolute_path = os.path.abspath(combined_path)

    return absolute_path
