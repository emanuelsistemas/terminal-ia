import sys
import os

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.__main__ import main

if __name__ == "__main__":
    main()
