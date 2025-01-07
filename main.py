import logging
import os
from dotenv import load_dotenv
from src.telegram_bot import TelegramInterface

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_env():
    """Carrega variáveis de ambiente"""
    try:
        # Tenta carregar do .env
        load_dotenv()
        
        # Verifica variáveis obrigatórias
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "GROQ_API_KEY",
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            logger.error(f"❌ Variáveis de ambiente faltando: {missing}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar variáveis de ambiente: {e}")
        return False

def main():
    """Função principal"""
    try:
        logger.info("Iniciando NexusIA Bot...")
        
        # Carrega variáveis de ambiente
        if not setup_env():
            logger.error("❌ Falha ao carregar configurações")
            return
        
        # Inicializa e executa o bot
        bot = TelegramInterface(
            token=os.getenv("TELEGRAM_BOT_TOKEN"),
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        bot.start()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        logger.error("Traceback:", exc_info=True)

if __name__ == "__main__":
    main()
