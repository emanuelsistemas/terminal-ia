from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import logging

class ChatLogger:
    def __init__(self, log_dir: str = "/root/projetos/chat-ia-terminal/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configura logging básico
        self.setup_logging()
        
        # Arquivo de log do dia
        self.current_date = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"{self.current_date}_chat.log"
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),  # Console
                logging.FileHandler(  # Arquivo
                    self.log_dir / "chat.log",
                    encoding="utf-8"
                )
            ]
        )
        self.logger = logging.getLogger("ChatBot")
    
    def _rotate_log_file(self):
        """Rotaciona o arquivo de log se necessário"""
        current_date = datetime.now().strftime("%Y%m%d")
        if current_date != self.current_date:
            self.current_date = current_date
            self.log_file = self.log_dir / f"{self.current_date}_chat.log"
    
    def log_message(self, 
                    level: str,
                    message: str,
                    chat_id: Optional[int] = None,
                    provider: Optional[str] = None,
                    extra: Optional[Dict[str, Any]] = None):
        """Registra uma mensagem no log"""
        self._rotate_log_file()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "chat_id": chat_id,
            "provider": provider
        }
        
        if extra:
            log_entry.update(extra)
        
        # Registra no arquivo de log do dia
        with open(self.log_file, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
        
        # Registra no logger do sistema
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def get_logs(self,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 level: Optional[str] = None,
                 chat_id: Optional[int] = None,
                 provider: Optional[str] = None) -> list:
        """Recupera logs com filtros"""
        logs = []
        
        # Determina quais arquivos processar
        if start_date and end_date:
            log_files = sorted(self.log_dir.glob("*_chat.log"))
            log_files = [f for f in log_files 
                        if start_date <= f.stem.split("_")[0] <= end_date]
        else:
            log_files = [self.log_file]
        
        # Processa cada arquivo
        for log_file in log_files:
            if not log_file.exists():
                continue
                
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Aplica filtros
                        if level and entry.get("level") != level:
                            continue
                        if chat_id and entry.get("chat_id") != chat_id:
                            continue
                        if provider and entry.get("provider") != provider:
                            continue
                            
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        return logs
    
    def export_logs(self, output_file: str, **filters) -> str:
        """Exporta logs filtrados para um arquivo"""
        logs = self.get_logs(**filters)
        
        output_path = self.log_dir / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Remove logs mais antigos que o especificado"""
        cutoff_date = datetime.now().strftime("%Y%m%d")
        
        for log_file in self.log_dir.glob("*_chat.log"):
            try:
                file_date = log_file.stem.split("_")[0]
                if file_date < cutoff_date:
                    log_file.unlink()
            except (IndexError, ValueError):
                continue
