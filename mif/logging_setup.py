"""Centralized logging setup helpers."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_file_logger(name: str, log_filename: str, level: int = logging.DEBUG) -> logging.Logger:
    """Create/reuse a logger that writes to logs/<log_filename>."""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    target_path = (log_dir / log_filename).resolve()
    has_handler = False
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            try:
                if Path(handler.baseFilename).resolve() == target_path:
                    has_handler = True
                    break
            except Exception:
                continue

    if not has_handler:
        file_handler = logging.FileHandler(target_path, encoding="utf-8", mode="a")
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    return logger
