from typing import Dict, Optional
import logging
from openai import OpenAI

from .conversa_agent import ConversaAgent
from .comando_agent import ComandoAgent
from .diretorio_agent import DiretorioAgent
from .file_agent import FileAgent
from .projeto_agent import ProjetoAgent
from .estados.estado_projeto import EstadoProjeto
from .estados.streaming_state import StreamingState
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
        
        # Inicializa o streaming de estados
        self.streaming = StreamingState()
        
        logger.info("OrquestradorAgent inicializado com sucesso")
    
    async def processar_mensagem(self, mensagem: str, chat_id: int) -> Dict:
        """Processa uma mensagem e retorna a resposta apropriada"""
        try:
            # Inicia o streaming para esta mensagem
            self.streaming.iniciar_fluxo(
                chat_id,
                f"Processando mensagem: {mensagem[:50]}..."
            )
            
            # Primeiro, tenta identificar se é um comando
            self.streaming.adicionar_estado(
                "ComandoAgent",
                "Analisando se é um comando",
                "processando"
            )
            is_comando = await self.comando.is_comando(mensagem)
            
            if is_comando:
                self.streaming.atualizar_ultimo_estado(
                    "sucesso",
                    "É um comando"
                )
                
                # Se for comando, processa como comando
                logger.info("Processando como comando")
                self.streaming.adicionar_estado(
                    "ComandoAgent",
                    "Processando comando",
                    "processando"
                )
                resultado = await self.processar_comando(mensagem)
                
                if resultado["tipo"] == "sucesso":
                    self.streaming.atualizar_ultimo_estado("sucesso")
                else:
                    self.streaming.atualizar_ultimo_estado("erro")
            else:
                self.streaming.atualizar_ultimo_estado(
                    "sucesso",
                    "Não é um comando"
                )
                
                # Se não for comando, processa como conversa normal
                logger.info("Processando como conversa normal")
                self.streaming.adicionar_estado(
                    "ConversaAgent",
                    "Processando mensagem",
                    "processando"
                )
                
                # Busca contexto relevante
                self.streaming.adicionar_estado(
                    "MemoryAgent",
                    "Buscando contexto relevante",
                    "processando"
                )
                contexto = self.memory.get_context(chat_id, mensagem)
                self.streaming.atualizar_ultimo_estado("sucesso")
                
                # Adiciona resumo do estado ao contexto
                if self.estado.tem_projeto_ativo():
                    self.streaming.adicionar_estado(
                        "EstadoAgent",
                        "Adicionando contexto do projeto",
                        "processando"
                    )
                    contexto.append({
                        "role": "system",
                        "content": f"\nContexto atual:\n{self.estado.get_resumo()}"
                    })
                    self.streaming.atualizar_ultimo_estado("sucesso")
                
                # Processa a mensagem com o contexto
                self.streaming.adicionar_estado(
                    "ConversaAgent",
                    "Gerando resposta",
                    "processando"
                )
                resultado = await self.conversa.processar_mensagem(mensagem, contexto)
                
                # Se processou com sucesso, salva na memória
                if resultado["tipo"] == "sucesso":
                    self.streaming.atualizar_ultimo_estado("sucesso")
                    self.streaming.adicionar_estado(
                        "MemoryAgent",
                        "Salvando interação na memória",
                        "processando"
                    )
                    self.memory.add_interaction(chat_id, mensagem, resultado["resposta"])
                    self.streaming.atualizar_ultimo_estado("sucesso")
                else:
                    self.streaming.atualizar_ultimo_estado("erro")
            
            # Finaliza o streaming
            self.streaming.finalizar_fluxo(resultado["tipo"] == "sucesso")
            
            # Adiciona o estado do streaming à resposta
            resultado["streaming"] = self.streaming.get_mensagem_streaming()
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            self.streaming.adicionar_estado(
                "Sistema",
                f"Erro: {str(e)}",
                "erro"
            )
            self.streaming.finalizar_fluxo(False)
            
            return {
                "tipo": "erro",
                "resposta": f"❌ Desculpe, ocorreu um erro ao processar sua mensagem. Detalhes: {str(e)}",
                "streaming": self.streaming.get_mensagem_streaming()
            }
    
    async def processar_comando(self, mensagem: str) -> Dict:
        """Processa um comando e retorna o resultado"""
        try:
            # Analisa o comando
            self.streaming.adicionar_estado(
                "ComandoAgent",
                "Analisando comando",
                "processando"
            )
            info_comando = await self.comando.analisar_comando(mensagem)
            
            if info_comando["tipo"] == "erro":
                self.streaming.atualizar_ultimo_estado("erro")
                return info_comando
            
            self.streaming.atualizar_ultimo_estado("sucesso")
            
            # Se for uma pergunta, retorna direto
            if info_comando["tipo"] == "pergunta":
                return info_comando
            
            # Atualiza o estado com informações do comando
            if info_comando["tipo_comando"] == "projeto":
                # Cria o projeto
                self.streaming.adicionar_estado(
                    "ProjetoAgent",
                    "Criando novo projeto",
                    "criando"
                )
                resultado = await self.projeto.criar_projeto(
                    info_comando["projeto"],
                    info_comando.get("caminho_base")
                )
                
                if resultado["tipo"] == "sucesso":
                    # Atualiza o estado
                    self.streaming.atualizar_ultimo_estado("sucesso")
                    self.streaming.adicionar_estado(
                        "EstadoAgent",
                        "Atualizando estado do projeto",
                        "processando"
                    )
                    self.estado.atualizar(
                        projeto_atual=info_comando["projeto"],
                        diretorio_atual=info_comando["diretorio_atual"]
                    )
                    self.streaming.atualizar_ultimo_estado("sucesso")
                else:
                    self.streaming.atualizar_ultimo_estado("erro")
                
                return resultado
            
            # Atualiza o estado com outras informações
            self.streaming.adicionar_estado(
                "EstadoAgent",
                "Atualizando estado",
                "processando"
            )
            self.estado.atualizar(
                ultimo_comando=mensagem,
                diretorio_atual=info_comando.get("diretorio_atual")
            )
            self.streaming.atualizar_ultimo_estado("sucesso")
            
            # Processa o comando de acordo com o tipo
            if info_comando["tipo_comando"] == "diretorio":
                self.streaming.adicionar_estado(
                    "DiretorioAgent",
                    "Processando comando de diretório",
                    "processando"
                )
                resultado = await self.diretorio.processar_comando(
                    mensagem,
                    info_comando.get("diretorio_atual"),
                    info_comando
                )
                self.streaming.atualizar_ultimo_estado(
                    "sucesso" if resultado["tipo"] == "sucesso" else "erro"
                )
                return resultado
                
            elif info_comando["tipo_comando"] == "arquivo":
                self.streaming.adicionar_estado(
                    "FileAgent",
                    "Processando comando de arquivo",
                    "processando"
                )
                resultado = await self.file.processar_comando(
                    mensagem,
                    info_comando.get("diretorio_atual"),
                    info_comando
                )
                self.streaming.atualizar_ultimo_estado(
                    "sucesso" if resultado["tipo"] == "sucesso" else "erro"
                )
                return resultado
            
            else:
                self.streaming.adicionar_estado(
                    "Sistema",
                    "Tipo de comando não suportado",
                    "erro"
                )
                return {
                    "tipo": "erro",
                    "resposta": "❌ Tipo de comando não suportado"
                }
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            self.streaming.adicionar_estado(
                "Sistema",
                f"Erro ao processar comando: {str(e)}",
                "erro"
            )
            return {
                "tipo": "erro",
                "resposta": f"❌ Desculpe, ocorreu um erro ao processar seu comando. Detalhes: {str(e)}"
            }
