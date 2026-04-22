import sys
from pathlib import Path
from loguru import logger as _logger
from app.config import settings


def setup_logger():
    log_path = settings.get_log_path()
    log_file = log_path / "app.log"

    _logger.remove()

    _logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    _logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        errors="replace",
    )

    _logger.info("日志系统初始化完成")


setup_logger()

logger = _logger
