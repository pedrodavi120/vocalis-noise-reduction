import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

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

# Adiciona o diretório 'src' ao sys.path se necessário
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from vocalis.gui.app import VocalisMainWindow


def main():
    app = QApplication(sys.argv)

    font = QFont()
    font.setFamily("Roboto")
    app.setFont(font)

    window = VocalisMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
