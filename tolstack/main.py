import sys, os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from tolstack.gui import run_app

import logging

logging.basicConfig(filename="error.log", level=logging.ERROR)

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        print(f"An error occurred: {e}")
