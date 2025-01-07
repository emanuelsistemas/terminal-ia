from typing import Dict, Optional
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, orquestrador):
        self.orquestrador = orquestrador
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        await update.message.reply_text(
            "🤖 Olá! Eu sou o NexusIA Bot, seu assistente para desenvolvimento web.\n\n" + \
            "Posso te ajudar a:\n" + \
            "- Criar novos projetos React + TypeScript\n" + \
            "- Gerenciar arquivos e diretórios\n" + \
            "- Dar dicas de boas práticas\n\n" + \
            "Para começar, use o comando /projeto para criar um novo projeto!"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        await update.message.reply_text(
            "🤖 Aqui estão os comandos disponíveis:\n\n" + \
            "/projeto - Cria um novo projeto\n" + \
            "/cd <caminho> - Navega entre diretórios\n" + \
            "/touch <arquivo> - Cria um arquivo\n" + \
            "/mkdir <diretório> - Cria um diretório\n\n" + \
            "Você também pode conversar normalmente comigo para tirar dúvidas!"
        )
    
    async def mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens normais"""
        try:
            # Envia mensagem de digitando
            await update.message.chat.send_chat_action("typing")
            
            # Processa a mensagem
            resultado = await self.orquestrador.processar_mensagem(
                update.message.text,
                update.message.chat_id
            )
            
            # Se tiver streaming, envia primeiro
            if "streaming" in resultado:
                await update.message.reply_text(
                    resultado["streaming"],
                    parse_mode=None  # Desativa o parse mode para não interferir com os emojis
                )
            
            # Envia a resposta principal
            if resultado["tipo"] == "pergunta":
                # Se for uma pergunta, envia só a pergunta
                await update.message.reply_text(resultado["resposta"])
            elif resultado["tipo"] == "sucesso" or resultado["tipo"] == "erro":
                # Se for sucesso ou erro, envia a resposta completa
                await update.message.reply_text(resultado["resposta"])
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await update.message.reply_text(
                f"❌ Desculpe, ocorreu um erro ao processar sua mensagem. Detalhes: {str(e)}"
            )
