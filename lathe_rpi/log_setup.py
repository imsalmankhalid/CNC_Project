"""
Central logging configuration for the MbW Lathe application.

Call ``setup_logging()`` once at start-up (done automatically by main.py /
ui.app.run_app()).  It configures the root logger so every module's logs go to
the console and/or a rotating log file, based on the settings in config.py.

Settings (config.py):
    LOG_TO_CONSOLE   – echo logs to the terminal / stderr
    LOG_TO_FILE      – also write logs to LOG_FILE
    LOG_FILE         – file path (relative to project dir, or absolute)
    LOG_LEVEL        – "DEBUG" | "INFO" | "WARNING" | "ERROR"
    LOG_MAX_BYTES    – rotate the log file after this many bytes
    LOG_BACKUP_COUNT – how many rotated files to keep

Debug logging is forced on when DEBUG_HAL is True in config.py or the
environment variable LATHE_DEBUG_HAL=1 is set.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

import config as cfg

_CONFIGURED = False

_FMT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_DATEFMT = "%H:%M:%S"


def debug_forced() -> bool:
    """Return True when debug logging should be forced on."""
    if os.environ.get("LATHE_DEBUG_HAL", "").strip() in ("1", "true", "True"):
        return True
    return bool(getattr(cfg, "DEBUG_HAL", False))


def _resolve_log_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    # Relative paths are resolved against the project directory (this file's dir)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def setup_logging(force: bool = False) -> str | None:
    """
    Configure the root logger from config.py settings.

    Idempotent: calling it more than once is a no-op unless ``force`` is True.
    Returns the absolute path of the log file if file logging is enabled,
    otherwise None.
    """
    global _CONFIGURED
    if _CONFIGURED and not force:
        return None
    _CONFIGURED = True

    level_name = "DEBUG" if debug_forced() else getattr(cfg, "LOG_LEVEL", "INFO")
    level = getattr(logging, str(level_name).upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Clear any handlers a stray basicConfig() may have installed so we do not
    # emit duplicate lines.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(_FMT, datefmt=_DATEFMT)

    if getattr(cfg, "LOG_TO_CONSOLE", True):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    log_path: str | None = None
    if getattr(cfg, "LOG_TO_FILE", False):
        log_path = _resolve_log_path(getattr(cfg, "LOG_FILE", "logs/lathe.log"))
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=int(getattr(cfg, "LOG_MAX_BYTES", 2_000_000)),
                backupCount=int(getattr(cfg, "LOG_BACKUP_COUNT", 3)),
            )
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError as exc:
            root.warning("Could not open log file %s: %s", log_path, exc)
            log_path = None

    logging.getLogger("log_setup").info(
        "Logging initialised (level=%s console=%s file=%s)",
        level_name,
        getattr(cfg, "LOG_TO_CONSOLE", True),
        log_path or "off",
    )
    return log_path
