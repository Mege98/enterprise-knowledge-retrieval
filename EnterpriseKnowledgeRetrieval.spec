# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_dir = Path(SPECPATH)

hiddenimports = (
    collect_submodules("pypdf")
    + collect_submodules("openpyxl")
)

datas = (
    collect_data_files("pypdf")
    + collect_data_files("openpyxl")
)

for resource_name in ("app_icon.png", "app_icon.ico"):
    resource_file = project_dir / resource_name
    if resource_file.exists():
        datas.append((str(resource_file), "."))

icon_file = project_dir / "app_icon.ico"
icon_value = str(icon_file) if icon_file.exists() else None

a = Analysis(
    [str(project_dir / "launcher.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6", "PySide2", "tkinter.test", "unittest.test"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EnterpriseKnowledgeRetrieval",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_value,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="EnterpriseKnowledgeRetrieval",
)
