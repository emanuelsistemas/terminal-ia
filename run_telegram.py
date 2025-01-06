import os
import logging
from src.telegram_bot import TelegramInterface

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telegram.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Salva PID
def save_pid():
    pid = os.getpid()
    with open("bot.pid", "w") as f:
        f.write(str(pid))
    logger.info(f"PID {pid} salvo em bot.pid")

try:
    # Salva PID
    save_pid()
    
    # Configurações do bot
    telegram_token = "7791283056:AAFUfbgvdMucx30o-upUa1ylrHBk9ySVtsI"
    groq_api_key = "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"
    deepseek_api_key = "sk-e56e6c97810f405684b72e676c05b231"

    # Inicia o bot
    logger.info("Iniciando bot...")
    bot = TelegramInterface(
        token=telegram_token,
        groq_api_key=groq_api_key,
        deepseek_api_key=deepseek_api_key,
        dev_chat_id=None
    )

    # Executa o bot
    logger.info("Bot iniciado, começando execução...")
    bot.run()

except Exception as e:
    logger.error(f"Erro fatal ao iniciar bot: {str(e)}", exc_info=True)
    raise
