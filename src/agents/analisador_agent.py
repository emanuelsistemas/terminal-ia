from typing import Dict
import logging
from openai import OpenAI
import json

logger = logging.getLogger(__name__)

class AnalisadorAgent:
    def __init__(self, client: OpenAI):
        self.client = client
        self.models = {
            "mixtral": "mixtral-8x7b-32768",
            "gpt4": "gpt-4",
            "deepseek": "deepseek-coder"
        }
    
    async def analisar_mensagem(self, mensagem: str, modelo: str = "mixtral") -> Dict:
        """Analisa a mensagem para determinar o tipo e extrair informações relevantes"""
        try:
            # Log do modelo usado
            logger.info(f"Analisando mensagem usando modelo: {modelo}")
            
            # Prompt para análise da mensagem
            prompt = f"""Analise a mensagem do usuário e extraia as informações relevantes.
            
            Mensagem: {mensagem}
            
            Retorne um JSON com:
            - tipo: 'comando_arquivo', 'comando_diretorio' ou 'conversa'
            - detalhes: para comandos, extraia nome do arquivo/diretório e conteúdo se houver
            - raciocinio: explique como você chegou a essa conclusão
            
            Exemplos:
            "crie uma pasta teste" -> {{
                "tipo": "comando_diretorio",
                "detalhes": {{"nome": "teste"}},
                "raciocinio": "Identificado comando de criar diretório pela presença de 'pasta' e um nome claro 'teste'"
            }}
            
            "crie um arquivo teste.txt" -> {{
                "tipo": "comando_arquivo",
                "detalhes": {{"nome": "teste.txt", "conteudo": ""}},
                "raciocinio": "Identificado comando de criar arquivo pela palavra 'arquivo' e extensão .txt"
            }}
            
            "como faço para..." -> {{
                "tipo": "conversa",
                "raciocinio": "Identificado como pergunta de conversação por começar com 'como faço'"
            }}
            
            Regras:
            1. Ignore palavras como 'crie', 'uma', 'pasta', etc
            2. Para arquivos, mantenha a extensão .txt se especificada
            3. Extraia apenas o nome essencial, sem palavras extras
            4. Preserve exatamente o que está entre aspas se houver
            5. Trate quebras de linha e espaços extras
            """
            
            # Faz a chamada para o modelo
            response = self.client.chat.completions.create(
                model=self.models.get(modelo, "mixtral-8x7b-32768"),
                messages=[{
                    "role": "system",
                    "content": "Você é um analisador de comandos especializado em operações de arquivo e diretório."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            # Extrai a resposta
            resultado = json.loads(response.choices[0].message.content)
            
            # Log do raciocínio
            if resultado.get("raciocinio"):
                logger.info(f"Raciocínio do modelo: {resultado['raciocinio']}")
            
            # Valida o resultado
            if not resultado.get("tipo") or resultado["tipo"] not in ["comando_arquivo", "comando_diretorio", "conversa"]:
                return {"sucesso": False, "mensagem": "Tipo de comando inválido"}
            
            # Para comandos, valida os detalhes
            if resultado["tipo"].startswith("comando_"):
                detalhes = resultado.get("detalhes", {})
                if not detalhes.get("nome"):
                    return {"sucesso": False, "mensagem": "Nome não encontrado no comando"}
            
            return {"sucesso": True, **resultado}
            
        except Exception as e:
            logger.error(f"Erro ao analisar mensagem: {e}")
            return {"sucesso": False, "mensagem": str(e)}
