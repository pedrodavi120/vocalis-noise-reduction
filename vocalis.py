#!/usr/bin/env python3
"""
Compatibilidade retroativa com o executável original vocalis.py.
Redireciona para o pacote modular vocalis.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from vocalis.__main__ import main

if __name__ == "__main__":
    main()