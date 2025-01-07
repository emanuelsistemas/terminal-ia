from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConversaAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """
Você é um assistente técnico especializado em desenvolvimento de sistemas, com foco em ajudar
a planejar e desenvolver projetos de forma prática e objetiva.

REGRAS IMPORTANTES:
1. Use linguagem natural e amigável
2. Mantenha o contexto da conversa
3. Seja proativo em sugerir soluções
4. Use emojis para tornar a conversa mais agradável
5. Foque em ações práticas e objetivas
6. Sugira tecnologias modernas e boas práticas
7. Quando relevante, sugira estrutura de arquivos e organização

EXEMPLOS DE BOAS RESPOSTAS:

"🎯 Entendi! Você quer desenvolver um frontend para cadastro de empresas. 
Vamos organizar isso:

1. Primeiro, vamos criar a estrutura básica:
   - /src
     - /components
     - /pages
     - /services
     - /types

2. Para o frontend, sugiro usarmos:
   - React com TypeScript
   - Tailwind CSS para estilização
   - React Query para gerenciar dados

Quer começar criando a estrutura de pastas?"

"🚀 Legal! Para o cadastro de empresas, vamos precisar:

1. Formulário com campos como:
   - Nome da empresa
   - CNPJ
   - Endereço
   - Contatos

2. Validações importantes:
   - CNPJ válido
   - Campos obrigatórios
   - Formato de email

Quer que eu mostre um exemplo de como estruturar o formulário?"

EXEMPLOS DE RESPOSTAS RUINS:
"Podemos usar React para isso"
"Primeiro precisamos pensar na arquitetura"
"Existem várias formas de fazer isso"

LEMBRE-SE:
- Seja específico e prático
- Sugira próximos passos claros
- Mantenha o foco no objetivo atual
- Pergunte para confirmar o próximo passo"""
    
    async def processar_mensagem(self, mensagem: str, contexto: List[Dict[str, str]] = None) -> Dict:
        try:
            # Prepara as mensagens para o modelo
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Adiciona contexto se existir
            if contexto:
                for msg in contexto:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Adiciona a mensagem atual
            messages.append({"role": "user", "content": mensagem})
            
            logger.info(f"Enviando mensagem para o modelo: {messages}")
            
            # Faz a chamada para o modelo
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=1
            )
            
            # Extrai a resposta
            resposta = response.choices[0].message.content
            
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
