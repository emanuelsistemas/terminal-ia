# Agentes do NexusIA Bot

Este diretório contém os agentes especializados que compõem o NexusIA Bot.
Cada agente é responsável por uma funcionalidade específica e trabalha em conjunto através do OrquestradorAgent.

## Estrutura de Agentes

### AnalisadorAgent
- **Arquivo**: analisador_agent.py
- **Responsabilidade**: Análise de intenções das mensagens
- **Funcionamento**: Usa IA para classificar mensagens em diferentes tipos (comando_diretorio, conversa, etc)
- **Prompt Base**: Especializado em análise de contexto e classificação

### ConversaAgent
- **Arquivo**: conversa_agent.py
- **Responsabilidade**: Gerenciamento de conversas naturais
- **Funcionamento**: Mantém contexto da conversa e gera respostas naturais
- **Prompt Base**: Focado em diálogo natural e assistência

### DiretorioAgent
- **Arquivo**: diretorio_agent.py
- **Responsabilidade**: Operações com sistema de arquivos
- **Funcionamento**: Cria, lista e gerencia diretórios
- **Prompt Base**: Especializado em comandos Linux e operações de arquivo

### OrquestradorAgent
- **Arquivo**: orquestrador_agent.py
- **Responsabilidade**: Coordenação entre agentes
- **Funcionamento**: Roteia mensagens e coordena respostas
- **Características**: Ponto central de comunicação

## Como Adicionar Novo Agente

1. Crie um novo arquivo `nome_agent.py`
2. Implemente a classe do agente seguindo o padrão:
   ```python
   class NovoAgent:
       def __init__(self):
           self.system_prompt = "Prompt específico..."
       
       async def processar(self, dados):
           # Implementação
           pass
   ```
3. Adicione o agente ao OrquestradorAgent
4. Atualize esta documentação

## Fluxo de Comunicação

1. Telegram → OrquestradorAgent
2. OrquestradorAgent → AnalisadorAgent
3. AnalisadorAgent retorna intenção
4. OrquestradorAgent → Agente Específico
5. Agente Específico processa e retorna
6. OrquestradorAgent → Telegram
