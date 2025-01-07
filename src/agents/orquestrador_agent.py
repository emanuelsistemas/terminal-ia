from typing import Dict, Optional
import logging
from openai import OpenAI

from .conversa_agent import ConversaAgent
from .comando_agent import ComandoAgent
from .diretorio_agent import DiretorioAgent
from .file_agent import FileAgent
from .projeto_agent import ProjetoAgent
from .estados.estado_projeto import EstadoProjeto
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
        self.projeto = ProjetoAgent()
        
        # Inicializa o sistema de memória
        self.memory = Memory()
        
        # Inicializa o estado do projeto
        self.estado = EstadoProjeto()
        
        logger.info("OrquestradorAgent inicializado com sucesso")
    
    async def processar_mensagem(self, mensagem: str, chat_id: int) -> Dict:
        """Processa uma mensagem e retorna a resposta apropriada"""
        try:
            # Primeiro, tenta identificar se é um comando
            is_comando = await self.comando.is_comando(mensagem)
            
            if is_comando:
                # Se for comando, processa como comando
                logger.info("Processando como comando")
                resultado = await self.processar_comando(mensagem)
            else:
                # Se não for comando, processa como conversa normal
                logger.info("Processando como conversa normal")
                
                # Busca contexto relevante
                contexto = self.memory.get_context(chat_id, mensagem)
                
                # Adiciona resumo do estado ao contexto
                if self.estado.tem_projeto_ativo():
                    contexto.append({
                        "role": "system",
                        "content": f"\nContexto atual:\n{self.estado.get_resumo()}"
                    })
                
                # Processa a mensagem com o contexto
                resultado = await self.conversa.processar_mensagem(mensagem, contexto)
                
                # Se processou com sucesso, salva na memória
                if resultado["tipo"] == "sucesso":
                    self.memory.add_interaction(chat_id, mensagem, resultado["resposta"])
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Desculpe, ocorreu um erro ao processar sua mensagem. Detalhes: {str(e)}"
            }
    
    async def processar_comando(self, mensagem: str) -> Dict:
        """Processa um comando e retorna o resultado"""
        try:
            # Analisa o comando
            info_comando = await self.comando.analisar_comando(mensagem)
            
            if info_comando["tipo"] == "erro":
                return info_comando
            
            # Atualiza o estado com informações do comando
            if info_comando["tipo_comando"] == "projeto":
                # Cria o projeto
                resultado = await self.projeto.criar_projeto(info_comando["projeto"])
                if resultado["tipo"] == "sucesso":
                    # Atualiza o estado
                    self.estado.atualizar(
                        projeto_atual=info_comando["projeto"],
                        diretorio_atual=info_comando["diretorio_atual"]
                    )
                return resultado
            
            # Atualiza o estado com outras informações
            self.estado.atualizar(
                ultimo_comando=mensagem,
                diretorio_atual=info_comando.get("diretorio_atual")
            )
            
            # Processa o comando de acordo com o tipo
            if info_comando["tipo_comando"] == "diretorio":
                return await self.diretorio.processar_comando(
                    mensagem,
                    info_comando.get("diretorio_atual"),
                    info_comando
                )
                
            elif info_comando["tipo_comando"] == "arquivo":
                return await self.file.processar_comando(
                    mensagem,
                    info_comando.get("diretorio_atual"),
                    info_comando
                )
            
            else:
                return {
                    "tipo": "erro",
                    "resposta": "❌ Tipo de comando não suportado"
                }
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Desculpe, ocorreu um erro ao processar seu comando. Detalhes: {str(e)}"
            }
