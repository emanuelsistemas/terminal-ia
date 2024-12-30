#!/bin/bash

# Define o diretório do projeto
PROJECT_DIR=/root/projetos/chat-ia-terminal

# Verifica se o diretório existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Erro: Diretório do projeto não encontrado: $PROJECT_DIR"
    exit 1
fi

# Ativa o ambiente virtual do projeto
source "$PROJECT_DIR/venv/bin/activate" > /dev/null 2>&1

# Muda para o diretório do projeto e executa
cd "$PROJECT_DIR" && \
PYTHONWARNINGS=ignore pip install -r requirements.txt > /dev/null 2>&1 && \
PYTHONWARNINGS=ignore python3 run.py "$@"
