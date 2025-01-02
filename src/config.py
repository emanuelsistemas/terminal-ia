from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

class Config:
    def __init__(self, config_dir: str = "/root/projetos/chat-ia-terminal/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.config: Dict[str, Any] = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Configurações padrão
        return {
            "providers": {
                "groq": {
                    "model": "mixtral-8x7b-32768",
                    "description": "Mixtral 8x7B - mais rápido e versátil"
                },
                "deepseek": {
                    "model": "deepseek-chat",
                    "description": "DeepSeek Chat - mais preciso e detalhado"
                }
            },
            "default_provider": "groq",
            "log_level": "INFO",
            "max_tokens": 2000,
            "temperature": 0.7,
            "language": "pt-BR",
            "features": {
                "knowledge_base": True,
                "conversation_memory": True,
                "system_prompts": True
            },
            "paths": {
                "data": "/root/projetos/chat-ia-terminal/data",
                "logs": "/root/projetos/chat-ia-terminal/logs",
                "prompts": "/root/projetos/chat-ia-terminal/prompts"
            }
        }
    
    def save_config(self):
        """Salva configurações no arquivo"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Define um valor de configuração"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Atualiza múltiplas configurações"""
        self.config.update(updates)
        self.save_config()
    
    def reset(self, key: Optional[str] = None):
        """Reseta configurações para o padrão"""
        default_config = self.load_config()
        
        if key:
            if key in default_config:
                self.config[key] = default_config[key]
        else:
            self.config = default_config
        
        self.save_config()
    
    def backup(self) -> str:
        """Cria um backup das configurações"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_dir / f"config_backup_{timestamp}.json"
        
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        return str(backup_file)
    
    def restore(self, backup_file: str):
        """Restaura configurações de um backup"""
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
        
        with open(backup_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.save_config()
