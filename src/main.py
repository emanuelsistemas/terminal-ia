import os
import sys
import asyncio
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from .chat import ChatAssistant
from .telegram_bot import TelegramInterface
from .terminal import TerminalInterface
from .logger import setup_logger

logger = setup_logger(__name__)

def load_config() -> dict:
    """Carrega configurações do ambiente"""
    load_dotenv()
    
    required_vars = [
        "GROQ_API_KEY",
        "DEEPSEEK_API_KEY",
    ]
    
    config = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        config[var] = value
    
    # Telegram token é opcional
    config["TELEGRAM_BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if missing_vars:
        logger.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        sys.exit(1)
    
    return config

def main():
    """Função principal do programa"""
    try:
        # Carrega configurações
        config = load_config()
        
        # Verifica modo de operação
        mode = sys.argv[1] if len(sys.argv) > 1 else "terminal"
        
        if mode == "telegram":
            # Verifica token do Telegram
            if not config["TELEGRAM_BOT_TOKEN"]:
                logger.error("Token do Telegram não configurado")
                sys.exit(1)
            
            # Inicia interface do Telegram
            telegram = TelegramInterface(
                token=config["TELEGRAM_BOT_TOKEN"],
                groq_api_key=config["GROQ_API_KEY"],
                deepseek_api_key=config["DEEPSEEK_API_KEY"]
            )
            telegram.run()
            
        else:
            # Inicia interface do terminal
            terminal = TerminalInterface(
                groq_api_key=config["GROQ_API_KEY"],
                deepseek_api_key=config["DEEPSEEK_API_KEY"]
            )
            terminal.run()
    
    except KeyboardInterrupt:
        logger.info("Programa encerrado pelo usuário")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
