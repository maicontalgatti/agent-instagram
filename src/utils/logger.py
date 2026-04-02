"""Logging estruturado para o pipeline editorial."""

from __future__ import annotations

import logging
import sys
from typing import Any

_LOG = logging.getLogger("agent_instagram")
_HANDLER: logging.Handler | None = None


def setup_logging(level: int = logging.INFO) -> None:
    global _HANDLER
    if _HANDLER is not None:
        return
    _HANDLER = logging.StreamHandler(sys.stdout)
    _HANDLER.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    _LOG.setLevel(level)
    _LOG.addHandler(_HANDLER)


def get_logger(name: str | None = None) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name or "agent_instagram.pipeline")


def log_kv(logger: logging.Logger, msg: str, **kwargs: Any) -> None:
    if not kwargs:
        logger.info(msg)
        return
    parts = [msg] + [f"{k}={v!r}" for k, v in kwargs.items()]
    logger.info(" | ".join(parts))
