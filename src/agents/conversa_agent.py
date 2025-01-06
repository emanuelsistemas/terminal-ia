from typing import Dict
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class ConversaAgent:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def processar_mensagem(self, mensagem: str) -> Dict:
        """Processa uma mensagem de conversa normal"""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": """Você é o Nexus, alguém que entende muito de Linux.
                    
                    Importante:
                    - Seja direto e natural
                    - Respostas curtas e objetivas
                    - Nada de exageros ou forçar informalidade
                    - Sem emoji, sem muitas exclamações
                    - Fale em português simples
                    - Não tente parecer amigável demais
                    
                    Exemplos RUINS (não faça assim):
                    "Oiii! Tudo bem com você, amigo? Estou super empolgado em ajudar!!!"
                    "Nossa, que legal você ter perguntado isso! Vamos trocar ideias?"
                    
                    Exemplos BONS:
                    "Oi, tudo bem?"
                    "Diz aí, o que precisa?"
                    "Beleza, vamo resolver isso"
                    """
                }, {
                    "role": "user",
                    "content": mensagem
                }],
                temperature=0.7
            )
            
            return {
                "sucesso": True,
                "resposta": response.choices[0].message.content,
                "modelo": "mixtral-8x7b-32768"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "sucesso": False,
                "resposta": "Deu um erro aqui. Tenta de novo?",
                "modelo": "mixtral-8x7b-32768"
            }
    
    async def formatar_resposta(self, resultado: Dict, tipo_comando: str) -> str:
        """Formata o resultado de uma operação usando LLM"""
        try:
            # Prepara o contexto baseado no tipo de comando
            if tipo_comando == "comando_arquivo":
                contexto = (
                    f"Arquivo criado:\n"
                    f"Nome: {resultado['info']['nome']}\n"
                    f"Caminho: {resultado['info']['caminho_completo']}"
                )
            elif tipo_comando == "comando_diretorio":
                contexto = (
                    f"Pasta criada:\n"
                    f"Nome: {resultado['info']['nome']}\n"
                    f"Caminho: {resultado['info']['caminho_completo']}"
                )
            else:
                return None
            
            prompt = (
                "Explique de forma simples e direta o que foi feito.\n\n"
                f"{contexto}\n\n"
                "Regras:\n"
                "- Seja breve e direto\n"
                "- Nada de exageros\n"
                "- Sem emoji\n"
                "- Português simples\n"
                "- Mencione o caminho"
            )
            
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": """Você está explicando algo no Linux.
                    
                    Importante:
                    - Seja direto e breve
                    - Sem exageros ou forçar informalidade
                    - Sem emoji ou exclamações
                    - Português simples
                    
                    Exemplo RUIM:
                    "Uhuul! Arquivo criado com sucesso! Está tudo prontinho! 😊"
                    
                    Exemplo BOM:
                    "Criei o arquivo em /pasta/arquivo.txt"
                    """
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao formatar resposta: {e}")
            return None
