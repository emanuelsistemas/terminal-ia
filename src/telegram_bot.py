from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Any
import logging

from .agents.orquestrador_agent import OrquestradorAgent

logger = logging.getLogger(__name__)

class TelegramInterface:
    def __init__(self, token: str, groq_api_key: str, deepseek_api_key: str):
        """Inicializa a interface do Telegram"""
        self.token = token
        self.app = Application.builder().token(token).build()
        self.orquestrador = OrquestradorAgent(groq_api_key, deepseek_api_key)
        
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
        logger.info(f"Mensagem recebida do chat {chat_id}")
        
        # Indica que está digitando
        await update.message.chat.send_action(action="typing")
        
        try:
            # Processa a mensagem
            resultado = await self.orquestrador.processar_mensagem(mensagem, chat_id)
            logger.info(f"Resultado do processamento: {resultado}")
            
            # Formata a resposta baseada no tipo de resultado
            if resultado["tipo"] == "erro":
                await update.message.reply_text(f"Erro: {resultado['mensagem']}")
            elif resultado["tipo"] in ["comando_arquivo", "comando_diretorio"]:
                if resultado["sucesso"]:
                    # Mostra o processo acontecendo
                    processo = resultado.get("processo", [])
                    if processo:
                        # Envia mensagem de processo
                        msg = await update.message.reply_text("\n".join(processo[:2]))
                        
                        # Atualiza a mensagem algumas vezes para simular progresso
                        if len(processo) > 4:
                            await msg.edit_text("\n".join(processo[:4]))
                        await msg.edit_text("\n".join(processo))
                    
                    # Formata a resposta usando LLM
                    resposta_formatada = await self.orquestrador.conversa.formatar_resposta(
                        resultado,
                        resultado["tipo"]
                    )
                    
                    # Se a formatação falhou, usa a resposta padrão
                    if not resposta_formatada:
                        if resultado["tipo"] == "comando_arquivo":
                            await update.message.reply_text(
                                f"Arquivo criado: {resultado['info']['caminho_completo']}"
                            )
                        else:
                            await update.message.reply_text(
                                f"Pasta criada: {resultado['info']['caminho_completo']}"
                            )
                    else:
                        await update.message.reply_text(resposta_formatada)
                else:
                    await update.message.reply_text(f"Erro: {resultado['mensagem']}")
            elif resultado["tipo"] == "conversa":
                await update.message.reply_text(resultado["resposta"])
            else:
                logger.error(f"Tipo de resultado desconhecido: {resultado}")
                await update.message.reply_text(
                    "Ocorreu um erro. Tente novamente."
                )
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await update.message.reply_text(
                "Ocorreu um erro. Tente novamente."
            )
