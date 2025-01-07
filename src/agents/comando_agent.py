from typing import Dict, Optional
import logging
import osimport shutil

logger = logging.getLogger(__name__)

class ComandoAgent:
    def __init__(self, client):
        self.client = client
    
    async def is_comando(self, mensagem: str) -> bool:
        """Verifica se a mensagem é um comando"""
        return mensagem.startswith("/")
    
    async def analisar_comando(self, mensagem: str) -> Dict:
        """Analisa um comando e retorna informações sobre ele"""
        try:
            partes = mensagem.split()
            comando = partes[0].lower()
            
            # Comandos de projeto
            if comando == "/projeto":
                if len(partes) < 2:
                    return {
                        "tipo": "erro",
                        "resposta": "❌ Por favor, especifique o nome do projeto"
                    }
                
                nome_projeto = partes[1]
                caminho_projeto = f"/root/projetos/{nome_projeto}"
                
                # Cria o diretório do projeto se não existir
                if not os.path.exists(caminho_projeto):
                    os.makedirs(caminho_projeto)
                    os.makedirs(f"{caminho_projeto}/src")
                    os.makedirs(f"{caminho_projeto}/src/components")
                    os.makedirs(f"{caminho_projeto}/src/pages")
                    os.makedirs(f"{caminho_projeto}/src/services")
                    os.makedirs(f"{caminho_projeto}/src/types")
                
                return {
                    "tipo": "sucesso",
                    "tipo_comando": "projeto",
                    "projeto": nome_projeto,
                    "diretorio_atual": caminho_projeto,
                    "resposta": f"✅ Projeto {nome_projeto} configurado em {caminho_projeto}"
                }
            
            # Comandos de branch
            elif comando == "/branch":
                if len(partes) < 2:
                    return {
                        "tipo": "erro",
                        "resposta": "❌ Por favor, especifique o nome da branch"
                    }
                
                return {
                    "tipo": "sucesso",
                    "tipo_comando": "branch",
                    "branch": partes[1],
                    "resposta": f"✅ Branch alterada para {partes[1]}"
                }
            
            # Comandos de diretório
            elif comando == "/cd":
                if len(partes) < 2:
                    return {
                        "tipo": "erro",
                        "resposta": "❌ Por favor, especifique o diretório"
                    }
                
                novo_dir = " ".join(partes[1:])
                return {
                    "tipo": "sucesso",
                    "tipo_comando": "diretorio",
                    "diretorio": novo_dir,
                    "resposta": f"✅ Diretório alterado para {novo_dir}"
                }
            
            # Comandos de arquivo
            elif comando == "/touch" or comando == "/mkdir":
                if len(partes) < 2:
                    return {
                        "tipo": "erro",
                        "resposta": "❌ Por favor, especifique o nome do arquivo/diretório"
                    }
                
                return {
                    "tipo": "sucesso",
                    "tipo_comando": "arquivo",
                    "operacao": "criar",
                    "tipo_arquivo": "arquivo" if comando == "/touch" else "diretorio",
                    "nome": partes[1],
                    "resposta": f"✅ {'Arquivo' if comando == '/touch' else 'Diretório'} {partes[1]} criado"
                }
            
            else:
                return {
                    "tipo": "erro",
                    "resposta": f"❌ Comando {comando} não reconhecido"
                }
            
        except Exception as e:
            logger.error(f"Erro ao analisar comando: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Erro ao analisar comando: {str(e)}"
            }
