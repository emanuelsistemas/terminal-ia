from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from .config import DATA_DIR
from .logger import setup_logger

logger = setup_logger(__name__)

class ConversationMemory:
    def __init__(self):
        # Configuração simplificada do ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(DATA_DIR / "chroma_db")
        )
        
        # Coleções para diferentes tipos de memória
        self.short_term = None
        self.long_term = None
        self.permanent = None
        
        # Configurações
        self.max_short_term = 10  # Últimas 10 mensagens
        self.max_long_term = 100  # Últimas 100 mensagens relevantes
        
        logger.info("Sistema de memória inicializado com sucesso")
    
    async def initialize(self):
        """Inicializa as coleções de memória"""
        try:
            # Cria ou recupera coleções
            self.short_term = self.client.get_or_create_collection(
                name="short_term_memory"
            )
            
            self.long_term = self.client.get_or_create_collection(
                name="long_term_memory"
            )
            
            self.permanent = self.client.get_or_create_collection(
                name="permanent_memory"
            )
            
            logger.info("Coleções de memória inicializadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar coleções de memória: {str(e)}")
            raise
    
    def _format_message(self, message: Dict) -> str:
        """Formata a mensagem para armazenamento"""
        timestamp = datetime.fromisoformat(message["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {message['role']}: {message['content']}"
    
    def _get_metadata(self, message: Dict) -> Dict:
        """Cria metadados para a mensagem"""
        return {
            "id": message["id"],
            "role": message["role"],
            "timestamp": message["timestamp"]
        }
    
    async def add_message(self, message: Dict):
        """Adiciona uma mensagem à memória"""
        try:
            formatted_message = self._format_message(message)
            metadata = self._get_metadata(message)
            
            # Adiciona à memória de curto prazo
            self.short_term.add(
                documents=[formatted_message],
                metadatas=[metadata],
                ids=[message["id"]]
            )
            
            # Mantém apenas as últimas max_short_term mensagens
            all_ids = self.short_term.get()['ids']
            if len(all_ids) > self.max_short_term:
                self.short_term.delete(ids=all_ids[:-self.max_short_term])
            
            # Adiciona à memória de longo prazo se for uma mensagem importante
            if self._is_important_message(message):
                self.long_term.add(
                    documents=[formatted_message],
                    metadatas=[metadata],
                    ids=[message["id"]]
                )
                
                # Mantém apenas as últimas max_long_term mensagens importantes
                all_ids = self.long_term.get()['ids']
                if len(all_ids) > self.max_long_term:
                    self.long_term.delete(ids=all_ids[:-self.max_long_term])
            
            # Adiciona à memória permanente se for uma mensagem crítica
            if self._is_critical_message(message):
                self.permanent.add(
                    documents=[formatted_message],
                    metadatas=[metadata],
                    ids=[message["id"]]
                )
            
            logger.info(f"Mensagem {message['id']} adicionada à memória")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem à memória: {str(e)}")
            raise
    
    def _is_important_message(self, message: Dict) -> bool:
        """Determina se uma mensagem é importante para memória de longo prazo"""
        # Critérios para mensagens importantes:
        # 1. Todas as mensagens do assistente
        # 2. Mensagens do usuário com comandos ou perguntas complexas
        # 3. Mensagens com palavras-chave importantes
        
        content = message["content"].lower()
        
        # Lista de palavras-chave importantes
        important_keywords = [
            "lembrar", "importante", "não esquecer", "atenção",
            "configurar", "instalar", "definir", "mudar",
            "problema", "erro", "falha", "bug",
            "como", "por que", "quando", "onde", "qual",
            "!restore", "!list", "!clear"
        ]
        
        # Verifica se é mensagem do assistente
        if message["role"] == "assistant":
            return True
        
        # Verifica se contém palavras-chave importantes
        if any(keyword in content for keyword in important_keywords):
            return True
        
        # Verifica se é uma pergunta ou comando complexo
        if len(content.split()) > 5:  # Mensagens com mais de 5 palavras
            return True
        
        return False
    
    def _is_critical_message(self, message: Dict) -> bool:
        """Determina se uma mensagem é crítica para memória permanente"""
        # Critérios para mensagens críticas:
        # 1. Comandos de sistema (!restore, !list)
        # 2. Mensagens com erros ou problemas críticos
        # 3. Configurações importantes do sistema
        
        content = message["content"].lower()
        
        # Lista de palavras-chave críticas
        critical_keywords = [
            "!restore", "!list",
            "erro crítico", "falha grave",
            "configuração do sistema", "backup",
            "api key", "credenciais",
            "memória", "banco de dados"
        ]
        
        # Verifica se contém palavras-chave críticas
        return any(keyword in content for keyword in critical_keywords)
    
    async def get_recent_context(self, max_results: int = 10) -> List[str]:
        """Recupera as mensagens mais recentes do contexto"""
        try:
            results = []
            
            # Obtém mensagens da memória de curto prazo
            short_term_data = self.short_term.get()
            if short_term_data and short_term_data['documents']:
                results.extend(short_term_data['documents'])
            
            # Obtém mensagens importantes da memória de longo prazo
            long_term_data = self.long_term.get()
            if long_term_data and long_term_data['documents']:
                results.extend(long_term_data['documents'])
            
            # Remove duplicatas mantendo a ordem
            unique_results = []
            seen = set()
            for result in results:
                if result not in seen:
                    unique_results.append(result)
                    seen.add(result)
            
            # Retorna as últimas max_results mensagens
            return unique_results[-max_results:]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto recente: {str(e)}")
            return []
    
    async def get_relevant_context(self, query: str, max_results: int = 5) -> List[str]:
        """Recupera contexto relevante para uma query"""
        try:
            # Busca em todas as camadas de memória
            results = []
            
            # 1. Primeiro na memória de curto prazo (mais recente)
            short_term_results = self.short_term.query(
                query_texts=[query],
                n_results=max_results
            )
            if short_term_results and short_term_results['documents']:
                results.extend(short_term_results['documents'][0])
            
            # 2. Depois na memória de longo prazo
            long_term_results = self.long_term.query(
                query_texts=[query],
                n_results=max_results
            )
            if long_term_results and long_term_results['documents']:
                results.extend(long_term_results['documents'][0])
            
            # 3. Por fim, na memória permanente
            permanent_results = self.permanent.query(
                query_texts=[query],
                n_results=max_results
            )
            if permanent_results and permanent_results['documents']:
                results.extend(permanent_results['documents'][0])
            
            # Remove duplicatas mantendo a ordem
            unique_results = []
            seen = set()
            for result in results:
                if result not in seen:
                    unique_results.append(result)
                    seen.add(result)
            
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {str(e)}")
            return []
    
    async def clear(self):
        """Limpa todas as memórias"""
        try:
            self.short_term.delete(ids=self.short_term.get()['ids'])
            self.long_term.delete(ids=self.long_term.get()['ids'])
            self.permanent.delete(ids=self.permanent.get()['ids'])
            
            logger.info("Memória limpa com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar memória: {str(e)}")
            raise
