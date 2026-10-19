#!/usr/bin/env python3
"""
Vocalis Launcher Script
"""
import sys
import os

# Garante carregamento da libportaudio e dependências em modo usuário no Linux
import ctypes
import ctypes.util

jack_path = os.path.expanduser("~/.local/lib/libjack.so.0")
if os.path.exists(jack_path):
    try:
        ctypes.CDLL(jack_path, mode=ctypes.RTLD_GLOBAL)
    except Exception:
        pass

_orig_find_library = ctypes.util.find_library

def _custom_find_library(name):
    if name == 'portaudio':
        user_lib = os.path.expanduser("~/.local/lib/libportaudio.so.2")
        if os.path.exists(user_lib):
            return user_lib
    return _orig_find_library(name)

ctypes.util.find_library = _custom_find_library

# Adiciona o diretório 'src' ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from vocalis.__main__ import main

if __name__ == "__main__":
    main()
