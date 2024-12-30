import os
import signal
import asyncio
from typing import Optional
from datetime import datetime
import pytz
from dotenv import load_dotenv
import sys
import threading
import time
import re
import unicodedata

from .chat import ChatAssistant, ChatError
from .config import COLORS
from .database import Database

class LoadingAnimation:
    def __init__(self, message: str = "Processando"):
        self.is_running = False
        self.thread = None
        self.frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]
        self.current_frame = 0
        self.message = message

    def animate(self):
        while self.is_running:
            sys.stdout.write(f"\r{COLORS.BLUE}{self.message} {self.frames[self.current_frame]}{COLORS.RESET}")
            sys.stdout.flush()
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            time.sleep(0.1)

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r\033[K")  # Limpa a linha
        sys.stdout.flush()

class Assistant:
    def __init__(self):
        self.chat: Optional[ChatAssistant] = None
        self.db = Database()
        self.running = True
        self.loading = LoadingAnimation()
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print("\nEncerrando...")
        self.running = False
    
    def strip_ansi(self, text: str) -> str:
        """Remove códigos ANSI de uma string"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def get_string_width(self, text: str) -> int:
        """Calcula a largura visual de uma string, considerando emojis e caracteres especiais"""
        width = 0
        text = self.strip_ansi(text)
        
        i = 0
        while i < len(text):
            # Pega o caractere atual
            char = text[i]
            
            # Verifica se é um emoji (surrogate pair)
            if ord(char) >= 0x1F000:
                width += 2
                i += 2 if i + 1 < len(text) and 0xD800 <= ord(text[i]) <= 0xDBFF else 1
            # Verifica se é um caractere de largura dupla
            elif unicodedata.east_asian_width(char) in ['F', 'W']:
                width += 2
                i += 1
            # Caractere normal
            else:
                width += 1
                i += 1
        
        return width
    
    def create_box(self, text: str, color: str = COLORS.GREEN, width: int = 50) -> str:
        # Divide o texto em linhas
        lines = text.split("\n")
        formatted_lines = []
        
        for line in lines:
            current_line = line
            while self.get_string_width(current_line) > width - 4:  # -4 para os caracteres ║ e espaços
                # Encontra o último espaço antes do limite
                visible_text = self.strip_ansi(current_line)
                test_width = 0
                split_point = 0
                
                for i, char in enumerate(visible_text):
                    if char == " ":
                        last_space = i
                    
                    char_width = 2 if ord(char) >= 0x1F000 or unicodedata.east_asian_width(char) in ['F', 'W'] else 1
                    test_width += char_width
                    
                    if test_width > width - 4:
                        split_point = last_space if 'last_space' in locals() else i
                        break
                
                # Divide a linha mantendo os códigos ANSI
                formatted_lines.append(current_line[:split_point])
                current_line = current_line[split_point:].lstrip()
            
            if current_line:
                formatted_lines.append(current_line)

        # Cria o box
        box_top = f"{color}╔{'═' * (width-2)}╗{COLORS.RESET}"
        box_bottom = f"{color}╚{'═' * (width-2)}╝{COLORS.RESET}"
        box_content = []
        
        for line in formatted_lines:
            # Calcula o padding baseado na largura visual do texto
            visible_width = self.get_string_width(line)
            padding = width - 4 - visible_width  # -4 para os caracteres ║ e espaços
            box_content.append(f"{color}║{COLORS.RESET} {line}{' ' * padding} {color}║{COLORS.RESET}")
        
        return "\n".join([box_top] + box_content + [box_bottom])
    
    def print_welcome(self):
        print(self.create_box("Bem-vindo ao Chat IA", COLORS.GREEN, 40))
    
    def print_menu(self):
        print("Escolha o provedor:\n")
        print("1. Groq")
        print("2. Deepseek\n")
    
    def get_provider_choice(self) -> str:
        while True:
            try:
                choice = input("Opção (1-2): ").strip()
                if choice == "1":
                    return "groq"
                elif choice == "2":
                    return "deepseek"
                else:
                    print("Opção inválida. Tente novamente.")
            except Exception as e:
                print(f"Erro: {str(e)}")
    
    async def initialize(self, provider: str):
        try:
            load_dotenv()
            
            api_key = {
                "groq": os.getenv("GROQ_API_KEY"),
                "deepseek": os.getenv("DEEPSEEK_API_KEY")
            }[provider]
            
            if not api_key:
                raise ChatError(f"Chave de API do {provider} não encontrada")
            
            self.chat = ChatAssistant(api_key=api_key, provider=provider)
            await self.db.initialize()
            
            print("\nAssistente iniciado. Digite:")
            print("- 'sair' para encerrar")
            print("- 'limpar' para limpar o histórico")
            print("- '!restore ID' para restaurar um checkpoint")
            print("- '!list' para listar checkpoints\n")
            
        except Exception as e:
            print(f"Erro: {str(e)}")
            self.running = False
    
    def format_timestamp(self) -> str:
        tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz)
        return now.strftime("%H:%M:%S - %d/%m/%Y")
    
    def get_model_info(self) -> str:
        if self.chat:
            return f"LLM: {self.chat.provider.upper()} | Modelo: {self.chat.model}"
        return ""

    def get_user_input(self) -> str:
        sys.stdout.write("Você: ")
        sys.stdout.flush()
        return input().strip()
    
    async def handle_restore(self, message_id: str):
        # Cria um loading específico para restauração
        loading = LoadingAnimation("Restaurando checkpoint")
        loading.start()
        
        try:
            messages = await self.db.restore_checkpoint(message_id)
            loading.stop()
            
            if messages:
                self.chat.messages = messages
                await self.db.save_messages(messages)
                print(f"\nCheckpoint {message_id} restaurado com sucesso!")
                
                # Mostra a última mensagem restaurada
                if messages:
                    last_message = messages[-1]
                    restored_message = [
                        f"{COLORS.LIGHT_BLACK}ID: {last_message['id']}{COLORS.RESET}",
                        f"{COLORS.LIGHT_BLACK}{self.format_timestamp()}{COLORS.RESET}",
                        f"{COLORS.LIGHT_BLACK}Estado restaurado até:{COLORS.RESET}",
                        last_message["content"]
                    ]
                    print(self.create_box("\n".join(restored_message), COLORS.YELLOW))
            else:
                print(f"\nErro: Checkpoint {message_id} não encontrado")
        except Exception as e:
            loading.stop()
            print(f"\nErro ao restaurar checkpoint: {str(e)}")
    
    async def handle_list_checkpoints(self):
        # Cria um loading específico para listagem
        loading = LoadingAnimation("Carregando checkpoints")
        loading.start()
        
        try:
            checkpoints = await self.db.list_checkpoints()
            loading.stop()
            
            if checkpoints:
                print("\nCheckpoints disponíveis:")
                for cp in checkpoints:
                    timestamp = datetime.fromisoformat(cp["timestamp"]).strftime("%d/%m/%Y %H:%M:%S")
                    print(f"ID: {cp['id']}")
                    print(f"Data: {timestamp}")
                    print(f"Tipo: {cp['type']}")
                    if cp['type'] == 'system':
                        print(f"Python: {cp.get('python_version', 'N/A')}")
                    print(f"Mensagem: {cp['content']}")
                    print("-" * 50)
            else:
                print("\nNenhum checkpoint encontrado")
        except Exception as e:
            loading.stop()
            print(f"\nErro ao listar checkpoints: {str(e)}")
    
    async def run(self):
        try:
            self.print_welcome()
            self.print_menu()
            
            provider = self.get_provider_choice()
            await self.initialize(provider)
            
            while self.running:
                try:
                    print()  # Linha em branco para separar mensagens
                    user_input = self.get_user_input()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() == "sair":
                        print("\nEncerrando...")
                        break
                    
                    if user_input.lower() == "limpar":
                        self.chat.clear_messages()
                        await self.db.save_messages([])
                        print("\nHistórico limpo.")
                        continue
                    
                    if user_input.lower() == "!list":
                        await self.handle_list_checkpoints()
                        continue
                    
                    if user_input.lower().startswith("!restore "):
                        message_id = user_input[9:].strip()
                        await self.handle_restore(message_id)
                        continue
                    
                    # Box para mensagem do usuário
                    print("\033[A\033[K", end="")  # Limpa a linha do input
                    message_id = self.chat.add_message("user", user_input)
                    user_message = [
                        f"{COLORS.LIGHT_BLACK}ID: {message_id}{COLORS.RESET}",
                        f"{COLORS.LIGHT_BLACK}{self.format_timestamp()}{COLORS.RESET}",
                        f"Você: {user_input}"
                    ]
                    print(self.create_box("\n".join(user_message), COLORS.GREEN))
                    print()  # Linha em branco após a mensagem do usuário
                    
                    # Salva mensagens após input do usuário
                    await self.db.save_messages(self.chat.messages)
                    
                    # Inicia animação de loading
                    self.loading.start()
                    
                    try:
                        # Obtém resposta da IA
                        response = await self.chat.get_response()
                        
                        # Para a animação de loading
                        self.loading.stop()
                        
                        # Pega o ID da última mensagem (resposta da IA)
                        ai_message_id = self.chat.messages[-1]["id"]
                        
                        # Cria mensagem completa com ID, timestamp, modelo e resposta
                        ai_message = [
                            f"{COLORS.LIGHT_BLACK}ID: {ai_message_id}{COLORS.RESET}",
                            f"{COLORS.LIGHT_BLACK}{self.format_timestamp()}{COLORS.RESET}",
                            f"{COLORS.LIGHT_BLACK}{self.get_model_info()}{COLORS.RESET}",
                            response
                        ]
                        
                        # Mostra box com todas as informações
                        print(self.create_box("\n".join(ai_message), COLORS.BLUE))
                        
                        # Salva mensagens após resposta da IA
                        await self.db.save_messages(self.chat.messages)
                        
                    except Exception as e:
                        # Para a animação de loading em caso de erro
                        self.loading.stop()
                        raise e
                    
                except ChatError as e:
                    error_message = [
                        f"{COLORS.LIGHT_BLACK}{self.format_timestamp()}{COLORS.RESET}",
                        f"Erro: {str(e)}"
                    ]
                    print(self.create_box("\n".join(error_message), COLORS.RED))
                
                except Exception as e:
                    error_message = [
                        f"{COLORS.LIGHT_BLACK}{self.format_timestamp()}{COLORS.RESET}",
                        f"Erro inesperado: {str(e)}"
                    ]
                    print(self.create_box("\n".join(error_message), COLORS.RED))
            
        except Exception as e:
            print(f"Erro fatal: {str(e)}")
        finally:
            # Garante que a animação de loading seja parada
            self.loading.stop()
            await self.db.close()

async def main():
    assistant = Assistant()
    await assistant.run()

if __name__ == "__main__":
    asyncio.run(main())
