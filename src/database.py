import json
from pathlib import Path
from typing import List, Dict
from .logger import setup_logger
from .config import DATA_DIR

logger = setup_logger(__name__)

class Database:
    def __init__(self):
        self.messages_file = DATA_DIR / "messages.json"
        self.messages: List[Dict] = []
        logger.info("Database inicializado com sucesso")

    async def initialize(self):
        try:
            # Criar diretório se não existir
            self.messages_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Carregar mensagens do arquivo se existir
            if self.messages_file.exists():
                with open(self.messages_file, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)
                logger.info(f"Carregadas {len(self.messages)} mensagens do arquivo")
            else:
                self.messages = []
                logger.info("Arquivo de mensagens não encontrado, iniciando vazio")
        except Exception as e:
            logger.error(f"Erro ao inicializar database: {str(e)}")
            raise

    async def save_messages(self, messages: List[Dict]):
        try:
            # Atualizar mensagens em memória
            self.messages = messages
            
            # Salvar no arquivo
            with open(self.messages_file, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Salvas {len(messages)} mensagens no arquivo")
        except Exception as e:
            logger.error(f"Erro ao salvar mensagens: {str(e)}")
            raise

    async def close(self):
        try:
            # Por enquanto não há nada especial para fazer aqui
            # mas mantemos o método para consistência e possíveis
            # futuras implementações
            logger.info("Database fechado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar database: {str(e)}")
            raise
