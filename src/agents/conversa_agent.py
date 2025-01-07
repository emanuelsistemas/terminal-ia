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
<<<<<<< HEAD
            # Prepara as mensagens com o contexto
            messages = [{
                "role": "system",
                "content": """Você é o Nexus, um assistente especializado em Linux e desenvolvimento.
                
                Importante:
                - Seja direto e natural nas respostas
                - Use o contexto disponível de forma inteligente
                - Quando usar informações da web, cite as fontes
                - Mantenha um tom profissional mas acessível
                - Sugira soluções práticas quando relevante
                
                Sobre o contexto:
                - Se vier da memória curta (short_term), use naturalmente
                - Se vier da memória longa (long_term), mencione "Lembro que falamos sobre isso antes..."
                - Se vier da web (web), cite "Segundo [fonte]..."
                """
            }]
            
            # Adiciona contexto se disponível
            if contexto and contexto.get("found", False):
                # Adiciona mensagem sobre a fonte do contexto
                if contexto["source"] == "long_term":
                    messages.append({
                        "role": "system",
                        "content": "As informações a seguir vêm de conversas anteriores armazenadas na memória."
                    })
                elif contexto["source"] == "web":
                    messages.append({
                        "role": "system",
                        "content": "As informações a seguir vêm de pesquisas web recentes. Cite as fontes."
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
            
            logger.info(f"Enviando mensagem para o modelo: {messages}")
            
=======
>>>>>>> 06bc870
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
<<<<<<< HEAD
    
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
=======
>>>>>>> 06bc870
