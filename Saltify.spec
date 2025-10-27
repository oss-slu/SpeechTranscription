# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('images', 'images'), ('build_assets\\\\en-model.slp', 'pattern/text/en'), ('CTkXYFrame', 'CTkXYFrame')]
datas += collect_data_files('whisper')
datas += collect_data_files('lightning_fabric')
datas += collect_data_files('pytorch_lightning')
datas += collect_data_files('pyannote.audio')
datas += collect_data_files('sv_ttk')
datas += copy_metadata('torch')
datas += copy_metadata('tqdm')
datas += copy_metadata('regex')
datas += copy_metadata('sacremoses')
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('filelock')
datas += copy_metadata('numpy')
datas += copy_metadata('tokenizers')
datas += copy_metadata('importlib_metadata')


a = Analysis(
    ['GUI.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['lightning_fabric', 'torch', 'torchvision', 'pytorch_lightning', 'pyannote.audio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Saltify',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
