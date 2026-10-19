#!/usr/bin/env python3
"""
Vocalis Launcher Script
"""
import sys
import os

# Adiciona o diretório 'src' ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from vocalis.__main__ import main

if __name__ == "__main__":
    main()
