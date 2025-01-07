from typing import Dict
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class ConversaAgent:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def processar_mensagem(self, mensagem: str, contexto: Dict = None) -> Dict:
        """Processa uma mensagem de conversa normal"""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": """Você é o Nexus, um assistente especializado em Linux e desenvolvimento.
                    
                    Importante:
                    - Seja direto e natural nas respostas
                    - Mantenha um tom profissional mas acessível
                    - Sugira soluções práticas quando relevante
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
