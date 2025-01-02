# Chat IA Terminal

Um assistente de IA via linha de comando com suporte a múltiplos provedores.

## Funcionalidades

### 1. Interface do Usuário (Terminal)
- Interface de linha de comando interativa
- Menu de seleção de provedor (Groq ou Deepseek)
- Animação de loading durante processamento
- Suporte a cores no terminal
- Formatação de texto unicode

### 2. Provedores de IA
- Suporte ao Groq (modelo mixtral-8x7b-32768)
- Suporte ao Deepseek (modelo deepseek-chat)
- Sistema flexível para adicionar novos provedores

### 3. Gerenciamento de Mensagens
- Histórico persistente de conversas
- Armazenamento em formato JSON
- Sistema de IDs únicos para mensagens
- Timestamps em todas as mensagens
- Limite de contexto (últimas 10 mensagens)

### 4. Comandos Especiais
- `sair`: Encerra o programa
- `limpar`: Limpa o histórico de mensagens
- Suporte a Ctrl+C para interrupção segura

### 5. Sistema de Logs
- Logs detalhados de operações
- Rotação automática de arquivos de log
- Visualizador de logs integrado
- Diferentes níveis de log (error, info, debug)

### 6. Gerenciamento de Configuração
- Carregamento de variáveis de ambiente (.env)
- Diretórios configuráveis para dados e logs
- Estrutura organizada de arquivos
- Configurações separadas por ambiente

### 7. Prompts do Sistema
- Sistema de prompts personalizáveis
- Suporte a contexto dinâmico
- Personalidade consistente do assistente
- Formatação de mensagens do usuário

### 8. Tratamento de Erros
- Tratamento robusto de exceções
- Mensagens de erro amigáveis
- Recuperação de falhas de conexão
- Validação de entrada do usuário

### 9. Armazenamento
- Sistema de banco de dados simples
- Armazenamento persistente de dados
- Backup automático de conversas
- Gerenciamento de arquivos

### 10. Recursos Avançados
- Suporte a múltiplos idiomas (foco em pt-BR)
- Sistema assíncrono para operações longas
- Formatação inteligente de respostas
- Medição de largura de strings unicode

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>

# Entre no diretório
cd chat-ia-terminal

# Instale o pacote
pip install -e .
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com suas chaves de API:

```env
GROQ_API_KEY=sua-chave-aqui
DEEPSEEK_API_KEY=sua-chave-aqui
```

## Uso

```bash
# Inicie o chat
chat-ia
```

## Estrutura do Projeto

```
src/
├── assistant.py    # Implementação principal do assistente
├── chat.py         # Gerenciamento de chat e mensagens
├── config.py       # Configurações do sistema
├── logger.py       # Sistema de logs
├── main.py         # Ponto de entrada do programa
├── prompts/        # Templates de prompts do sistema
└── terminal.py     # Utilitários do terminal
```

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
