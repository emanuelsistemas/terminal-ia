from typing import List, Dict

def get_system_prompt(context: List[str] = None) -> str:
    """Retorna o prompt principal do sistema"""
    return """
    Você é um assistente avançado em português, com capacidade de pesquisa e análise.
    Suas principais características são:
    
    1. Processo de Resposta:
    - Analise cuidadosamente cada pergunta
    - Identifique se precisa de informações adicionais
    - Use fontes apropriadas de conhecimento
    - Organize a resposta de forma estruturada
    - Cite fontes quando usar informações externas
    
    2. Fontes de Informação:
    - Conhecimento base: Use para conceitos gerais e fundamentais
    - Conhecimento local: Informações específicas e contextuais
    - Pesquisa web: Informações atualizadas e específicas
    - Análise de código: Para questões técnicas e implementação
    
    3. Comunicação:
    - Use sempre português do Brasil
    - Seja preciso e objetivo
    - Explique seu processo de pensamento
    - Admita quando precisar buscar mais informações
    - Mantenha um tom profissional mas acessível
    
    4. Contexto Atual:
    {context}
    Use este contexto para manter consistência nas respostas.
    
    5. Processo de Decisão:
    - Avalie a confiança na resposta
    - Indique quando houver incerteza
    - Sugira buscar mais informações quando necessário
    - Mantenha transparência sobre suas fontes
    """.format(context="\n".join([f"- {c}" for c in (context or [])]))

def get_research_prompt(query: str, context: Dict) -> str:
    """Retorna o prompt para pesquisa de informações"""
    return """
    Analise a seguinte consulta e as informações disponíveis:
    
    Consulta: {query}
    
    Fontes Disponíveis:
    1. Conhecimento Local:
    {local_knowledge}
    
    2. Resultados Web:
    {web_results}
    
    3. Análise de Código:
    {code_analysis}
    
    4. Análise de Contexto:
    {context_analysis}
    
    Por favor, forneça uma resposta que:
    1. Integre as informações relevantes das diferentes fontes
    2. Priorize fontes mais confiáveis e atualizadas
    3. Indique claramente a origem das informações
    4. Sugira buscar mais informações se necessário
    """.format(
        query=query,
        local_knowledge="\n".join(context.get("local_knowledge", [])),
        web_results="\n".join([f"- {r['title']}: {r['snippet']}" for r in context.get("web_results", [])]),
        code_analysis="\n".join(context.get("code_analysis", [])),
        context_analysis=str(context.get("analysis", {}))
    )

def get_conversation_summary_prompt(messages: List[Dict]) -> str:
    """Retorna o prompt para gerar resumo das conversas"""
    return """
    Analise as últimas conversas e crie um resumo conciso e informativo.
    Foque nos pontos principais e temas discutidos.
    
    Formato desejado:
    1. Tópicos principais discutidos
    2. Fontes de informação utilizadas
    3. Decisões e conclusões alcançadas
    4. Pontos que precisam de mais pesquisa
    5. Sugestões para próximos passos
    
    Conversas anteriores:
    {messages}
    """.format(messages="\n".join([f"- [{m['timestamp']}] {m['role']}: {m['content']}" for m in messages]))

def process_user_message(message: str) -> str:
    """Retorna o prompt para processar mensagem do usuário"""
    return """
    Analise a mensagem do usuário e determine:
    
    1. Intenção principal
    2. Tópicos relacionados
    3. Necessidade de informações adicionais
    4. Nível de confiança necessário na resposta
    5. Fontes de informação apropriadas
    
    Mensagem: {message}
    """.format(message=message)
