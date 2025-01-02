from typing import Optional, List, Dict
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
from datetime import datetime
from .config import DATA_DIR
from .logger import setup_logger

logger = setup_logger(__name__)

class BrowserTest:
    def __init__(self):
        self.screenshots_dir = DATA_DIR / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = DATA_DIR / "browser_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.test_results: List[Dict] = []
    
    def _save_screenshot(self, page, name: str) -> str:
        """Salva screenshot da página"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        page.screenshot(path=str(filepath))
        return str(filepath)
    
    def _save_logs(self, logs: List[Dict], name: str) -> str:
        """Salva logs do navegador"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.json"
        filepath = self.logs_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        return str(filepath)
    
    def test_page(self, url: str, name: str = "test") -> Dict:
        """Testa uma página web e coleta logs e screenshots"""
        result = {
            "url": url,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "errors": [],
            "warnings": [],
            "console_logs": [],
            "screenshots": [],
            "performance": {}
        }
        
        try:
            with sync_playwright() as p:
                # Inicia o navegador
                browser = p.chromium.launch()
                context = browser.new_context()
                page = context.new_page()
                
                # Coleta logs do console
                page.on("console", lambda msg: result["console_logs"].append({
                    "type": msg.type,
                    "text": msg.text,
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Coleta erros
                page.on("pageerror", lambda err: result["errors"].append({
                    "message": str(err),
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Navega para a página
                response = page.goto(url, wait_until="networkidle")
                result["status_code"] = response.status if response else None
                
                # Tira screenshot inicial
                result["screenshots"].append({
                    "name": "initial",
                    "path": self._save_screenshot(page, f"{name}_initial")
                })
                
                # Testa interações básicas
                page.mouse.move(100, 100)
                page.mouse.wheel(delta_y=100)
                
                # Tira screenshot após interação
                result["screenshots"].append({
                    "name": "after_interaction",
                    "path": self._save_screenshot(page, f"{name}_after_interaction")
                })
                
                # Coleta métricas de performance
                performance = page.evaluate("""
                    () => {
                        const timing = window.performance.timing;
                        return {
                            loadTime: timing.loadEventEnd - timing.navigationStart,
                            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                            firstPaint: timing.responseEnd - timing.navigationStart
                        }
                    }
                """)
                result["performance"] = performance
                
                # Fecha o navegador
                browser.close()
                
                # Salva logs
                result["logs_file"] = self._save_logs(
                    result["console_logs"],
                    f"{name}_console_logs"
                )
                
                result["success"] = True
                
        except Exception as e:
            logger.error(f"Erro no teste do navegador: {str(e)}")
            result["errors"].append({
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        self.test_results.append(result)
        return result
    
    def get_test_report(self) -> str:
        """Gera um relatório dos testes realizados"""
        report = []
        report.append("=== Relatório de Testes do Navegador ===")
        
        for result in self.test_results:
            report.append(f"\nTeste: {result['name']}")
            report.append(f"URL: {result['url']}")
            report.append(f"Status: {'✓ Sucesso' if result['success'] else '✗ Falha'}")
            
            if result["errors"]:
                report.append("\nErros:")
                for error in result["errors"]:
                    report.append(f"- {error['message']}")
            
            if result["console_logs"]:
                report.append("\nLogs do Console:")
                for log in result["console_logs"]:
                    report.append(f"- [{log['type']}] {log['text']}")
            
            if result["performance"]:
                report.append("\nPerformance:")
                for metric, value in result["performance"].items():
                    report.append(f"- {metric}: {value}ms")
            
            report.append("\nScreenshots:")
            for screenshot in result["screenshots"]:
                report.append(f"- {screenshot['name']}: {screenshot['path']}")
            
            report.append("\n" + "-"*50)
        
        return "\n".join(report)
