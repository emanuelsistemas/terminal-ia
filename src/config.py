from pathlib import Path

# Diretório de dados
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Arquivo de mensagens
MESSAGES_FILE = DATA_DIR / "messages.json"

# Configurações dos modelos
MODEL_CONFIGS = {
    "groq": {
        "model": "mixtral-8x7b-32768",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "deepseek": {
        "model": "deepseek-coder",  # Nome simplificado do modelo
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
}

class COLORS:
    # Cores básicas
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Cores claras
    LIGHT_BLACK = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"
    LIGHT_WHITE = "\033[97m"
    
    # Estilos
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Reset
    RESET = "\033[0m"
