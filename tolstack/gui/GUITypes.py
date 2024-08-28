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
    MAX_IMG_WIDTH = 51
    MAX_IMG_HEIGHT = 52
    IMAGE_FOLDER = 100


BOOLEAN_OPTIONS = [
    OptionsWidget.FIND_IMAGES,
    OptionsWidget.SHOW_PLOTS,
    OptionsWidget.WHERE_USED,
    OptionsWidget.SENSITIVITY,
    OptionsWidget.CONTRIBUTIONS,
]


# Assume that everything is either a text input supporting text() or is a checkbox supporting isChecked()
def is_boolean_option(item: Enum):
    return item in BOOLEAN_OPTIONS


def get_default_options():
    return {
        OptionsWidget.FIND_IMAGES: False,
        OptionsWidget.SHOW_PLOTS: False,
        OptionsWidget.WHERE_USED: False,
        OptionsWidget.SENSITIVITY: False,
        OptionsWidget.CONTRIBUTIONS: False,
        OptionsWidget.UNITS: "inches",
        OptionsWidget.MAX_IMG_WIDTH: "6",
        OptionsWidget.MAX_IMG_HEIGHT: "4",
        OptionsWidget.IMAGE_FOLDER: "images",
    }
