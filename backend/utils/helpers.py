"""General-purpose helper functions."""

from __future__ import annotations

import time
import uuid
from typing import Any


def generate_id() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def timestamp() -> float:
    """Current UNIX timestamp."""
    return time.time()


def truncate(text: str, max_length: int = 200) -> str:
    """Truncate *text* to *max_length* characters with an ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_dict_get(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Nested dict lookup without KeyError."""
    current: Any = d
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current
