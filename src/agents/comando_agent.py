from typing import Dict, Optional
import logging
import os
import shutil

logger = logging.getLogger(__name__)

class ComandoAgent:
    def __init__(self, client):
        self.client = client
        self.estado_comando = {}
    
    async def is_comando(self, mensagem: str) -> bool:
        """Verifica se a mensagem é um comando"""
        return mensagem.startswith("/") or self.estado_comando.get("aguardando_resposta")
    
    async def analisar_comando(self, mensagem: str) -> Dict:
        """Analisa um comando e retorna informações sobre ele"""
        try:
            # Se estamos aguardando uma resposta para um comando em andamento
            if self.estado_comando.get("aguardando_resposta"):
                comando_atual = self.estado_comando["comando"]
                
                if comando_atual == "/projeto":
                    if self.estado_comando.get("aguardando") == "nome":
                        # Recebemos o nome do projeto
                        self.estado_comando["nome_projeto"] = mensagem
                        self.estado_comando["aguardando"] = "caminho"
                        
                        return {
                            "tipo": "pergunta",
                            "resposta": "📂 Qual será o caminho da pasta principal do projeto? (Ex: /root/projetos)"
                        }
                        
                    elif self.estado_comando.get("aguardando") == "caminho":
                        # Recebemos o caminho do projeto
                        caminho = mensagem
                        nome_projeto = self.estado_comando["nome_projeto"]
                        
                        # Limpa o estado
                        self.estado_comando = {}
                        
                        # Retorna as informações para criar o projeto
                        return {
                            "tipo": "sucesso",
                            "tipo_comando": "projeto",
                            "projeto": nome_projeto,
                            "caminho_base": caminho,
                            "diretorio_atual": os.path.join(caminho, nome_projeto),
                            "resposta": f"✅ Criando projeto {nome_projeto} em {caminho}..."
                        }
            
            # Se é um novo comando
            partes = mensagem.split()
            comando = partes[0].lower()
            
            # Comandos de projeto
            if comando == "/projeto":
                # Inicia o processo de criação do projeto
                self.estado_comando = {
                    "comando": "/projeto",
                    "aguardando_resposta": True,
                    "aguardando": "nome"
                }
                
                return {
                    "tipo": "pergunta",
                    "resposta": "🚀 Legal! Vamos criar um novo projeto. Qual será o nome dele?"
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
            
            # Se não é um comando conhecido, processa como conversa normal
            return {
                "tipo": "conversa",
                "resposta": mensagem
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar comando: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Erro ao analisar comando: {str(e)}"
            }
