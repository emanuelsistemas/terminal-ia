import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pkg_resources
from .logger import setup_logger
from .config import DATA_DIR

logger = setup_logger(__name__)

class SystemBackup:
    def __init__(self, max_backups: int = 10):
        self.backup_dir = DATA_DIR / "system_backups"
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_installed_packages(self) -> List[str]:
        """Obtém lista de pacotes Python instalados com suas versões"""
        try:
            return [f"{dist.key}=={dist.version}" 
                    for dist in pkg_resources.working_set]
        except Exception as e:
            logger.error(f"Erro ao obter pacotes instalados: {str(e)}")
            return []

    def get_system_services(self) -> List[Dict]:
        """Obtém status dos serviços do sistema"""
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--plain"],
                capture_output=True,
                text=True
            )
            services = []
            for line in result.stdout.split("\n")[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            "name": parts[0],
                            "status": parts[3]
                        })
            return services
        except Exception as e:
            logger.error(f"Erro ao obter serviços: {str(e)}")
            return []

    def create_backup(self, message_id: str, messages: List[Dict]) -> bool:
        """Cria um backup completo do sistema"""
        try:
            backup_path = self.backup_dir / message_id
            backup_path.mkdir(parents=True, exist_ok=True)

            # Backup de mensagens
            with open(backup_path / "messages.json", "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)

            # Backup de pacotes instalados
            with open(backup_path / "packages.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(self.get_installed_packages()))

            # Backup de serviços
            with open(backup_path / "services.json", "w", encoding="utf-8") as f:
                json.dump(self.get_system_services(), f, ensure_ascii=False, indent=2)

            # Backup de arquivos do projeto
            project_backup = backup_path / "project"
            project_backup.mkdir(parents=True, exist_ok=True)
            
            # Define diretórios para backup
            dirs_to_backup = [
                "src",
                "data",
                "config",
                "scripts"
            ]
            
            # Copia diretórios do projeto
            for dir_name in dirs_to_backup:
                src_path = Path("/root/projetos/chat-ia-terminal") / dir_name
                if src_path.exists():
                    dst_path = project_backup / dir_name
                    if src_path.is_dir():
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)

            # Metadata do backup
            metadata = {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "python_version": pkg_resources.get_distribution("pip").version,
            }
            
            with open(backup_path / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"Backup completo criado: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return False

    def restore_backup(self, message_id: str) -> Optional[Dict]:
        """Restaura um backup completo do sistema"""
        try:
            backup_path = self.backup_dir / message_id
            if not backup_path.exists():
                logger.error(f"Backup não encontrado: {message_id}")
                return None

            # Restaura mensagens
            with open(backup_path / "messages.json", "r", encoding="utf-8") as f:
                messages = json.load(f)

            # Restaura pacotes
            with open(backup_path / "packages.txt", "r", encoding="utf-8") as f:
                packages = f.read().splitlines()
                subprocess.run(["pip", "install", "-r", backup_path / "packages.txt"])

            # Restaura arquivos do projeto
            project_backup = backup_path / "project"
            if project_backup.exists():
                for item in project_backup.iterdir():
                    dst_path = Path("/root/projetos/chat-ia-terminal") / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dst_path)

            logger.info(f"Backup restaurado: {message_id}")
            return messages

        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return None

    def cleanup_old_backups(self):
        """Remove backups antigos mantendo apenas max_backups"""
        try:
            backups = [d for d in self.backup_dir.iterdir() if d.is_dir()]
            if len(backups) > self.max_backups:
                # Ordena por data de modificação, mais antigos primeiro
                backups.sort(key=lambda x: x.stat().st_mtime)
                
                # Remove os mais antigos
                for backup in backups[:-self.max_backups]:
                    shutil.rmtree(backup)
                    logger.info(f"Backup antigo removido: {backup.name}")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")

    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            for backup_dir in sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            ):
                try:
                    with open(backup_dir / "metadata.json", "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    with open(backup_dir / "messages.json", "r", encoding="utf-8") as f:
                        messages = json.load(f)
                        last_message = messages[-1]
                    
                    backups.append({
                        "id": metadata["id"],
                        "timestamp": metadata["timestamp"],
                        "python_version": metadata.get("python_version", "unknown"),
                        "last_message": last_message["content"][:100] + "..." 
                            if len(last_message["content"]) > 100 
                            else last_message["content"]
                    })
                except Exception as e:
                    logger.error(f"Erro ao ler backup {backup_dir.name}: {str(e)}")
                    continue
                    
            return backups
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []
