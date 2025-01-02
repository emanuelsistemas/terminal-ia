from typing import Optional, Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import asyncio
from .chat import ChatAssistant
from .config import DATA_DIR
from .logger import setup_logger

logger = setup_logger(__name__)

class TelegramInterface:
    def __init__(self, token: str, groq_api_key: str, deepseek_api_key: str):
        """Inicializa a interface do Telegram"""
        self.token = token
        self.groq_api_key = groq_api_key
        self.deepseek_api_key = deepseek_api_key
        self.chats: Dict[int, ChatAssistant] = {}
        self.default_provider = "groq"
    
    def _get_chat_assistant(self, chat_id: int) -> ChatAssistant:
        """Obtém ou cria um assistente para o chat"""
        if chat_id not in self.chats:
            # Usa o provider padrão ao criar novo chat
            self.chats[chat_id] = ChatAssistant(
                api_key=self.groq_api_key,
                provider=self.default_provider
            )
        return self.chats[chat_id]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_message = """
        🤖 Olá! Eu sou um assistente IA que pode te ajudar com várias tarefas.
        
        Comandos disponíveis:
        /start - Mostra esta mensagem de ajuda
        /provider <nome> - Muda o provedor (groq ou deepseek)
        /clear - Limpa o histórico da conversa
        /status - Mostra informações do chat atual
        
        Você pode me enviar mensagens normalmente e eu vou tentar ajudar!
        """
        await update.message.reply_text(welcome_message)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        await self.start(update, context)
    
    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /clear"""
        chat_id = update.effective_chat.id
        assistant = self._get_chat_assistant(chat_id)
        assistant.clear_messages()
        await update.message.reply_text("🧹 Histórico limpo com sucesso!")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        chat_id = update.effective_chat.id
        assistant = self._get_chat_assistant(chat_id)
        
        status_message = f"""
        📊 Status do Chat:
        
        ID: {chat_id}
        Provider: {assistant.provider}
        Mensagens: {len(assistant.messages)}
        Última atividade: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        await update.message.reply_text(status_message)
    
    async def change_provider(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /provider"""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Por favor, especifique o provider: /provider [groq|deepseek]"
            )
            return
        
        provider = context.args[0].lower()
        if provider not in ["groq", "deepseek"]:
            await update.message.reply_text(
                "❌ Provider inválido. Use 'groq' ou 'deepseek'"
            )
            return
        
        # Cria novo assistente com o provider escolhido
        api_key = self.groq_api_key if provider == "groq" else self.deepseek_api_key
        self.chats[chat_id] = ChatAssistant(api_key=api_key, provider=provider)
        
        await update.message.reply_text(f"🔄 Provider alterado para {provider}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens normais"""
        chat_id = update.effective_chat.id
        assistant = self._get_chat_assistant(chat_id)
        
        # Indica que está digitando
        async with context.bot.send_chat_action(chat_id, "typing"):
            try:
                # Adiciona mensagem do usuário
                assistant.add_message("user", update.message.text)
                
                # Obtém resposta
                response = await assistant.get_response()
                
                # Envia resposta
                await update.message.reply_text(response)
                
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {str(e)}")
                await update.message.reply_text(
                    "❌ Desculpe, ocorreu um erro ao processar sua mensagem."
                )
    
    def run(self):
        """Inicia o bot do Telegram"""
        try:
            # Cria aplicação
            application = Application.builder().token(self.token).build()
            
            # Adiciona handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help))
            application.add_handler(CommandHandler("clear", self.clear))
            application.add_handler(CommandHandler("status", self.status))
            application.add_handler(CommandHandler("provider", self.change_provider))
            application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message
            ))
            
            # Inicia o bot
            logger.info("🤖 Bot do Telegram iniciado!")
            application.run_polling()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar bot: {str(e)}")
            raise
