from typing import List, Dict
from datetime import datetime
import uuid
import json
from .config import DATA_DIR
from .logger import setup_logger

logger = setup_logger(__name__)

class ChatError(Exception):
    """Erro específico do chat"""
    pass

class ChatAssistant:
    def __init__(self, api_key: str, provider: str):
        self.api_key = api_key
        self.provider = provider
        self.messages_file = DATA_DIR / "messages.json"
        self.messages: List[Dict] = []
        self._load_messages()
        
    def _load_messages(self):
        """Carrega mensagens do arquivo"""
        try:
            if self.messages_file.exists():
                with open(self.messages_file, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar mensagens: {str(e)}")
            self.messages = []
    
    def _save_messages(self):
        """Salva mensagens no arquivo"""
        try:
            # Garante que o diretório existe
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(self.messages_file, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar mensagens: {str(e)}")
    
    def add_message(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico"""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        self._save_messages()
    
    def get_response(self) -> str:
        """Obtém resposta do modelo"""
        try:
            from openai import OpenAI
            
            if self.provider == "groq":
                client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                model = "mixtral-8x7b-32768"
                
            elif self.provider == "deepseek":
                client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                model = "deepseek-chat"
                
            else:
                raise ChatError(f"Provedor {self.provider} não suportado")
            
            # Prepara mensagens para o formato do OpenAI
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.messages[-10:]  # Últimas 10 mensagens
            ]
            
            # Faz a chamada para a API
            chat_completion = client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            # Extrai e salva a resposta
            response = chat_completion.choices[0].message.content
            self.add_message("assistant", response)
            
            return response
                
        except Exception as e:
            logger.error(f"Erro ao obter resposta: {str(e)}")
            raise ChatError(f"Erro ao obter resposta: {str(e)}")
    
    def clear_messages(self):
        """Limpa o histórico de mensagens"""
        try:
            self.messages = []
            if self.messages_file.exists():
                self.messages_file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar mensagens: {str(e)}")
            raise ChatError(f"Erro ao limpar mensagens: {str(e)}")
