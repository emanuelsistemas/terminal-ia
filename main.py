import os
import sys
import logging
from dotenv import load_dotenv

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importa o bot
from src.telegram_bot import TelegramInterface

def carregar_variaveis_ambiente():
    """Carrega as variáveis de ambiente do arquivo .env"""
    # Carrega variáveis do .env
    load_dotenv()
    
    # Verifica variáveis obrigatórias
    variaveis = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY")
    }
    
    # Verifica se todas as variáveis estão presentes
    faltando = [k for k, v in variaveis.items() if not v]
    if faltando:
        logger.error(f"❌ Erro: Variáveis de ambiente faltando: {', '.join(faltando)}")
        sys.exit(1)
    
    return variaveis

def main():
    """Função principal do bot"""
    try:
        logger.info("Iniciando NexusIA Bot...")
        
        # Carrega variáveis de ambiente
        env = carregar_variaveis_ambiente()
        
        # Inicializa o bot
        bot = TelegramInterface(
            token=env["TELEGRAM_BOT_TOKEN"],
            groq_api_key=env["GROQ_API_KEY"],
            deepseek_api_key=None
        )
        
        logger.info("Bot inicializado, iniciando execução...")
        
        # Inicia o bot
        bot.start()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
