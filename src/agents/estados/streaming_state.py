from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StreamingState:
    def __init__(self):
        self.fluxo_atual: List[Dict] = []
        self.chat_id: Optional[int] = None
        
    def iniciar_fluxo(self, chat_id: int, descricao: str):
        """Inicia um novo fluxo de trabalho"""
        self.chat_id = chat_id
        self.fluxo_atual = [{
            "timestamp": datetime.now().isoformat(),
            "agente": "Sistema",
            "acao": "🔄 Iniciando novo fluxo de trabalho",
            "descricao": descricao,
            "status": "iniciado"
        }]
        logger.info(f"Fluxo iniciado: {descricao}")
    
    def adicionar_estado(self, agente: str, acao: str, status: str = "processando"):
        """Adiciona um novo estado ao fluxo"""
        emoji = self._get_status_emoji(status)
        estado = {
            "timestamp": datetime.now().isoformat(),
            "agente": agente,
            "acao": f"{emoji} {acao}",
            "status": status
        }
        self.fluxo_atual.append(estado)
        logger.info(f"Estado adicionado: {agente} - {acao} ({status})")
        
    def atualizar_ultimo_estado(self, status: str, descricao: Optional[str] = None):
        """Atualiza o status do último estado adicionado"""
        if self.fluxo_atual:
            ultimo_estado = self.fluxo_atual[-1]
            emoji = self._get_status_emoji(status)
            
            # Atualiza a ação com o novo emoji
            acao_sem_emoji = ultimo_estado["acao"].split(" ", 1)[1]
            ultimo_estado["acao"] = f"{emoji} {acao_sem_emoji}"
            
            ultimo_estado["status"] = status
            if descricao:
                ultimo_estado["descricao"] = descricao
            
            logger.info(f"Estado atualizado: {ultimo_estado['agente']} - {status}")
    
    def finalizar_fluxo(self, sucesso: bool = True):
        """Finaliza o fluxo atual"""
        status = "sucesso" if sucesso else "erro"
        self.adicionar_estado(
            "Sistema",
            "Fluxo de trabalho finalizado",
            status
        )
        logger.info(f"Fluxo finalizado: {status}")
    
    def get_mensagem_streaming(self) -> str:
        """Retorna uma mensagem formatada com o estado atual do streaming"""
        if not self.fluxo_atual:
            return "Nenhum fluxo em andamento"
        
        mensagem = "🔄 Fluxo de Trabalho:\n\n"
        
        for estado in self.fluxo_atual:
            # Formata o timestamp para hora:minuto:segundo
            timestamp = datetime.fromisoformat(estado["timestamp"]).strftime("%H:%M:%S")
            
            mensagem += f"[{timestamp}] {estado['agente']}:\n"
            mensagem += f"  {estado['acao']}\n"
            
            if "descricao" in estado:
                mensagem += f"  └─ {estado['descricao']}\n"
            
            mensagem += "\n"
        
        return mensagem
    
    def _get_status_emoji(self, status: str) -> str:
        """Retorna o emoji apropriado para cada status"""
        return {
            "iniciado": "🔄",
            "processando": "⏳",
            "sucesso": "✅",
            "erro": "❌",
            "aguardando": "⏸️",
            "validando": "🔍",
            "criando": "🛠️",
            "configurando": "⚙️",
        }.get(status, "❓")
