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
                ids=[f"{chat_id}_{datetime.now().timestamp()}"],
            )
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {e}")
    
    def get_context(self, chat_id: int, query: str) -> Dict:
        """Obtém o contexto relevante para uma query"""
        try:
            # Primeiro tenta encontrar nas mensagens recentes
            if chat_id in self.message_cache and self.message_cache[chat_id]:
                return {
                    "found": True,
                    "source": "short_term",
                    "context": self.message_cache[chat_id]
                }
            
            # Se não encontrou no cache, busca no ChromaDB
            results = self.collection.query(
                query_texts=[query],
                where={"chat_id": str(chat_id)},
                n_results=5
            )
            
            if results and results["documents"][0]:
                context = [json.loads(doc) for doc in results["documents"][0]]
                return {
                    "found": True,
                    "source": "long_term",
                    "context": context
                }
            
            return {
                "found": False,
                "source": None,
                "context": []
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar contexto: {e}")
            return {
                "found": False,
                "source": None,
                "context": []
            }
