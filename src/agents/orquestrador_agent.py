from typing import Dict
import logging
from openai import OpenAI

from .analisador_agent import AnalisadorAgent
from .conversa_agent import ConversaAgent
from .diretorio_agent import DiretorioAgent
from .file_agent import FileAgent
from ..memory import Memory

logger = logging.getLogger(__name__)

class OrquestradorAgent:
    def __init__(self, groq_api_key: str, deepseek_api_key: str = None):
        # Inicializa os clientes
        self.groq_client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
        
        # Inicializa os agentes
        self.analisador = AnalisadorAgent(self.groq_client)
        self.conversa = ConversaAgent(self.groq_client)
        self.diretorio = DiretorioAgent()
        self.file = FileAgent()
        
        # Inicializa o sistema de memória
        self.memory = Memory()
        
        # Modelo atual para análise
        self.modelo_analise = "mixtral"
    
    def set_modelo_analise(self, modelo: str):
        """Define qual modelo será usado para análise"""
        if modelo in ["mixtral", "gpt4", "deepseek"]:
            self.modelo_analise = modelo
            logger.info(f"Modelo de análise alterado para: {modelo}")
    
    async def processar_mensagem(self, mensagem: str, chat_id: int) -> Dict:
        try:
            # Adiciona mensagem do usuário à memória
            self.memory.add_message(chat_id, "user", mensagem)
            
            # Obtém contexto relevante
            contexto = self.memory.get_context(chat_id, mensagem)
            
            # Analisa a mensagem para determinar o tipo
            analise = await self.analisador.analisar_mensagem(mensagem, self.modelo_analise)
            logger.info(f"Análise concluída usando {self.modelo_analise}: {analise}")
            
            if not analise["sucesso"]:
                return {
                    "tipo": "erro",
                    "mensagem": "Não consegui entender sua mensagem. Pode tentar de outro jeito?"
                }
            
            # Processa baseado no tipo
            if analise["tipo"] == "comando_arquivo":
                resultado = await self.file.processar_comando(
                    mensagem,
                    info_comando=analise
                )
                if resultado["sucesso"]:
                    self.memory.add_message(chat_id, "assistant", str(resultado))
                return {**resultado, "tipo": "comando_arquivo"}
                
            elif analise["tipo"] == "comando_diretorio":
                resultado = await self.diretorio.processar_comando(
                    mensagem,
                    info_comando=analise
                )
                if resultado["sucesso"]:
                    self.memory.add_message(chat_id, "assistant", str(resultado))
                return {**resultado, "tipo": "comando_diretorio"}
                
            else:  # conversa normal
                resultado = await self.conversa.processar_mensagem(mensagem, contexto)
                if resultado["sucesso"]:
                    self.memory.add_message(chat_id, "assistant", resultado["resposta"])
                return {**resultado, "tipo": "conversa"}
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "tipo": "erro",
                "mensagem": "Ocorreu um erro ao processar sua mensagem"
            }
