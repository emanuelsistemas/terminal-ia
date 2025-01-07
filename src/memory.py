from typing import List, Dict, Optional
from datetime import datetime
import logging
import json
from pathlib import Path
import chromadb

logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, data_dir: str = "/root/projetos/chat-ia-terminal/data"):
        # Configuração dos diretórios
        self.data_dir = Path(data_dir)
        self.chroma_dir = self.data_dir / "chroma_db"
        
        # Cria diretórios se não existirem
        self.data_dir.mkdir(exist_ok=True)
        self.chroma_dir.mkdir(exist_ok=True)
        
        # Inicializa ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.collection = self.client.get_or_create_collection("chat_memory")
        
        # Cache das últimas 10 mensagens por chat
        self.message_cache: Dict[int, List[Dict]] = {}
        
        logger.info("Sistema de memória inicializado")
    
    def add_interaction(self, chat_id: int, user_message: str, bot_response: str) -> None:
        """Adiciona uma interação completa (mensagem do usuário e resposta do bot) à memória"""
        # Adiciona mensagem do usuário
        self.add_message(chat_id, "user", user_message)
        # Adiciona resposta do bot
        self.add_message(chat_id, "assistant", bot_response)
    
    def add_message(self, chat_id: int, role: str, content: str) -> None:
        """Adiciona uma mensagem à memória"""
        try:
            # Prepara a mensagem
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Adiciona ao cache de mensagens recentes
            if chat_id not in self.message_cache:
                self.message_cache[chat_id] = []
            
            self.message_cache[chat_id].append(message)
            
            # Mantém apenas as últimas 10 mensagens no cache
            if len(self.message_cache[chat_id]) > 10:
                self.message_cache[chat_id].pop(0)
            
            # Salva no ChromaDB
            self.collection.add(
                documents=[json.dumps(message)],
                metadatas=[{"chat_id": str(chat_id)}],
                ids=[f"{chat_id}_{datetime.now().timestamp()}"])
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem à memória: {e}")
    
    def get_context(self, chat_id: int, current_message: str) -> List[Dict]:
        """Retorna o contexto relevante para uma mensagem"""
        try:
            # Primeiro, pega as últimas mensagens do cache
            context = []
            if chat_id in self.message_cache:
                context.extend([
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in self.message_cache[chat_id][-5:]
                ])
            
            return context
            
        except Exception as e:
            logger.error(f"Erro ao buscar contexto: {e}")
            return []
