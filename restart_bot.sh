#!/bin/bash

# Mata qualquer instância anterior do bot
pkill -f "python3 main.py"

# Aguarda 2 segundos
sleep 2

# Inicia o bot em background
nohup python3 main.py > bot.log 2>&1 &

# Aguarda 2 segundos
sleep 2

# Mostra as últimas 10 linhas do log
tail -n 10 bot.log
