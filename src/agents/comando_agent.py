from typing import Dict
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class ComandoAgent:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def is_comando(self, mensagem: str) -> bool:
        """Verifica se a mensagem é um comando"""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": """Você é um analisador de comandos Linux.
                    
                    Sua função é identificar se uma mensagem contém um pedido para:
                    1. Criar um arquivo
                    2. Criar um diretório
                    
                    Responda apenas com "sim" ou "não".
                    
                    Exemplos:
                    "cria um arquivo teste.txt" -> sim
                    "faz uma pasta projetos" -> sim
                    "que horas são?" -> não
                    "como vai?" -> não
                    """
                }, {
                    "role": "user",
                    "content": mensagem
                }],
                temperature=0
            )
            
            resposta = response.choices[0].message.content.lower().strip()
            return resposta == "sim"
            
        except Exception as e:
            logger.error(f"Erro ao verificar comando: {e}")
            return False
    
    async def analisar_comando(self, mensagem: str) -> Dict:
        """Analisa um comando e retorna suas informações"""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": """Você é um analisador de comandos Linux.
                    
                    Sua função é extrair informações de comandos para:
                    1. Criar arquivos
                    2. Criar diretórios
                    
                    Para arquivos, extraia:
                    - nome do arquivo
                    - caminho (opcional)
                    - conteúdo (opcional)
                    
                    Para diretórios, extraia:
                    - nome do diretório
                    - caminho (opcional)
                    
                    Retorne um JSON no formato:
                    
                    Para arquivos:
                    {
                        "sucesso": true,
                        "tipo": "criar_arquivo",
                        "info": {
                            "nome": "nome.txt",
                            "caminho": "pasta/subpasta",
                            "conteudo": "texto do arquivo"
                        }
                    }
                    
                    Para diretórios:
                    {
                        "sucesso": true,
                        "tipo": "criar_diretorio",
                        "info": {
                            "nome": "pasta",
                            "caminho": "caminho/opcional"
                        }
                    }
                    
                    Se não for possível identificar, retorne:
                    {
                        "sucesso": false,
                        "erro": "mensagem de erro"
                    }
                    """
                }, {
                    "role": "user",
                    "content": mensagem
                }],
                temperature=0
            )
            
            # Converte a resposta para dict
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Erro ao analisar comando: {e}")
            return {
                "sucesso": False,
                "erro": "Não consegui entender o comando"
            }
