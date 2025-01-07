from typing import Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

class FileAgent:
    def __init__(self):
        self.workspace = "/root/projetos"
        logger.info(f"✓ Workspace configurado em {self.workspace}")
    
    async def processar_comando(self, mensagem: str, diretorio_atual: Optional[str], info_comando: Dict) -> Dict:
        """Processa um comando relacionado a arquivos"""
        try:
            if not diretorio_atual:
                return {
                    "tipo": "erro",
                    "resposta": "❌ Nenhum diretório selecionado. Use /projeto primeiro."
                }
            
            caminho_completo = os.path.join(diretorio_atual, info_comando["nome"])
            
            if info_comando["operacao"] == "criar":
                if info_comando["tipo_arquivo"] == "arquivo":
                    # Cria um arquivo vazio
                    with open(caminho_completo, "w") as f:
                        pass
                else:
                    # Cria um diretório
                    os.makedirs(caminho_completo, exist_ok=True)
                
                return {
                    "tipo": "sucesso",
                    "resposta": f"✅ {'Arquivo' if info_comando['tipo_arquivo'] == 'arquivo' else 'Diretório'} {info_comando['nome']} criado em {diretorio_atual}"
                }
            
            else:
                return {
                    "tipo": "erro",
                    "resposta": f"❌ Operação {info_comando['operacao']} não suportada"
                }
            
        except Exception as e:
            logger.error(f"Erro ao processar comando de arquivo: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Erro ao processar comando: {str(e)}"
            }
