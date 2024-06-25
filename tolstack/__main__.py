from tolstack.gui import run_app

import logging

logging.basicConfig(filename='error.log', level=logging.ERROR)

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
