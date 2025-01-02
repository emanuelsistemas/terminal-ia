from typing import List, Dict
from datetime import datetime
import uuid
import json
from pathlib import Path
from groq import Groq
from openai import OpenAI

DATA_DIR = Path("/root/projetos/chat-ia-terminal/data")

class ChatError(Exception):
    pass

class ChatAssistant:
    def __init__(self, api_key: str, provider: str):
        self.api_key = api_key
        self.provider = provider
        self.messages_file = DATA_DIR / "messages.json"
        self.messages: List[Dict] = []
        self._load_messages()
    
    def _load_messages(self):
        try:
            if self.messages_file.exists():
                with open(self.messages_file, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar mensagens: {str(e)}")
            self.messages = []
    
    def _save_messages(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.messages_file, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar mensagens: {str(e)}")
    
    def add_message(self, role: str, content: str):
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        self._save_messages()
    
    async def async_chat(self, message: str) -> str:
        try:
            self.add_message("user", message)
            
            if self.provider == "groq":
                client = Groq(api_key=self.api_key)
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "user", "content": message}]
                )
            else:  # deepseek
                client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1")
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": message}]
                )
            
            assistant_message = response.choices[0].message.content
            self.add_message("assistant", assistant_message)
            return assistant_message
        
        except Exception as e:
            print(f"Erro no chat assíncrono: {str(e)}")
            raise ChatError(f"Erro ao processar mensagem: {str(e)}")
