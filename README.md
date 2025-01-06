# Chat IA Terminal

Bot do Telegram que usa múltiplas LLMs (Groq e DeepSeek) para interpretar comandos em linguagem natural.

## Gerenciando o Bot

Use o script `manage_bot.py` para gerenciar o bot:

```bash
# Iniciar o bot
./manage_bot.py start

# Parar o bot
./manage_bot.py stop

# Reiniciar o bot
./manage_bot.py restart

# Ver status do bot
./manage_bot.py status

# Ver logs
./manage_bot.py logs              # Últimas 20 linhas
./manage_bot.py logs -n 50        # Últimas 50 linhas
./manage_bot.py logs -f           # Monitora em tempo real
./manage_bot.py logs -e           # Mostra apenas erros
```

## Comandos do Bot

- `/provider` - Mostra os providers disponíveis
- `/provider groq` - Muda para o provider Groq
- `/provider deepseek` - Muda para o provider DeepSeek

## Exemplos de Uso

Você pode usar linguagem natural para criar pastas. Exemplos:

- "crie uma pasta src em /root/projetos/chatfood"
- "preciso de um diretório chamado config dentro de /root/projetos/app"
- "faça uma pasta chamada docs no /var/www/html"

O bot usará IA para interpretar seu comando e executar a ação apropriada.
