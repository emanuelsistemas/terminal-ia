from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EstadoProjeto:
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """Reseta o estado para valores padrão"""
        self._estado = {
            "projeto_atual": None,
            "branch_atual": None,
            "diretorio_atual": None,
            "ultimo_comando": None,
            "timestamp": None,
            "contexto_adicional": {}
        }
    
    def atualizar(self, **kwargs) -> None:
        """Atualiza o estado com novos valores"""
        for key, value in kwargs.items():
            if key in self._estado:
                self._estado[key] = value
        self._estado["timestamp"] = datetime.now().isoformat()
        logger.info(f"Estado atualizado: {self.get_resumo()}")
    
    def get_estado(self) -> Dict:
        """Retorna o estado completo"""
        return self._estado.copy()
    
    def get_resumo(self) -> str:
        """Retorna um resumo do estado atual em formato legível"""
        if not self._estado["projeto_atual"]:
            return "🤖 Nenhum projeto selecionado"
        
        resumo = f"🚀 Projeto: {self._estado['projeto_atual']}"
        
        if self._estado["branch_atual"]:
            resumo += f"\n📌 Branch: {self._estado['branch_atual']}"
        
        if self._estado["diretorio_atual"]:
            resumo += f"\n📂 Diretório: {self._estado['diretorio_atual']}"
        
        if self._estado["ultimo_comando"]:
            resumo += f"\n⚡ Último comando: {self._estado['ultimo_comando']}"
        
        return resumo
    
    def tem_projeto_ativo(self) -> bool:
        """Verifica se há um projeto ativo"""
        return bool(self._estado["projeto_atual"])
    
    def get_projeto_atual(self) -> Optional[str]:
        """Retorna o nome do projeto atual"""
        return self._estado["projeto_atual"]
    
    def get_branch_atual(self) -> Optional[str]:
        """Retorna o nome da branch atual"""
        return self._estado["branch_atual"]
