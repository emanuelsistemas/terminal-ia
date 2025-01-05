from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
from openai import OpenAI
import json
import re
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
        self.workspace_dir = Path("/root/projetos/chat-ia-terminal/workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Carrega os prompts
        self.prompts = self._load_prompts()
        
        # Descrições dos modelos
        self.model_descriptions = {
            "groq": {
                "name": "Mixtral 8x7B",
                "description": "mais rápido e versátil",
                "provider": "Groq"
            },
            "deepseek": {
                "name": "DeepSeek Chat",
                "description": "mais preciso e detalhado",
                "provider": "DeepSeek"
            }
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
    
    def _format_response(self, response: str, provider: str) -> str:
        model_info = self.model_descriptions[provider]
        model_header = f"_Via {model_info['provider']} ({model_info['name']})_\n\n"
        return model_header + response

    def _create_file(self, filename: str, content: str) -> str:
        """Cria um arquivo no workspace e retorna o caminho"""
        if not filename:
            return "Nome do arquivo não especificado"

        try:
            # Se não houver extensão, adiciona .txt
            if '.' not in filename:
                filename = f"{filename}.txt"

            # Sanitiza o nome do arquivo
            filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
            
            # Define o caminho completo
            filepath = self.workspace_dir / filename
            
            # Cria o arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Arquivo criado com sucesso!\nLocal: `{filepath}`\nConteúdo: `{content}`"
        except Exception as e:
            return f"❌ Erro ao criar arquivo: {str(e)}"
    
    def _chat_with_ai(self, message: str, provider: str) -> str:
        try:
            logger.info(f"Processando mensagem com provider {provider}")
            
            # Verifica se é um comando para criar arquivo
            create_file_match = re.match(r"crie\s+(?:um\s+)?(?:arquivo\s+)?(?:chamado\s+)?([\w.-]+)(?:\s+com\s+(?:a\s+)?mensagem(?:,\s+|\s+e\s+|\s+)(.+))", message.lower())
            if create_file_match:
                filename = create_file_match.group(1)
                content = create_file_match.group(2).strip()
                logger.info(f"Criando arquivo {filename} com conteúdo {content}")
                return self._create_file(filename, content)
            
            # Se não for comando de criar arquivo, processa normalmente com a IA
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
        await update.message.reply_text(
            self.prompts["commands"]["start"]["message"],
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Comando /help recebido do chat {update.effective_chat.id}")
        await self.start(update, context)
    
    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Comando /clear recebido do chat {chat_id}")
        if chat_id in self.chats:
            self.chats[chat_id]["message_count"] = 0
            await update.message.reply_text(
                self.prompts["commands"]["clear_success"]["message"],
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                self.prompts["commands"]["clear_empty"]["message"],
                parse_mode=ParseMode.MARKDOWN
            )
    
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
        await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
    
    def _create_provider_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🚀 {self.model_descriptions['groq']['provider']} - {self.model_descriptions['groq']['name']}",
                    callback_data="provider_groq"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🧠 {self.model_descriptions['deepseek']['provider']} - {self.model_descriptions['deepseek']['name']}",
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
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def provider_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = query.message.chat_id
        provider = query.data.split("_")[1]  # provider_groq -> groq
        
        logger.info(f"Callback de provider recebido: {provider} para chat {chat_id}")
        
        await query.answer()
        self._get_chat_info(chat_id)["provider"] = provider
        
        model_info = self.model_descriptions[provider]
        await query.edit_message_text(
            self.prompts["commands"]["provider_changed"]["message"].format(
                provider=model_info["provider"],
                description=model_info["description"]
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message = update.message.text
        chat_info = self._get_chat_info(chat_id)
        provider = chat_info["provider"]
        
        logger.info(f"Mensagem recebida do chat {chat_id} usando provider {provider}")
        
        try:
            # Mostra "digitando" por mais tempo
            typing_task = asyncio.create_task(
                self._show_typing(context.bot, chat_id)
            )
            
            # Processa a mensagem
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._chat_with_ai,
                message,
                provider
            )
            
            # Cancela o "digitando"
            typing_task.cancel()
            
            chat_info["message_count"] += 1
            formatted_response = self._format_response(response, provider)
            await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Resposta enviada para chat {chat_id}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem para chat {chat_id}: {str(e)}")
            error_msg = self._format_response(
                self.prompts["commands"]["error"]["message"].format(error=str(e)),
                provider
            )
            await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)

    async def _show_typing(self, bot, chat_id):
        """Mostra o estado de digitação continuamente"""
        try:
            while True:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                await asyncio.sleep(5)  # Renova a cada 5 segundos
        except asyncio.CancelledError:
            pass
    
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
