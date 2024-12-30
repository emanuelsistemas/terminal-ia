import uuid
from typing import Dict, List, Optional
from datetime import datetime
from groq import Groq
from openai import OpenAI
from .logger import setup_logger
from .memory import ConversationMemory
from .prompts.system import (
    get_system_prompt,
    get_conversation_summary_prompt,
    process_user_message,
    get_response_format_prompt
)

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
                
                # Gera resumo das conversas anteriores
                summary = await self._get_conversation_summary(context)
                if summary:
                    print("\n" + summary + "\n")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar chat: {str(e)}")
            raise ChatError(f"Erro ao inicializar chat: {str(e)}")
    
    async def _get_conversation_summary(self, context: List[str]) -> str:
        """Gera um resumo das conversas anteriores"""
        try:
            # Prepara o prompt para o resumo
            messages = [
                {"role": "system", "content": get_conversation_summary_prompt(self.messages)},
                {"role": "user", "content": "Gere um resumo amigável das conversas anteriores."}
            ]
            
            # Obtém o resumo do modelo
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return completion.choices[0].message.content
            
            elif self.provider == "deepseek":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return ""
    
    async def _process_user_message(self, message: str) -> str:
        """Processa a mensagem do usuário para melhor compreensão"""
        try:
            # Prepara o prompt para processar a mensagem
            messages = [
                {"role": "system", "content": process_user_message(message)},
                {"role": "user", "content": "Reformule esta mensagem para melhor compreensão."}
            ]
            
            # Obtém a mensagem processada do modelo
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,  # Menor temperatura para maior precisão
                    max_tokens=200
                )
                return completion.choices[0].message.content
            
            elif self.provider == "deepseek":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=200
                )
                return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return message  # Retorna mensagem original em caso de erro
    
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
            
            # Processa a última mensagem do usuário
            last_message = self.messages[-1]["content"]
            processed_message = await self._process_user_message(last_message)
            
            # Obtém contexto relevante da memória
            context = await self.memory.get_relevant_context(processed_message)
            
            # Prepara as mensagens para o modelo
            messages = [
                # Prompt principal do sistema
                {"role": "system", "content": get_system_prompt(context)},
                # Formato das respostas
                {"role": "system", "content": get_response_format_prompt()}
            ]
            
            # Adiciona últimas mensagens do histórico
            messages.extend([
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.messages[-5:]
            ])
            
            # Substitui a última mensagem pela versão processada
            if len(messages) > 2:  # Garante que há mensagens além dos prompts do sistema
                messages[-1]["content"] = processed_message
            
            # Obtém resposta do modelo
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1,
                    stream=False
                )
                response = completion.choices[0].message.content
            
            elif self.provider == "deepseek":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
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
