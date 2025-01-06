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
        
        # Memória de curto prazo por chat
        self.short_term: Dict[int, List[Dict]] = {}
        
        logger.info("Sistema de memória inicializado")
    
    def add_message(self, chat_id: int, role: str, content: str) -> None:
        """Adiciona uma mensagem à memória de curto prazo"""
        if chat_id not in self.short_term:
            self.short_term[chat_id] = []
        
        # Adiciona à memória de curto prazo
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.short_term[chat_id].append(message)
        
        # Se exceder 10 mensagens, move as mais antigas para o ChromaDB
        if len(self.short_term[chat_id]) > 10:
            oldest = self.short_term[chat_id].pop(0)
            self._add_to_long_term(chat_id, oldest)
    
    def get_context(self, chat_id: int, query: str) -> List[Dict]:
        """Obtém o contexto relevante para uma query"""
        # Primeiro tenta na memória de curto prazo
        if chat_id in self.short_term:
            recent_context = self.short_term[chat_id]
            if self._is_relevant(query, recent_context):
                return recent_context
        
        # Se não encontrar ou não for relevante, busca na memória de longo prazo
        long_term = self._search_long_term(chat_id, query)
        if long_term:
            return long_term
        
        # Se não encontrar nada, retorna lista vazia
        return []
    
    def _is_relevant(self, query: str, context: List[Dict]) -> bool:
        """Verifica se o contexto recente é relevante para a query"""
        # Por enquanto retorna True para manter o contexto recente
        # Pode ser melhorado com análise de similaridade
        return True
    
    def _add_to_long_term(self, chat_id: int, message: Dict) -> None:
        """Adiciona uma mensagem à memória de longo prazo (ChromaDB)"""
        try:
            # Prepara metadados
            metadata = {
                "chat_id": str(chat_id),
                "role": message["role"],
                "timestamp": message["timestamp"]
            }
            
            # Adiciona ao ChromaDB
            self.collection.add(
                documents=[message["content"]],
                metadatas=[metadata],
                ids=[f"{chat_id}_{datetime.now().timestamp()}"]
            )
            
            logger.info(f"Mensagem adicionada à memória de longo prazo para chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar à memória de longo prazo: {e}")
    
    def _search_long_term(self, chat_id: int, query: str, n_results: int = 5) -> List[Dict]:
        """Busca mensagens relevantes na memória de longo prazo"""
        try:
            results = self.collection.query(
                query_texts=[query],
                where={"chat_id": str(chat_id)},
                n_results=n_results
            )
            
            # Formata resultados
            messages = []
            for i in range(len(results["documents"][0])):
                messages.append({
                    "role": results["metadatas"][0][i]["role"],
                    "content": results["documents"][0][i],
                    "timestamp": results["metadatas"][0][i]["timestamp"]
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao buscar na memória de longo prazo: {e}")
            return []
    
    def clear_chat(self, chat_id: int) -> None:
        """Limpa a memória de curto prazo de um chat"""
        if chat_id in self.short_term:
            del self.short_term[chat_id]
