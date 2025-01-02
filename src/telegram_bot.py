from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
from openai import OpenAI
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramInterface:
    def __init__(self, token: str, groq_api_key: str, deepseek_api_key: str):
        logger.info("Iniciando TelegramInterface...")
        self.token = token
        self.groq_api_key = groq_api_key
        self.deepseek_api_key = deepseek_api_key
        self.chats: Dict[int, Dict] = {}
        self.default_provider = "groq"
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Carrega os prompts
        self.prompts = self._load_prompts()
        
        # Descrições dos modelos
        self.model_descriptions = {
            "groq": "Mixtral 8x7B - mais rápido e versátil",
            "deepseek": "DeepSeek Chat - mais preciso e detalhado"
        }
        logger.info("TelegramInterface iniciado com sucesso")
    
    def _load_prompts(self) -> Dict:
        logger.info("Carregando prompts...")
        prompts = {}
        prompts_dir = Path("/root/projetos/chat-ia-terminal/prompts")
        
        try:
            # Carrega system prompts
            with open(prompts_dir / "system.json", "r", encoding="utf-8") as f:
                prompts["system"] = json.load(f)
            
            # Carrega comandos
            with open(prompts_dir / "commands.json", "r", encoding="utf-8") as f:
                prompts["commands"] = json.load(f)
            
            logger.info("Prompts carregados com sucesso")
            return prompts
        except Exception as e:
            logger.error(f"Erro ao carregar prompts: {str(e)}")
            raise
    
    def _init_chat(self, chat_id: int) -> None:
        if chat_id not in self.chats:
            logger.info(f"Inicializando novo chat {chat_id}")
            self.chats[chat_id] = {
                "provider": self.default_provider,
                "start_time": datetime.now(),
                "message_count": 0
            }
    
    def _get_chat_info(self, chat_id: int) -> Dict:
        self._init_chat(chat_id)
        return self.chats[chat_id]
    
    def _get_provider(self, chat_id: int) -> str:
        return self._get_chat_info(chat_id)["provider"]
    
    def _get_system_prompt(self, provider: str) -> Dict:
        return self.prompts["system"].get(provider, self.prompts["system"]["default"])
    
    def _chat_with_ai(self, message: str, provider: str) -> str:
        try:
            logger.info(f"Processando mensagem com provider {provider}")
            system_prompt = self._get_system_prompt(provider)
            messages = [system_prompt, {"role": "user", "content": message}]
            
            if provider == "groq":
                client = Groq(api_key=self.groq_api_key)
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=messages
                )
            else:  # deepseek
                client = OpenAI(api_key=self.deepseek_api_key, base_url="https://api.deepseek.com/v1")
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
            
            logger.info("Resposta gerada com sucesso")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return self.prompts["commands"]["error"]["message"].format(error=str(e))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Comando /start recebido do chat {chat_id}")
        self._init_chat(chat_id)
        await update.message.reply_text(self.prompts["commands"]["start"]["message"])
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Comando /help recebido do chat {update.effective_chat.id}")
        await self.start(update, context)
    
    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Comando /clear recebido do chat {chat_id}")
        if chat_id in self.chats:
            self.chats[chat_id]["message_count"] = 0
            await update.message.reply_text(self.prompts["commands"]["clear_success"]["message"])
        else:
            await update.message.reply_text(self.prompts["commands"]["clear_empty"]["message"])
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Comando /status recebido do chat {chat_id}")
        chat_info = self._get_chat_info(chat_id)
        
        uptime = datetime.now() - chat_info["start_time"]
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        status_msg = self.prompts["commands"]["status"]["message"].format(
            provider=chat_info["provider"],
            message_count=chat_info["message_count"],
            uptime=f"{hours}h {minutes}m"
        )
        await update.message.reply_text(status_msg)
    
    def _create_provider_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🚀 Groq - {self.model_descriptions['groq']}",
                    callback_data="provider_groq"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🧠 DeepSeek - {self.model_descriptions['deepseek']}",
                    callback_data="provider_deepseek"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def set_provider(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Comando /provider recebido do chat {chat_id}")
        keyboard = self._create_provider_keyboard()
        await update.message.reply_text(
            "Selecione o modelo de IA:",
            reply_markup=keyboard
        )
    
    async def provider_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = query.message.chat_id
        provider = query.data.split("_")[1]  # provider_groq -> groq
        
        logger.info(f"Callback de provider recebido: {provider} para chat {chat_id}")
        
        await query.answer()
        self._get_chat_info(chat_id)["provider"] = provider
        
        await query.edit_message_text(
            self.prompts["commands"]["provider_changed"]["message"].format(
                provider=provider,
                description=self.model_descriptions[provider]
            )
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message = update.message.text
        chat_info = self._get_chat_info(chat_id)
        provider = chat_info["provider"]
        
        logger.info(f"Mensagem recebida do chat {chat_id} usando provider {provider}")
        
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._chat_with_ai,
                message,
                provider
            )
            
            chat_info["message_count"] += 1
            await update.message.reply_text(response)
            logger.info(f"Resposta enviada para chat {chat_id}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem para chat {chat_id}: {str(e)}")
            error_msg = self.prompts["commands"]["error"]["message"].format(error=str(e))
            await update.message.reply_text(error_msg)
    
    def run(self):
        logger.info("Iniciando aplicação do Telegram...")
        try:
            app = Application.builder().token(self.token).build()
            
            # Registra handlers
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CommandHandler("help", self.help))
            app.add_handler(CommandHandler("clear", self.clear))
            app.add_handler(CommandHandler("status", self.status))
            app.add_handler(CommandHandler("provider", self.set_provider))
            app.add_handler(CallbackQueryHandler(self.provider_callback, pattern=r"^provider_"))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            logger.info("Handlers registrados, iniciando polling...")
            print("Bot do Telegram iniciado e pronto para uso!")
            app.run_polling()
        except Exception as e:
            logger.error(f"Erro fatal ao iniciar bot: {str(e)}")
            raise
