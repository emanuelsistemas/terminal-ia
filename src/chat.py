from typing import List, Dict
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
    
    def add_message(self, role: str, content: str) -> None:
        """
        Adiciona uma mensagem ao histórico.
        
        Args:
            role (str): Papel do remetente ("system", "user" ou "assistant")
            content (str): Conteúdo da mensagem
        """
        try:
            if role not in ["system", "user", "assistant"]:
                raise ChatError(f"Papel {role} inválido")
            
            self.messages.append({"role": role, "content": content})
            
        except Exception as e:
            raise ChatError(f"Erro ao adicionar mensagem: {str(e)}")
    
    async def get_response(self) -> str:
        """
        Gera uma resposta com base no histórico de mensagens.
        
        Returns:
            str: Resposta gerada
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                top_p=self.config["top_p"],
                frequency_penalty=self.config["frequency_penalty"],
                presence_penalty=self.config["presence_penalty"]
            )
            
            message = response.choices[0].message.content
            self.add_message("assistant", message)
            
            return message
            
        except Exception as e:
            raise ChatError(f"Erro ao gerar resposta: {str(e)}")
    
    def clear_messages(self) -> None:
        """
        Limpa o histórico de mensagens.
        """
        try:
            self.messages = []
            # Re-adiciona mensagem do sistema para o Deepseek
            if self.provider == "deepseek":
                self.add_message("system", "You are a helpful AI assistant.")
        except Exception as e:
            raise ChatError(f"Erro ao limpar mensagens: {str(e)}")
