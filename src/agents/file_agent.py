from pathlib import Path
from typing import Dict, List
import logging
import os

logger = logging.getLogger(__name__)

class FileAgent:
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
            if info_comando and info_comando.get("detalhes"):
                info = info_comando["detalhes"]
            else:
                return {
                    "sucesso": False,
                    "mensagem": "Não foi possível entender as informações do arquivo",
                    "processo": self._processo_log
                }
            
            # Usa o diretório atual se fornecido, senão usa o workspace
            if diretorio_atual:
                caminho_base = diretorio_atual
            else:
                caminho_base = str(self.workspace)
            
            # Constrói o caminho completo
            caminho_completo = os.path.join(caminho_base, info["nome"])
            
            # Processo de criação com feedback
            self._add_log("🔄 Analisando seu comando...")
            self._add_log("✓ Comando interpretado corretamente")
            
            self._add_log("🔄 Verificando diretório...")
            # Verifica se tem permissão para criar no diretório
            if not os.access(os.path.dirname(caminho_completo), os.W_OK):
                return {
                    "sucesso": False,
                    "mensagem": f"Sem permissão para criar arquivo em {os.path.dirname(caminho_completo)}",
                    "processo": self._processo_log
                }
            self._add_log("✓ Diretório encontrado e com permissões corretas")
            
            self._add_log("🔄 Criando arquivo...")
            # Tenta criar o arquivo
            try:
                with open(caminho_completo, 'w') as f:
                    f.write(info.get("conteudo", ""))
                self._add_log("✓ Arquivo criado com sucesso!")
            except Exception as e:
                return {
                    "sucesso": False,
                    "mensagem": f"Erro ao criar arquivo: {str(e)}",
                    "processo": self._processo_log
                }
            
            # Verifica se o arquivo foi realmente criado
            if not os.path.exists(caminho_completo):
                return {
                    "sucesso": False,
                    "mensagem": "Falha ao criar arquivo",
                    "processo": self._processo_log
                }
            
            # Adiciona informações ao resultado
            info["caminho_base"] = caminho_base
            info["caminho_completo"] = caminho_completo
            info["permissoes"] = oct(os.stat(caminho_completo).st_mode)[-3:]
            info["tamanho"] = f"{os.path.getsize(caminho_completo)/1024:.1f}K"
            
            return {
                "sucesso": True,
                "mensagem": f"Arquivo \"{info['nome']}\" criado com sucesso!",
                "processo": self._processo_log,
                "info": info
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro: {str(e)}",
                "processo": self._processo_log
            }
