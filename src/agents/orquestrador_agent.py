from typing import Dict, Optional
import logging
from openai import OpenAI

from .conversa_agent import ConversaAgent
from .comando_agent import ComandoAgent
from .diretorio_agent import DiretorioAgent
from .file_agent import FileAgent
from ..memory import Memory

logger = logging.getLogger(__name__)

class OrquestradorAgent:
    def __init__(self, groq_api_key: str):
        # Inicializa o cliente OpenAI
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key
        )
        
        # Inicializa os agentes
        self.conversa = ConversaAgent(self.client)
        self.comando = ComandoAgent(self.client)
        self.diretorio = DiretorioAgent()
        self.file = FileAgent()
        
        # Inicializa o sistema de memória
        self.memory = Memory()
        
        logger.info("OrquestradorAgent inicializado com sucesso")
    
    async def processar_mensagem(self, mensagem: str, chat_id: int) -> Dict:
        """Processa uma mensagem e retorna a resposta apropriada"""
        try:
            # Primeiro, tenta identificar se é um comando
            is_comando = await self.comando.is_comando(mensagem)
            
            if is_comando:
                # Se for comando, processa como comando
                logger.info("Processando como comando")
                return await self.processar_comando(mensagem)
            else:
                # Se não for comando, processa como conversa normal
                logger.info("Processando como conversa normal")
                
                # Busca contexto relevante
                contexto = self.memory.get_context(chat_id, mensagem)
                
                # Processa a mensagem com o contexto
                resultado = await self.conversa.processar_mensagem(mensagem, contexto)
                
                # Se processou com sucesso, salva na memória
                if resultado["sucesso"]:
                    self.memory.add_message(chat_id, "user", mensagem)
                    self.memory.add_message(chat_id, "assistant", resultado["resposta"])
                
                return resultado
            
        except Exception as e:
            logger.error(f"Erro no OrquestradorAgent: {e}")
            return {
                "tipo": "erro",
                "mensagem": "Ocorreu um erro ao processar sua mensagem"
            }
    
    async def processar_comando(self, mensagem: str) -> Dict:
        """Processa um comando identificado"""
        try:
            # Analisa o comando
            comando = await self.comando.analisar_comando(mensagem)
            
            if not comando["sucesso"]:
                return {
                    "tipo": "erro",
                    "mensagem": comando["erro"]
                }
            
            # Executa baseado no tipo
            if comando["tipo"] == "criar_arquivo":
                resultado = await self.file.criar_arquivo(
                    comando["info"]["nome"],
                    comando["info"]["conteudo"],
                    comando["info"].get("caminho", "")
                )
                resultado["tipo"] = "comando_arquivo"
                return resultado
                
            elif comando["tipo"] == "criar_diretorio":
                resultado = await self.diretorio.criar_diretorio(
                    comando["info"]["nome"],
                    comando["info"].get("caminho", "")
                )
                resultado["tipo"] = "comando_diretorio"
                return resultado
            
            else:
                return {
                    "tipo": "erro",
                    "mensagem": "Tipo de comando não suportado"
                }
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            return {
                "tipo": "erro",
                "mensagem": "Erro ao processar o comando"
            }
