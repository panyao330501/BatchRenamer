# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for BatchRenamer
# Build: pyinstaller batch_renamer.spec  (from d:\Code\rename, conda env rename active)

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Bundle customtkinter themes/assets and tkinterdnd2 native DLLs
datas = []
datas += collect_data_files("customtkinter")
datas += collect_data_files("tkinterdnd2")

binaries = []
binaries += collect_dynamic_libs("tkinterdnd2")

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "customtkinter",
        "tkinterdnd2",
        "darkdetect",
        "PIL",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BatchRenamer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # add an .ico file path here to set an app icon
)
