from typing import Dict
import logging
from openai import OpenAI

from .analisador_agent import AnalisadorAgent
from .conversa_agent import ConversaAgent
from .diretorio_agent import DiretorioAgent
from .file_agent import FileAgent

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
        
        # Mantém o contexto por chat
        self.contexto = {}
        
        # Modelo atual para análise
        self.modelo_analise = "mixtral"
    
    def set_modelo_analise(self, modelo: str):
        """Define qual modelo será usado para análise"""
        if modelo in ["mixtral", "gpt4", "deepseek"]:
            self.modelo_analise = modelo
            logger.info(f"Modelo de análise alterado para: {modelo}")
    
    async def processar_mensagem(self, mensagem: str, chat_id: int) -> Dict:
        try:
            # Analisa a mensagem para determinar o tipo
            analise = await self.analisador.analisar_mensagem(mensagem, self.modelo_analise)
            logger.info(f"Análise concluída usando {self.modelo_analise}: {analise}")
            
            if not analise["sucesso"]:
                return {
                    "tipo": "erro",
                    "mensagem": "Não consegui entender sua mensagem. Pode tentar de outro jeito?"
                }
            
            # Obtém o contexto do chat atual
            contexto_chat = self.contexto.get(chat_id, {})
            logger.info(f"Contexto atual para chat {chat_id}: {contexto_chat}")
            
            # Processa baseado no tipo
            if analise["tipo"] == "conversa":
                logger.info("Encaminhando para ConversaAgent")
                resultado = await self.conversa.processar_mensagem(mensagem)
                return {"tipo": "conversa", **resultado}
            
            elif analise["tipo"] == "comando_diretorio":
                logger.info("Encaminhando para DiretorioAgent")
                resultado = await self.diretorio.processar_comando(
                    mensagem,
                    contexto_chat.get("diretorio_atual"),
                    analise
                )
                return {"tipo": "comando_diretorio", **resultado}
            
            elif analise["tipo"] == "comando_arquivo":
                logger.info("Encaminhando para FileAgent")
                resultado = await self.file.processar_comando(
                    mensagem,
                    contexto_chat.get("diretorio_atual"),
                    analise
                )
                return {"tipo": "comando_arquivo", **resultado}
            
            else:
                return {
                    "tipo": "erro",
                    "mensagem": "Desculpe, não sei como processar esse tipo de comando."
                }
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "tipo": "erro",
                "mensagem": f"Erro ao processar mensagem: {str(e)}"
            }
