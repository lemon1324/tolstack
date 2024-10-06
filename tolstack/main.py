import sys, os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from tolstack.gui.gui import run_app
from tolstack.AppConfig import AppConfig

import logging

logging.basicConfig(filename=AppConfig.path_to_error_log, level=logging.ERROR, filemode='a')

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        logging.exception("An error occurred in GUI code, outside the processing update.")
        print(f"An error occurred: {e}")
