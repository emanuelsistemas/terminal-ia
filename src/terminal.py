from typing import Optional
import sys
import asyncio
from .chat import ChatAssistant
from .logger import setup_logger

logger = setup_logger(__name__)

class TerminalInterface:
    def __init__(self, groq_api_key: str, deepseek_api_key: str):
        """Inicializa a interface do terminal"""
        self.groq_api_key = groq_api_key
        self.deepseek_api_key = deepseek_api_key
        self.assistant = ChatAssistant(
            api_key=self.groq_api_key,
            provider="groq"
        )
    
    def _print_help(self):
        """Mostra ajuda dos comandos"""
        help_text = """
        Comandos disponíveis:
        /help    - Mostra esta mensagem de ajuda
        /clear   - Limpa o histórico da conversa
        /provider <nome> - Muda o provedor (groq ou deepseek)
        /exit    - Sai do programa
        """
        print(help_text)
    
    def _handle_command(self, command: str) -> bool:
        """Processa comandos. Retorna True se deve continuar executando"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/help":
            self._print_help()
            return True
            
        elif cmd == "/clear":
            self.assistant.clear_messages()
            print("🧹 Histórico limpo!")
            return True
            
        elif cmd == "/provider":
            if len(parts) < 2:
                print("❌ Por favor, especifique o provider: /provider [groq|deepseek]")
                return True
            
            provider = parts[1].lower()
            if provider not in ["groq", "deepseek"]:
                print("❌ Provider inválido. Use 'groq' ou 'deepseek'")
                return True
            
            # Cria novo assistente com o provider escolhido
            api_key = self.groq_api_key if provider == "groq" else self.deepseek_api_key
            self.assistant = ChatAssistant(api_key=api_key, provider=provider)
            print(f"🔄 Provider alterado para {provider}")
            return True
            
        elif cmd == "/exit":
            print("👋 Até logo!")
            return False
        
        return True
    
    async def _process_message(self, message: str):
        """Processa uma mensagem do usuário"""
        try:
            # Adiciona mensagem do usuário
            self.assistant.add_message("user", message)
            
            # Obtém e mostra resposta
            response = await self.assistant.get_response()
            print(f"\n🤖 {response}\n")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            print("\n❌ Erro ao processar mensagem. Tente novamente.\n")
    
    def run(self):
        """Inicia a interface do terminal"""
        print("\n🤖 Assistente iniciado! Digite /help para ver os comandos.\n")
        
        while True:
            try:
                # Lê input do usuário
                message = input("👤 ").strip()
                
                # Ignora mensagens vazias
                if not message:
                    continue
                
                # Processa comandos
                if message.startswith("/"):
                    if not self._handle_command(message):
                        break
                    continue
                
                # Processa mensagem normal
                asyncio.run(self._process_message(message))
                
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
                
            except Exception as e:
                logger.error(f"Erro na interface do terminal: {str(e)}")
                print("\n❌ Ocorreu um erro. Tente novamente.\n")
