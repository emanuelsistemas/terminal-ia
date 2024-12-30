import uuid
from typing import Dict, List, Optional
from datetime import datetime
from groq import Groq
from openai import OpenAI
from .logger import setup_logger
from .memory import ConversationMemory

logger = setup_logger(__name__)

class ChatError(Exception):
    pass

class ChatAssistant:
    def __init__(self, api_key: str, provider: str = "groq"):
        self.provider = provider
        self.messages: List[Dict] = []
        self.memory = ConversationMemory()
        
        # Configuração do cliente baseado no provedor
        if provider == "groq":
            self.client = Groq(api_key=api_key)
            self.model = "mixtral-8x7b-32768"
        elif provider == "deepseek":
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            self.model = "deepseek-chat"
        else:
            raise ChatError(f"Provedor {provider} não suportado")
        
        logger.info(f"Chat inicializado com provedor {provider}")
    
    async def initialize(self):
        """Inicializa o chat e carrega o contexto da memória"""
        try:
            # Inicializa a memória
            await self.memory.initialize()
            
            # Carrega mensagens anteriores da memória
            context = await self.memory.get_recent_context()
            if context:
                logger.info(f"Carregadas {len(context)} mensagens do contexto anterior")
                print("\nContexto anterior carregado:")
                for msg in context[-3:]:  # Mostra as 3 últimas mensagens do contexto
                    print(f"- {msg}")
                print()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar chat: {str(e)}")
            raise ChatError(f"Erro ao inicializar chat: {str(e)}")
    
    def add_message(self, role: str, content: str) -> str:
        """Adiciona uma mensagem ao histórico e retorna seu ID"""
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        return message_id
    
    async def clear_messages(self):
        """Limpa o histórico de mensagens e a memória"""
        self.messages = []
        await self.memory.clear()
    
    async def get_response(self) -> str:
        """Obtém resposta da IA para o histórico atual"""
        try:
            if not self.messages:
                raise ChatError("Nenhuma mensagem no histórico")
            
            # Obtém contexto relevante da memória
            last_message = self.messages[-1]["content"]
            context = await self.memory.get_relevant_context(last_message)
            
            # Prepara o prompt com contexto
            system_prompt = [
                "Você é um assistente útil e amigável.",
                "Contexto relevante da conversa:",
                *context,
                "Use este contexto para manter consistência nas respostas.",
                "Se não houver contexto relevante, responda com base no seu conhecimento geral."
            ]
            
            # Adiciona mensagem do sistema com contexto
            messages_with_context = [
                {"role": "system", "content": "\n".join(system_prompt)}
            ]
            
            # Adiciona últimas mensagens do histórico
            messages_with_context.extend([
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.messages[-5:]
            ])
            
            # Obtém resposta do modelo
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages_with_context,
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1,
                    stream=False
                )
                response = completion.choices[0].message.content
            
            elif self.provider == "deepseek":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages_with_context,
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1,
                    stream=False
                )
                response = completion.choices[0].message.content
            
            # Adiciona resposta ao histórico
            self.add_message("assistant", response)
            
            # Adiciona mensagem à memória
            await self.memory.add_message(self.messages[-1])
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao obter resposta: {str(e)}")
            raise ChatError(f"Erro ao obter resposta: {str(e)}")
