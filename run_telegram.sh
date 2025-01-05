#!/bin/bash

# Função para iniciar o bot
start_bot() {
    echo "Iniciando o bot..."
    python3 run_telegram.py >> telegram.log 2>&1
}

# Mata qualquer instância anterior do bot
pkill -f run_telegram.py

# Inicia o bot
start_bot &

# Guarda o PID do bot
echo $! > bot.pid

echo "Bot iniciado com PID $(cat bot.pid)"
