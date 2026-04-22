import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger
from app.config import settings
from app.services.chroma_service import chroma_service


class BackupManager:
    def __init__(self):
        self.backup_path = settings.get_backup_path()

    def create_backup(self, knowledge_base_name: str) -> Optional[str]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{knowledge_base_name}_{timestamp}"
            backup_dir = self.backup_path / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)

            chroma_path = settings.get_chroma_path()
            chroma_backup = backup_dir / "chroma"
            if chroma_path.exists():
                shutil.copytree(chroma_path, chroma_backup)

            metadata = {
                "knowledge_base_name": knowledge_base_name,
                "backup_time": timestamp,
                "chroma_path": str(chroma_backup)
            }
            with open(backup_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"备份创建成功: {backup_name}")
            return str(backup_dir)
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            return None

    def restore_backup(self, backup_path: str, knowledge_base_name: str) -> bool:
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                logger.error(f"备份不存在: {backup_path}")
                return False

            chroma_backup = backup_dir / "chroma"
            if not chroma_backup.exists():
                logger.error(f"备份中没有 Chroma 数据")
                return False

            chroma_path = settings.get_chroma_path()
            if chroma_path.exists():
                shutil.rmtree(chroma_path)
            shutil.copytree(chroma_backup, chroma_path)

            logger.info(f"备份还原成功: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"还原备份失败: {str(e)}")
            return False

    def list_backups(self) -> list:
        try:
            backups = []
            for item in self.backup_path.iterdir():
                if item.is_dir():
                    metadata_file = item / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            backups.append(metadata)
            return backups
        except Exception as e:
            logger.error(f"列出备份失败: {str(e)}")
            return []

    def delete_backup(self, backup_path: str) -> bool:
        try:
            backup_dir = Path(backup_path)
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                logger.info(f"删除备份: {backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除备份失败: {str(e)}")
            return False


backup_manager = BackupManager()
