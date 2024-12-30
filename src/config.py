from pathlib import Path
import os

# Diretório base do projeto
BASE_DIR = Path(os.path.expanduser("~/.chat-ia"))

# Diretório de dados
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Diretório de logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
