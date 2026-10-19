# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Garante que 'src' esteja acessível durante o processo de análise do PyInstaller
SRC_DIR = os.path.abspath('src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

block_cipher = None

# Coleta todos os módulos internos do pacote vocalis, pyrnnoise e audiolab
vocalis_modules = collect_submodules('vocalis')
pyrnnoise_modules = collect_submodules('pyrnnoise')
audiolab_modules = collect_submodules('audiolab')

hidden_imports = [
    'sounddevice',
    'soundfile',
    'noisereduce',
    'scipy',
    'scipy.signal',
    'numpy',
    'PySide6',
    'cffi',
    'pyrnnoise',
    'audiolab',
] + vocalis_modules + pyrnnoise_modules + audiolab_modules

# Garante inclusão de binários nativos do RNNoise (rnnoise.dll no Windows / librnnoise.so no Linux)
binaries = collect_dynamic_libs('pyrnnoise')

# Garante a inclusão dos arquivos de assets, templates do audiolab e metadados
datas = [
    ('logo.png', '.'),
    ('icon.ico', '.'),
    ('src/vocalis', 'vocalis'),
] + collect_data_files('pyrnnoise') + collect_data_files('audiolab')

a = Analysis(
    ['run.py'],
    pathex=[SRC_DIR, os.path.abspath('.')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='vocalis',
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
    icon=['icon.ico'],
)
