import PyInstaller.__main__
import toml
import sys

from tolstack.AppConfig import AppConfig


def get_version():
    with open("pyproject.toml", "r") as f:
        pyproject_data = toml.load(f)
    return pyproject_data.get("tool", {}).get("poetry", {}).get("version", "")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        print(get_version())
    else:
        PyInstaller.__main__.run(
            [
                "tolstack/main.py",
                "--onedir",
                "--windowed",
                "--name=tolstack",
                "--additional-hooks-dir=build_tools/pyinstaller-hooks",
                f"--splash=tolstack/content/splash_v{AppConfig.app_version}.png",
                "--noconfirm",
            ]
        )
