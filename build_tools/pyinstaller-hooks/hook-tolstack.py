# pyinstaller-hooks/hook-tolstack.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs
hiddenimports = collect_submodules('tolstack') 
datas = collect_data_files('tolstack') 
binaries = collect_dynamic_libs('tolstack')