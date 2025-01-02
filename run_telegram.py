import os
import signal
import sys
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

from src.telegram_bot import TelegramInterface

def signal_handler(signum, frame):
    print("\nEncerrando o bot...")
    sys.exit(0)

def main():
    # Registra handlers para SIGINT e SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configurações do bot
    token = "7791283056:AAFUfbgvdMucx30o-upUa1ylrHBk9ySVtsI"
    groq_key = "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"
    deepseek_key = "sk-e56e6c97810f405684b72e676c05b231"
    
    try:
        # Inicia o bot
        bot = TelegramInterface(token, groq_key, deepseek_key)
        print("Bot iniciado com configurações atualizadas...")
        bot.run()
    except Exception as e:
        print(f"Erro ao iniciar o bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
