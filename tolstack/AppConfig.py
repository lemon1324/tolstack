from pathlib import Path
import sys


class AppConfig:
    app_version = "0.8.1"
    file_format_version = "4.0"

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent.parent

    path_to_help = (bundle_dir / 'tolstack/content/help.md').resolve()


if __name__ == "__main__":
    print(f"Application version: {AppConfig.app_version}")
    print(f"File format version: {AppConfig.file_format_version}")
    print(f"Path to help: {AppConfig.path_to_help}")
