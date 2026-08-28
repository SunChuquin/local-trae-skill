import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    chroma_persist_directory: str = "./data/chroma"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32

    chunk_size: int = 500
    chunk_overlap: int = 150

    # 上传处理并发上限：一次只处理一个文档（默认1），避免 CPU 并发向量化卡死
    max_concurrent_uploads: int = 1

    default_top_k: int = 5
    default_similarity_threshold: float = 0.4

    backup_directory: str = "./data/backup"
    data_directory: str = "./data"
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_data_path(self) -> Path:
        path = Path(self.data_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_chroma_path(self) -> Path:
        path = Path(self.chroma_persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_backup_path(self) -> Path:
        path = Path(self.backup_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_log_path(self) -> Path:
        path = Path(self.log_file).parent
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
