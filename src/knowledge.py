from typing import List, Dict, Optional
import json
import requests
from pathlib import Path
from datetime import datetime
from .config import DATA_DIR
from .logger import setup_logger

logger = setup_logger(__name__)

class KnowledgeBase:
    def __init__(self):
        self.cache_file = DATA_DIR / "knowledge_cache.json"
        self.cache: Dict = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carrega cache de conhecimento"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
        return {}
    
    def _save_cache(self):
        """Salva cache de conhecimento"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Realiza busca na web (exemplo com DuckDuckGo)"""
        try:
            # Aqui você pode integrar com APIs de busca como DuckDuckGo, Google, etc.
            # Por enquanto, retornamos um resultado simulado
            return [{
                "title": "Resultado simulado",
                "snippet": "Este é um resultado de busca simulado.",
                "url": "https://exemplo.com"
            }]
        except Exception as e:
            logger.error(f"Erro na busca web: {str(e)}")
            return []
    
    def search_local_knowledge(self, query: str) -> List[str]:
        """Busca no conhecimento local"""
        relevant_info = []
        for key, value in self.cache.items():
            if query.lower() in key.lower():
                relevant_info.append(value)
        return relevant_info
    
    def add_to_knowledge(self, key: str, content: str):
        """Adiciona informação ao conhecimento local"""
        self.cache[key] = {
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()

class ContextAnalyzer:
    def __init__(self):
        self.kb = KnowledgeBase()
    
    def analyze_message(self, message: str) -> Dict:
        """Analisa a mensagem e determina a melhor fonte de informação"""
        analysis = {
            "requires_web_search": False,
            "requires_local_knowledge": False,
            "requires_code_analysis": False,
            "identified_topics": [],
            "confidence": 0.0
        }
        
        # Identificar se a mensagem contém palavras-chave que indicam necessidade de pesquisa
        web_search_keywords = ["atual", "novo", "última versão", "recente", "notícia"]
        code_keywords = ["código", "função", "classe", "método", "implementação"]
        
        message_lower = message.lower()
        
        # Verifica necessidade de busca web
        for keyword in web_search_keywords:
            if keyword in message_lower:
                analysis["requires_web_search"] = True
                analysis["identified_topics"].append(f"web_search:{keyword}")
        
        # Verifica necessidade de análise de código
        for keyword in code_keywords:
            if keyword in message_lower:
                analysis["requires_code_analysis"] = True
                analysis["identified_topics"].append(f"code:{keyword}")
        
        # Verifica conhecimento local
        local_results = self.kb.search_local_knowledge(message)
        if local_results:
            analysis["requires_local_knowledge"] = True
            analysis["confidence"] = 0.8
        
        return analysis

class InformationManager:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.analyzer = ContextAnalyzer()
    
    async def get_information(self, query: str) -> Dict:
        """Obtém informações de várias fontes baseado na análise de contexto"""
        analysis = self.analyzer.analyze_message(query)
        results = {
            "local_knowledge": [],
            "web_results": [],
            "code_analysis": [],
            "analysis": analysis
        }
        
        if analysis["requires_local_knowledge"]:
            results["local_knowledge"] = self.kb.search_local_knowledge(query)
        
        if analysis["requires_web_search"]:
            results["web_results"] = self.kb.search_web(query)
        
        return results
