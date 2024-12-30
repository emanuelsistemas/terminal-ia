import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .logger import setup_logger
from .config import DATA_DIR

logger = setup_logger(__name__)

class Database:
    def __init__(self, max_checkpoints: int = 10):
        self.messages_file = DATA_DIR / "messages.json"
        self.checkpoints_dir = DATA_DIR / "checkpoints"
        self.messages: List[Dict] = []
        self.max_checkpoints = max_checkpoints
        logger.info("Database inicializado com sucesso")

    async def initialize(self):
        try:
            # Criar diretórios se não existirem
            self.messages_file.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
            
            # Carregar mensagens do arquivo se existir
            if self.messages_file.exists():
                with open(self.messages_file, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)
                logger.info(f"Carregadas {len(self.messages)} mensagens do arquivo")
            else:
                self.messages = []
                logger.info("Arquivo de mensagens não encontrado, iniciando vazio")
            
            # Limpar checkpoints antigos na inicialização
            await self.cleanup_old_checkpoints()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar database: {str(e)}")
            raise

    async def cleanup_old_checkpoints(self):
        """Remove os checkpoints mais antigos mantendo apenas max_checkpoints"""
        try:
            checkpoints = list(self.checkpoints_dir.glob("*.json"))
            if len(checkpoints) > self.max_checkpoints:
                # Ordena por data de modificação, mais antigos primeiro
                checkpoints.sort(key=lambda x: x.stat().st_mtime)
                
                # Remove os mais antigos
                for checkpoint in checkpoints[:-self.max_checkpoints]:
                    checkpoint.unlink()
                    logger.info(f"Checkpoint removido: {checkpoint.name}")
        except Exception as e:
            logger.error(f"Erro ao limpar checkpoints antigos: {str(e)}")

    async def save_messages(self, messages: List[Dict]):
        try:
            # Adicionar ID e timestamp se não existirem
            for msg in messages:
                if "id" not in msg:
                    msg["id"] = str(uuid.uuid4())
                if "timestamp" not in msg:
                    msg["timestamp"] = datetime.now().isoformat()
            
            # Atualizar mensagens em memória
            self.messages = messages
            
            # Salvar no arquivo principal
            with open(self.messages_file, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # Criar checkpoint apenas para mensagens da IA
            if messages and messages[-1]["role"] == "assistant":
                checkpoint_file = self.checkpoints_dir / f"{messages[-1]['id']}.json"
                with open(checkpoint_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
                logger.info(f"Checkpoint criado: {messages[-1]['id']}")
                
                # Limpa checkpoints antigos após criar um novo
                await self.cleanup_old_checkpoints()
            
            logger.info(f"Salvas {len(messages)} mensagens no arquivo")
        except Exception as e:
            logger.error(f"Erro ao salvar mensagens: {str(e)}")
            raise

    async def restore_checkpoint(self, message_id: str) -> Optional[List[Dict]]:
        try:
            checkpoint_file = self.checkpoints_dir / f"{message_id}.json"
            if not checkpoint_file.exists():
                logger.error(f"Checkpoint não encontrado: {message_id}")
                return None
            
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
            
            logger.info(f"Checkpoint restaurado: {message_id}")
            return messages
        except Exception as e:
            logger.error(f"Erro ao restaurar checkpoint: {str(e)}")
            return None

    async def list_checkpoints(self) -> List[Dict]:
        try:
            checkpoints = []
            for file in sorted(self.checkpoints_dir.glob("*.json"), 
                             key=lambda x: x.stat().st_mtime, 
                             reverse=True):
                with open(file, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                    last_message = messages[-1]
                    checkpoints.append({
                        "id": last_message["id"],
                        "timestamp": last_message["timestamp"],
                        "content": last_message["content"][:100] + "..." if len(last_message["content"]) > 100 else last_message["content"]
                    })
            return checkpoints
        except Exception as e:
            logger.error(f"Erro ao listar checkpoints: {str(e)}")
            return []

    async def close(self):
        try:
            logger.info("Database fechado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar database: {str(e)}")
            raise
