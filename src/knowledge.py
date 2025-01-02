from typing import List, Dict, Optional
from pathlib import Path
import json
import chromadb
from datetime import datetime

class KnowledgeBase:
    def __init__(self, data_dir: str = "/root/projetos/chat-ia-terminal/data"):
        self.data_dir = Path(data_dir)
        self.chroma_dir = self.data_dir / "chroma_db"
        self.checkpoints_dir = self.data_dir / "checkpoints"
        self.system_backups_dir = self.data_dir / "system_backups"
        
        # Inicializa diretórios
        self.data_dir.mkdir(exist_ok=True)
        self.chroma_dir.mkdir(exist_ok=True)
        self.checkpoints_dir.mkdir(exist_ok=True)
        self.system_backups_dir.mkdir(exist_ok=True)
        
        # Inicializa ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.collection = self.client.get_or_create_collection("knowledge")
    
    def add_knowledge(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Adiciona novo conhecimento à base"""
        if metadata is None:
            metadata = {}
        
        # Adiciona timestamp
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Adiciona ao ChromaDB
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[metadata.get("id", str(datetime.now().timestamp()))]
        )
        
        return "Conhecimento adicionado com sucesso"
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict]:
        """Busca conhecimento similar à query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Formata resultados
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted_results
    
    def save_checkpoint(self, chat_state: Dict) -> str:
        """Salva um checkpoint do estado atual do chat"""
        checkpoint_id = str(datetime.now().timestamp())
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(chat_state, f, ensure_ascii=False, indent=2)
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Dict:
        """Carrega um checkpoint específico"""
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} não encontrado")
        
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_checkpoints(self) -> List[Dict]:
        """Lista todos os checkpoints disponíveis"""
        checkpoints = []
        for file in self.checkpoints_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                checkpoints.append({
                    "id": file.stem,
                    "timestamp": data.get("timestamp", ""),
                    "description": data.get("description", "")
                })
        return checkpoints
    
    def backup_system(self, system_state: Dict) -> str:
        """Faz backup do estado do sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.system_backups_dir / f"backup_{timestamp}.json"
        
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(system_state, f, ensure_ascii=False, indent=2)
        
        return timestamp
    
    def restore_system(self, backup_id: str) -> Dict:
        """Restaura um backup do sistema"""
        backup_file = self.system_backups_dir / f"backup_{backup_id}.json"
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup {backup_id} não encontrado")
        
        with open(backup_file, "r", encoding="utf-8") as f:
            return json.load(f)
