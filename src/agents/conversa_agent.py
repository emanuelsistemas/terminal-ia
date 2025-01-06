from typing import Dict, List
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class ConversaAgent:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def processar_mensagem(self, mensagem: str, contexto: List[Dict] = None) -> Dict:
        """Processa uma mensagem de conversa normal usando o contexto disponível"""
        try:
            # Prepara as mensagens com o contexto
            messages = [{
                "role": "system",
                "content": """Você é o Nexus, um especialista em Linux e desenvolvimento.
                
                Importante:
                - Seja proativo e sugira soluções práticas
                - Foque em ideias e exemplos concretos
                - Guie o usuário com perguntas específicas quando necessário
                - Sugira tecnologias e ferramentas relevantes
                - Use sua experiência para dar dicas práticas
                - Mantenha um tom direto e profissional
                
                Quando o usuário falar de projetos:
                1. Sugira estruturas e tecnologias específicas
                2. Dê exemplos de implementação
                3. Mencione ferramentas úteis
                4. Proponha próximos passos práticos
                
                Exemplos RUINS:
                "Existem vários sistemas ERP disponíveis..."
                "Recomendo avaliar diferentes opções..."
                
                Exemplos BONS:
                "Para um ERP fiscal, sugiro começarmos com:
                1. PostgreSQL para o banco
                2. FastAPI para a API
                3. React para o frontend
                Quer que eu mostre como estruturar?"
                
                "Vamos começar criando a estrutura base:
                1. Primeiro o banco de dados
                2. Depois os endpoints principais
                Por qual você quer começar?"
                """
            }]
            
            # Adiciona contexto se disponível
            if contexto:
                for msg in contexto:
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
