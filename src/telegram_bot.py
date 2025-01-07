from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Any
import logging
import traceback

from .agents.orquestrador_agent import OrquestradorAgent

logger = logging.getLogger(__name__)

class TelegramInterface:
    def __init__(self, token: str, groq_api_key: str):
        """Inicializa a interface do Telegram"""
        self.token = token
        self.app = Application.builder().token(token).build()
        self.orquestrador = OrquestradorAgent(groq_api_key)
        
        # Registra os handlers
        self.app.add_handler(CommandHandler("start", self._start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._message))
        
        logger.info("TelegramInterface iniciado com sucesso")
    
    def start(self):
        """Inicia o bot"""
        logger.info("Iniciando aplicação do Telegram...")
        logger.info("Handlers registrados, iniciando polling...")
        self.app.run_polling()
    
    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Responde ao comando /start"""
        if not update.message:
            return
        
        chat_id = update.message.chat_id
        logger.info(f"Inicializando novo chat {chat_id}")
        
        await update.message.reply_text(
            "Oi, sou o Nexus. O que precisa?"
        )
    
    async def _message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto"""
        if not update.message or not update.message.text:
            return
        
        chat_id = update.message.chat_id
        mensagem = update.message.text
        
        # Log da mensagem recebida
        logger.info(f"Mensagem recebida do chat {chat_id}: {mensagem}")
        
        try:
            # Indica que está digitando
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Processa a mensagem
            resultado = await self.orquestrador.processar_mensagem(mensagem, chat_id)
            
            # Log do resultado
            logger.info(f"Resultado do processamento: {resultado}")
            
            # Envia a resposta
            if resultado.get("tipo") == "erro":
                await update.message.reply_text(resultado["mensagem"])
                return
            
            if resultado.get("tipo") in ["comando_arquivo", "comando_diretorio"]:
                if resultado.get("sucesso"):
                    await update.message.reply_text("Operação realizada com sucesso.")
                else:
                    await update.message.reply_text(resultado["mensagem"])
            
            else:  # conversa normal
                if resultado.get("sucesso"):
                    await update.message.reply_text(resultado["resposta"])
                else:
                    await update.message.reply_text("Erro: " + resultado.get("resposta", "Erro desconhecido"))
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            logger.error("Traceback completo:", exc_info=True)
            await update.message.reply_text("Erro: Ocorreu um erro ao processar sua mensagem. Detalhes: " + str(e))
