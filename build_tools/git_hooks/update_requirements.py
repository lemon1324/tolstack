import os
import subprocess
import pathlib
import sys

def main():
    print(os.getcwd())
    
    # Define file paths
    poetry_lock = pathlib.Path("poetry.lock")
    requirements_txt = pathlib.Path("build_tools/requirements.txt")

    # Check if both files exist
    if not poetry_lock.exists() or not requirements_txt.exists():
        print(f"Error: {'poetry.lock' if not poetry_lock.exists() else 'requirements.txt'} does not exist.")
        return 1

    # Get the modification times
    lock_mtime = poetry_lock.stat().st_mtime
    req_mtime = requirements_txt.stat().st_mtime

    # Compare modification times
    if lock_mtime > req_mtime:
        print("Updating requirements.txt from poetry.lock...")
        try:
            # Use subprocess.run with `shell=False` for cross-platform compatibility
            subprocess.run(
                ["poetry", "export", "-f", "requirements.txt", "--output", "build_tools/requirements.txt"],
                check=True
            )
            print("requirements.txt updated successfully.")
            
            # Stage the new file since we assume it's good.
            subprocess.run(
                ["git", "add", "build_tools/requirements.txt"],
                check=True
            )
            print("File added to git staging successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while exporting requirements.txt: {e}")
            return 1
    else:
        print("requirements.txt is up-to-date with poetry.lock.")

    return 0

if __name__ == "__main__":
    sys.exit(main())