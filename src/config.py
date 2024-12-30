from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Diretório de dados
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
