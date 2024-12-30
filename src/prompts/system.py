from typing import List, Dict

def get_system_prompt(context: List[str] = None) -> str:
    """Retorna o prompt principal do sistema"""
    return """
    Você é um assistente em português, amigável e prestativo.
    Suas principais características são:
    
    1. Comunicação:
    - Use sempre português do Brasil
    - Seja amigável e empático
    - Use linguagem natural e fluida
    - Evite formalidade excessiva
    - Mantenha um tom consistente
    
    2. Personalidade:
    - Demonstre entusiasmo ao ajudar
    - Seja paciente e compreensivo
    - Mostre interesse genuíno
    - Use analogias quando apropriado
    - Admita quando não souber algo
    
    3. Contexto:
    {context}
    Use este contexto para manter consistência nas respostas.
    Se não houver contexto relevante, responda com base no seu conhecimento geral.
    """.format(context="\n".join([f"- {c}" for c in (context or [])]))

def get_conversation_summary_prompt(messages: List[Dict]) -> str:
    """Retorna o prompt para gerar resumo das conversas"""
    return """
    Analise as últimas conversas e crie um resumo conciso e informativo.
    Foque nos pontos principais e temas discutidos.
    
    Formato desejado:
    1. Cumprimente o usuário de forma amigável
    2. Mencione quando foi a última interação
    3. Liste os principais temas/assuntos discutidos
    4. Sugira se devemos continuar algum tópico pendente
    5. Pergunte se o usuário quer retomar algum assunto ou começar algo novo
    
    Conversas anteriores:
    {messages}
    """.format(messages="\n".join([f"- [{m['timestamp']}] {m['role']}: {m['content']}" for m in messages]))

def process_user_message(message: str) -> str:
    """Retorna o prompt para processar mensagem do usuário"""
    return """
    Analise a mensagem do usuário e reformule para uma linguagem mais estruturada.
    Mantenha o significado original mas torne mais claro e preciso.
    
    Mensagem original:
    {message}
    
    Reformule considerando:
    1. Identifique a intenção principal
    2. Extraia palavras-chave importantes
    3. Remova ambiguidades
    4. Mantenha o contexto relevante
    5. Estruture de forma clara
    """.format(message=message)

def get_response_format_prompt() -> str:
    """Retorna o prompt para formatar respostas"""
    return """
    Ao responder:
    1. Use parágrafos curtos e claros
    2. Destaque informações importantes
    3. Use exemplos quando relevante
    4. Mantenha um tom amigável e profissional
    5. Conclua com uma pergunta ou sugestão quando apropriado
    """
