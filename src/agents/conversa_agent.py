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
            # Prepara as mensagens com o contexto
            messages = [{
                "role": "system",
                "content": """Você é o Nexus, um assistente especializado em Linux e desenvolvimento.
                    
                    IMPORTANTE: 
                    - Sempre responda em português do Brasil
                    - NUNCA invente ou assuma contextos que não foram fornecidos
                    - Se não tiver contexto anterior, apenas responda a pergunta atual
                    - Se perguntarem sobre conversas anteriores e não tiver contexto, diga que não tem essa informação
                    
                    Diretrizes:
                    - Seja direto e natural nas respostas
                    - Mantenha um tom profissional mas acessível
                    - Sugira soluções práticas quando relevante
                    - Use português claro e simples
                    """
            }]
            
            # Adiciona contexto se disponível
            if contexto and contexto.get("found", False):
                # Adiciona mensagem sobre a fonte do contexto
                if contexto["source"] == "short_term":
                    messages.append({
                        "role": "system",
                        "content": "As informações a seguir vêm da nossa conversa atual."
                    })
                elif contexto["source"] == "long_term":
                    messages.append({
                        "role": "system",
                        "content": "As informações a seguir vêm de conversas anteriores armazenadas na memória."
                    })
                
                # Adiciona o contexto encontrado
                for msg in contexto["context"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Adiciona a mensagem atual
            messages.append({
                "role": "user",
                "content": mensagem
            })
            
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
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
