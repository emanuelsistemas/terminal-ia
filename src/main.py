import os
import logging
from dotenv import load_dotenv

from src.telegram_bot import TelegramInterface

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Obtém tokens
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not telegram_token or not groq_api_key:
        logger.error("Tokens não encontrados nas variáveis de ambiente")
        return
    
    try:
        logger.info("Iniciando NexusIA Bot...")
        
        # Inicializa e inicia o bot
        bot = TelegramInterface(telegram_token, groq_api_key)
        bot.start()
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        logger.error("Traceback completo:", exc_info=True)

if __name__ == "__main__":
    main()
