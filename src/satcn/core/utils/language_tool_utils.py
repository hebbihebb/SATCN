import logging
import threading
from shutil import which
from typing import Optional, Tuple

import language_tool_python


_logger = logging.getLogger(__name__)
_cache_lock = threading.Lock()
_cached_tool: Optional[Tuple[object, str]] = None


def is_java_available() -> bool:
    """Return True when a `java` executable is present on the PATH."""

    return which("java") is not None


def _build_language_tool(logger: Optional[logging.Logger] = None):
    """Instantiate the best available LanguageTool backend."""

    log = logger or _logger

    if is_java_available():
        try:
            tool = language_tool_python.LanguageTool("en-US")
            log.info(
                "Initialized LanguageTool JVM backend.",
                extra={"event": "language_tool_initialized", "backend": "java"},
            )
            return tool, "java"
        except Exception:
            log.exception(
                "Failed to initialize LanguageTool JVM backend.",
                extra={"event": "language_tool_init_error", "backend": "java"},
            )
    else:
        log.warning(
            "Java runtime not detected; attempting LanguageTool public API fallback.",
            extra={"event": "language_tool_java_missing"},
        )

    try:
        tool = language_tool_python.LanguageToolPublicAPI("en-US")
        log.info(
            "Initialized LanguageTool public API backend.",
            extra={"event": "language_tool_initialized", "backend": "public_api"},
        )
        return tool, "public_api"
    except Exception:
        log.exception(
            "Failed to initialize LanguageTool public API backend; grammar corrections disabled.",
            extra={"event": "language_tool_init_error", "backend": "public_api"},
        )
        return None, "disabled"


def get_language_tool(
    logger: Optional[logging.Logger] = None, force_refresh: bool = False
):
    """Return a cached LanguageTool client and its backend identifier."""

    global _cached_tool
    with _cache_lock:
        if force_refresh or _cached_tool is None:
            _cached_tool = _build_language_tool(logger)
        return _cached_tool


def reset_language_tool_cache():
    """Clear the cached LanguageTool client (used by tests)."""

    global _cached_tool
    with _cache_lock:
        _cached_tool = None
