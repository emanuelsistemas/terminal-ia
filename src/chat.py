from typing import List, Dict
import uuid
import openai
from .config import MODEL_CONFIGS

class ChatError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ChatAssistant:
    def __init__(self, api_key: str, provider: str = "groq"):
        """
        Inicializa o assistente de chat.
        
        Args:
            api_key (str): Chave da API do provedor
            provider (str): Nome do provedor ("groq" ou "deepseek")
        """
        try:
            if provider not in MODEL_CONFIGS:
                raise ChatError(f"Provedor {provider} não suportado")
            
            self.provider = provider
            self.config = MODEL_CONFIGS[provider]
            self.model = self.config["model"]
            
            # Define a URL base baseada no provedor
            base_url = {
                "groq": "https://api.groq.com/openai/v1",
                "deepseek": "https://api.deepseek.com/v1"
            }[provider]
            
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.messages: List[Dict[str, str]] = []
            
            # Adiciona mensagem do sistema para o Deepseek
            if provider == "deepseek":
                self.add_message("system", "You are a helpful AI assistant.")
            
        except KeyError as e:
            raise ChatError(f"Erro ao inicializar o chat: {str(e)}")
        except Exception as e:
            raise ChatError(f"Erro inesperado: {str(e)}")
    
    def add_message(self, role: str, content: str) -> str:
        """
        Adiciona uma mensagem ao histórico.
        
        Args:
            role (str): Papel do remetente ("system", "user" ou "assistant")
            content (str): Conteúdo da mensagem
            
        Returns:
            str: ID da mensagem adicionada
        """
        try:
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "role": role,
                "content": content
            }
            self.messages.append(message)
            return message_id
        except Exception as e:
            raise ChatError(f"Erro ao adicionar mensagem: {str(e)}")
    
    def clear_messages(self) -> None:
        """
        Limpa o histórico de mensagens.
        """
        try:
            # Mantém apenas a mensagem do sistema se for Deepseek
            if self.provider == "deepseek":
                self.messages = [msg for msg in self.messages if msg["role"] == "system"]
            else:
                self.messages = []
        except Exception as e:
            raise ChatError(f"Erro ao limpar mensagens: {str(e)}")
    
    async def get_response(self) -> str:
        """
        Obtém uma resposta da IA baseada no histórico de mensagens.
        
        Returns:
            str: Resposta da IA
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": msg["role"],
                    "content": msg["content"]
                } for msg in self.messages],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            response = completion.choices[0].message.content
            self.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            raise ChatError(f"Erro ao obter resposta: {str(e)}")
