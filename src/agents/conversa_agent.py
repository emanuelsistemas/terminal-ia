from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ConversaAgent:
    def __init__(self, client):
        self.client = client
        self.projeto_atual = None
    
    async def processar_mensagem(self, mensagem: str, contexto: Optional[List[Dict]] = None) -> Dict:
        """Processa uma mensagem e retorna uma resposta"""
        try:
            # Prepara o contexto base
            if not contexto:
                contexto = []
            
            # Adiciona o prompt do sistema
            contexto = [
                {
                    "role": "system",
                    "content": """Você é um assistente especializado em desenvolvimento web com React e TypeScript.
                    Você ajuda a criar e organizar projetos, sempre sugerindo as melhores práticas.
                    Use emojis para tornar as mensagens mais amigáveis.
                    Seja direto e objetivo nas respostas.
                    Quando precisar criar arquivos ou estruturas, use os comandos disponíveis.
                    Sempre mantenha o contexto do projeto atual."""
                }
            ] + contexto
            
            # Adiciona a mensagem do usuário
            contexto.append({"role": "user", "content": mensagem})
            
            # Gera a resposta usando o modelo
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=contexto,
                temperature=0.7,
                max_tokens=2000
            )
            
            resposta = completion.choices[0].message.content
            
            return {
                "tipo": "sucesso",
                "resposta": resposta
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Desculpe, ocorreu um erro ao processar sua mensagem. Detalhes: {str(e)}"
            }
