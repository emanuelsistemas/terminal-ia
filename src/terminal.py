from typing import Optional, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from pathlib import Path
import json
import asyncio
from datetime import datetime

class TerminalInterface:
    def __init__(self, data_dir: str = "/root/projetos/chat-ia-terminal/data"):
        self.data_dir = Path(data_dir)
        self.history_file = self.data_dir / "terminal_history"
        
        # Configura o prompt
        self.session = PromptSession(
            history=FileHistory(str(self.history_file))
        )
        
        # Estilo do terminal
        self.style = Style.from_dict({
            "prompt": "#00aa00 bold",
            "command": "#884444",
            "output": "#448844",
            "error": "#ff0000",
            "info": "#0000ff"
        })
        
        # Comandos disponíveis
        self.commands = {
            "help": self.show_help,
            "clear": self.clear_screen,
            "exit": self.exit_terminal,
            "status": self.show_status,
            "provider": self.change_provider,
            "config": self.manage_config,
            "logs": self.view_logs,
            "backup": self.manage_backup,
            "knowledge": self.manage_knowledge
        }
        
        # Auto-completar
        self.completer = WordCompleter(
            list(self.commands.keys()) + 
            ["groq", "deepseek", "show", "set", "reset", "list", "search", "add"]
        )
    
    async def show_help(self, args: Optional[str] = None):
        """Mostra ajuda sobre comandos disponíveis"""
        help_text = """
        Comandos disponíveis:
        
        help                    - Mostra esta mensagem de ajuda
        clear                   - Limpa a tela
        exit                    - Sai do terminal
        status                  - Mostra status atual do sistema
        provider [nome]         - Muda ou mostra o provedor atual
        config [show|set|reset] - Gerencia configurações
        logs [filtros]          - Visualiza logs do sistema
        backup [create|restore] - Gerencia backups
        knowledge [comandos]    - Gerencia base de conhecimento
        """
        print(help_text)
    
    async def clear_screen(self, args: Optional[str] = None):
        """Limpa a tela do terminal"""
        print("\033[2J\033[H", end="")
    
    async def exit_terminal(self, args: Optional[str] = None):
        """Sai do terminal"""
        print("\nAté logo!")
        return True
    
    async def show_status(self, args: Optional[str] = None):
        """Mostra status do sistema"""
        # Implementar lógica de status
        pass
    
    async def change_provider(self, args: Optional[str] = None):
        """Muda ou mostra o provedor atual"""
        # Implementar lógica de mudança de provedor
        pass
    
    async def manage_config(self, args: Optional[str] = None):
        """Gerencia configurações do sistema"""
        # Implementar lógica de configuração
        pass
    
    async def view_logs(self, args: Optional[str] = None):
        """Visualiza logs do sistema"""
        # Implementar lógica de visualização de logs
        pass
    
    async def manage_backup(self, args: Optional[str] = None):
        """Gerencia backups do sistema"""
        # Implementar lógica de backup
        pass
    
    async def manage_knowledge(self, args: Optional[str] = None):
        """Gerencia base de conhecimento"""
        # Implementar lógica de conhecimento
        pass
    
    async def process_command(self, command: str) -> bool:
        """Processa um comando do usuário"""
        if not command.strip():
            return False
        
        # Separa comando e argumentos
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None
        
        # Executa o comando
        if cmd in self.commands:
            try:
                result = await self.commands[cmd](args)
                return result if isinstance(result, bool) else False
            except Exception as e:
                print(f"Erro ao executar comando: {str(e)}")
                return False
        else:
            print(f"Comando desconhecido: {cmd}")
            return False
    
    async def run(self):
        """Inicia o terminal interativo"""
        print("Bem-vindo ao Terminal do ChatBot!\nDigite 'help' para ver os comandos disponíveis.\n")
        
        while True:
            try:
                # Obtém comando do usuário
                command = await self.session.prompt_async(
                    ">>> ",
                    style=self.style,
                    completer=self.completer
                )
                
                # Processa comando
                should_exit = await self.process_command(command)
                if should_exit:
                    break
                    
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Erro: {str(e)}")
        
        print("\nEncerrando terminal...")
