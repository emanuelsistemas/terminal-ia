from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import ParseMode
from typing import Tuple, Optional, Dict
import logging
import re
import os
import json
import asyncio
from groq import AsyncGroq
from openai import AsyncOpenAI

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AIProvider:
    def __init__(self):
        self.groq_client = AsyncGroq(api_key="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")
        self.deepseek_client = AsyncOpenAI(api_key="sk-e56e6c97810f405684b72e676c05b231")
        self.current_provider = "groq"
        
        # Carrega configurações
        self.load_config()
        
    def load_config(self):
        """Carrega configurações dos providers"""
        self.config = {
            "providers": {
                "groq": {
                    "model": "mixtral-8x7b-32768",
                    "description": "Mixtral 8x7B - mais rápido e versátil"
                },
                "deepseek": {
                    "model": "deepseek-chat",
                    "description": "DeepSeek Chat - mais preciso e detalhado"
                }
            },
            "default_provider": "groq"
        }
    
    def get_current_provider(self) -> str:
        return self.current_provider
    
    def set_provider(self, provider: str):
        if provider in self.config["providers"]:
            self.current_provider = provider
    
    async def ask(self, message: str) -> Optional[Tuple[str, str]]:
        """Pergunta à IA atual sobre o comando"""
        try:
            # Prepara o prompt
            system_prompt = "Você é um assistente técnico especializado em Linux. Analise a mensagem e extraia informações sobre criação de diretório. Se for um comando para criar pasta, retorne exatamente neste formato: 'Caminho Base: /caminho\nNome do Diretório: nome'. Se não for um comando para criar pasta, responda apenas 'Não é um comando para criar pasta'."
            
            if self.current_provider == "groq":
                completion = await self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    model=self.config["providers"]["groq"]["model"],
                    temperature=0
                )
                response = completion.choices[0].message.content
            else:  # deepseek
                completion = await self.deepseek_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    model=self.config["providers"]["deepseek"]["model"],
                    temperature=0
                )
                response = completion.choices[0].message.content
            
            logger.info(f"Resposta da IA ({self.current_provider}): {response}")
            
            if "não é um comando" in response.lower():
                return None
            
            # Extrai as informações da resposta
            base_path = re.search(r"caminho base:[ ]*([\w/.-]+)", response.lower())
            dirname = re.search(r"nome do diretório:[ ]*([\w/.-]+)", response.lower())
            
            if base_path and dirname:
                return base_path.group(1), dirname.group(1)
        
        except Exception as e:
            logger.error(f"Erro ao consultar IA: {str(e)}")
        
        return None

# Instância global do provider
ai_provider = AIProvider()

# Salva PID
def save_pid():
    with open("/tmp/telegram.pid", "w") as f:
        f.write(str(os.getpid()))

async def create_directory(path: str) -> Tuple[bool, str]:
    """Cria um diretório e retorna o status e mensagem"""
    try:
        os.makedirs(path, exist_ok=True)
        if os.path.exists(path) and os.path.isdir(path):
            return True, f"✅ Diretório '{path}' criado com sucesso!"
        return False, f"❌ Falha ao criar diretório '{path}'"
    except Exception as e:
        return False, f"❌ Erro ao criar diretório: {str(e)}"

def get_dir_info(path: str) -> Tuple[str, str]:
    """Retorna as permissões e tamanho do diretório"""
    try:
        stat = os.stat(path)
        perms = oct(stat.st_mode)[-3:]
        size = f"{stat.st_size / 1024:.1f}K"
        return perms, size
    except Exception as e:
        logger.error(f"Erro ao obter informações do diretório: {e}")
        return "????", "????"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    logger.info(f"Mensagem recebida: {message}")
    
    # Consulta a IA atual para interpretar o comando
    result = await ai_provider.ask(message)
    
    if not result:
        await update.message.reply_text(
            "❌ Não entendi o comando. Por favor, especifique claramente o nome da pasta e onde deseja criá-la.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    base_path, dirname = result
    full_path = os.path.join(base_path, dirname)

    # Primeira mensagem - Intenção
    await update.message.reply_text(
        f"🔄 Vou criar a pasta \"{dirname}\" em {base_path}...\n" \
        f"_(usando {ai_provider.get_current_provider()})_",
        parse_mode=ParseMode.MARKDOWN
    )

    # Cria o diretório e aguarda um momento
    success, msg = await create_directory(full_path)
    await asyncio.sleep(1)

    # Segunda mensagem - Resultado
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    # Terceira mensagem - Resumo (se sucesso)
    if success:
        perms, size = get_dir_info(full_path)
        await update.message.reply_text(
            f"📝 *Resumo da operação:*\n\n" \
            f"• Nome: `{dirname}`\n" \
            f"• Caminho: `{base_path}`\n" \
            f"• Caminho completo: `{full_path}`\n" \
            f"• Permissões: `{perms}`\n" \
            f"• Tamanho: `{size}`",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Altera o provider de IA"""
    message = update.message.text.lower().split()
    if len(message) > 1:
        provider = message[1]
        if provider in ai_provider.config["providers"]:
            ai_provider.set_provider(provider)
            await update.message.reply_text(
                f"✅ Provider alterado para *{provider}*\n" \
                f"Modelo: `{ai_provider.config['providers'][provider]['model']}`\n" \
                f"Descrição: _{ai_provider.config['providers'][provider]['description']}_",
                parse_mode=ParseMode.MARKDOWN
            )
            return
    
    # Se chegou aqui, mostra os providers disponíveis
    providers = "\n".join([f"• *{k}*: _{v['description']}_" for k, v in ai_provider.config["providers"].items()])
    await update.message.reply_text(
        f"ℹ️ *Providers disponíveis:*\n\n{providers}\n\n" \
        f"Para alterar, use: /provider <nome>",
        parse_mode=ParseMode.MARKDOWN
    )

def main() -> None:
    """Inicia o bot"""
    # Salva PID
    save_pid()

    # Token do bot
    token = "7791283056:AAFUfbgvdMucx30o-upUa1ylrHBk9ySVtsI"

    # Cria a aplicação
    app = Application.builder().token(token).build()

    # Adiciona handlers
    app.add_handler(CommandHandler("provider", handle_provider))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia o bot
    logger.info("Bot iniciado e pronto para uso!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
