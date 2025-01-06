from pathlib import Path
from typing import Dict, List
import logging
import os

logger = logging.getLogger(__name__)

class DiretorioAgent:
    def __init__(self):
        # Diretório padrão para operações
        self.workspace = Path("/root/projetos/chat-ia-terminal/workspace")
        
        # Log de processo
        self._processo_log: List[str] = []
        
        # Garante que o workspace existe
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._add_log(f"✓ Workspace configurado em {self.workspace}")
    
    def _add_log(self, mensagem: str) -> None:
        """Adiciona uma mensagem ao log do processo"""
        self._processo_log.append(mensagem)
        logger.info(mensagem)
    
    def get_processo_log(self) -> List[str]:
        """Retorna o log do processo atual"""
        return self._processo_log
    
    async def processar_comando(self, comando: str, diretorio_atual: str = None, info_comando: Dict = None) -> Dict:
        # Limpa o log anterior
        self._processo_log = []
        
        try:
            # Usa as informações do AnalisadorAgent se disponíveis
            if info_comando and info_comando.get("detalhes", {}).get("nome"):
                nome_dir = info_comando["detalhes"]["nome"]
            else:
                return {
                    "sucesso": False,
                    "mensagem": "Não foi possível entender o nome do diretório",
                    "processo": self._processo_log
                }
            
            # Usa o diretório atual se fornecido, senão usa o workspace
            if diretorio_atual:
                caminho_base = diretorio_atual
            else:
                caminho_base = str(self.workspace)
            
            # Remove aspas do nome se presentes
            nome_dir = nome_dir.strip('"\'')
            
            # Constrói o caminho completo
            caminho_completo = os.path.join(caminho_base, nome_dir)
            
            # Processo de criação com feedback
            self._add_log("🔄 Analisando seu comando...")
            self._add_log("✓ Comando interpretado corretamente")
            
            self._add_log("🔄 Verificando permissões...")
            # Verifica se tem permissão para criar no diretório pai
            if not os.access(os.path.dirname(caminho_completo), os.W_OK):
                return {
                    "sucesso": False,
                    "mensagem": f"Sem permissão para criar diretório em {os.path.dirname(caminho_completo)}",
                    "processo": self._processo_log
                }
            self._add_log("✓ Permissões verificadas")
            
            self._add_log("🔄 Criando diretório...")
            # Tenta criar o diretório
            try:
                os.makedirs(caminho_completo, exist_ok=True)
                self._add_log("✓ Diretório criado com sucesso!")
            except Exception as e:
                return {
                    "sucesso": False,
                    "mensagem": f"Erro ao criar diretório: {str(e)}",
                    "processo": self._processo_log
                }
            
            # Verifica se o diretório foi realmente criado
            if not os.path.exists(caminho_completo):
                return {
                    "sucesso": False,
                    "mensagem": "Falha ao criar diretório",
                    "processo": self._processo_log
                }
            
            return {
                "sucesso": True,
                "mensagem": f"Diretório \"{nome_dir}\" criado com sucesso!",
                "processo": self._processo_log,
                "info": {
                    "nome": nome_dir,
                    "caminho_completo": caminho_completo,
                    "permissoes": oct(os.stat(caminho_completo).st_mode)[-3:]
                }
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro: {str(e)}",
                "processo": self._processo_log
            }
