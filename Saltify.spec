# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('images', 'images'), ('components', 'components'), ('venv39\\Lib\\site-packages\\pattern\\text', 'pattern/text'), ('venv39\\Lib\\site-packages\\lightning_fabric', 'lightning_fabric'), ('venv39\\Lib\\site-packages\\pyannote', 'pyannote'), ('venv39\\Lib\\site-packages\\torch', 'torch'), ('venv39\\Lib\\site-packages\\torchaudio', 'torchaudio')]
datas += collect_data_files('sv_ttk')
datas += collect_data_files('whisper')
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
datas += copy_metadata('openai-whisper', recursive=True)


a = Analysis(
    ['GUI.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
