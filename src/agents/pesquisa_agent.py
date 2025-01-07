from typing import Dict, List
import logging
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class PesquisaAgent:
    def __init__(self):
        self.search_url = "https://ddg-api.herokuapp.com/search"
    
    async def pesquisar(self, query: str, max_results: int = 3) -> List[Dict]:
        """Realiza uma pesquisa web e retorna os resultados mais relevantes"""
        try:
            # Faz a pesquisa
            response = requests.get(
                self.search_url,
                params={"query": query, "limit": max_results}
            )
            results = response.json()
            
            # Formata os resultados
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro ao realizar pesquisa: {e}")
            return []
    
    async def extrair_conteudo(self, url: str) -> str:
        """Extrai o conteúdo principal de uma página web"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Pega o texto
            text = soup.get_text()
            
            # Limpa o texto
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return text[:1000]  # Limita o tamanho do texto
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo: {e}")
            return ""
