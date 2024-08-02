from enum import Enum


class AnalysisWidget(Enum):
    TITLE = 0
    DOCNO = 1
    REVISION = 2
    DESCRIPTION = 3


class DataWidget(Enum):
    CONSTANTS = 0
    DIMENSIONS = 1
    EXPRESSIONS = 2


class OptionsWidget(Enum):
    FIND_IMAGES = 0
    SHOW_PLOTS = 1
    WHERE_USED = 2
    SENSITIVITY = 3
    CONTRIBUTIONS = 4
    UNITS = 50
    IMAGE_FOLDER = 100


BOOLEAN_OPTIONS = [
    OptionsWidget.FIND_IMAGES,
    OptionsWidget.WHERE_USED,
    OptionsWidget.SENSITIVITY,
    OptionsWidget.CONTRIBUTIONS,
]


# Assume that everything is either a text input supporting text() or is a checkbox supporting isChecked()
def is_boolean_option(item: Enum):
    return item in BOOLEAN_OPTIONS
