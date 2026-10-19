import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

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
