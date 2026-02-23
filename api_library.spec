# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for REST API Library
This file provides advanced customization for the build process.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

block_cipher = None

# Application details
app_name = 'rest-api-library'
main_script = 'run.py'

# Collect all hidden imports
hiddenimports = [
    # Uvicorn
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    # FastAPI
    'fastapi',
    'fastapi.responses',
    'fastapi.routing',
    # Pydantic
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic_settings',
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.orm',
    'sqlalchemy.sql',
    # Database drivers (optional - uncomment as needed)
    # 'psycopg2',
    # 'psycopg2.extensions',
    # 'pymysql',
    # 'pymysql.cursors',
]

# Collect all data and binary files
datas = [
    ('.env.example', '.'),
    ('README.md', '.'),
    ('QUICKSTART.md', '.'),
]

# Collect package data
tmp_ret = collect_all('fastapi')
datas += tmp_ret[0]
hiddenimports += tmp_ret[1]

tmp_ret = collect_all('pydantic')
datas += tmp_ret[0]
hiddenimports += tmp_ret[1]

tmp_ret = collect_all('sqlalchemy')
datas += tmp_ret[0]
hiddenimports += tmp_ret[1]

# Copy metadata
datas += copy_metadata('fastapi')
datas += copy_metadata('pydantic')
datas += copy_metadata('uvicorn')
datas += copy_metadata('sqlalchemy')

# Binaries
binaries = []

# Analysis
a = Analysis(
    [main_script],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for GUI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment and set path to icon file
)

# For onedir mode, uncomment below and comment out the EXE block above
"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
"""
