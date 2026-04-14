# -*- mode: python ; coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Saltify PyInstaller spec file
#
# This spec bundles all runtime dependencies so the resulting executable
# works on a clean macOS / Windows machine with NO pre-installed Python,
# Java, ffmpeg, or other tools.
#
# Usage:  pyinstaller Saltify.spec
# ---------------------------------------------------------------------------
import os
import sys

block_cipher = None

a = Analysis(
    ['GUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('build_assets/en-model.slp', 'pattern/text/en'),
        ('CTkXYFrame', 'CTkXYFrame'),
        ('components', 'components'),
        ('nltk_data', 'nltk_data'),
    ],
    hiddenimports=[
        'lightning_fabric',
        'torch',
        'torchvision',
        'pytorch_lightning',
        'pyannote.audio',
        'language_tool_python',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, cipher=block_cipher)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
