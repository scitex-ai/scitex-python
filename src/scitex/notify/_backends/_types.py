#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_types.py

"""Core types for notification backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NotifyLevel(Enum):
    """Notification urgency levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotifyResult:
    """Result of a notification attempt."""

    success: bool
    backend: str
    message: str
    timestamp: str
    error: Optional[str] = None
    details: Optional[dict] = None


class BaseNotifyBackend(ABC):
    """Base class for notification backends."""

    name: str = "base"

    @abstractmethod
    async def send(
        self,
        message: str,
        title: Optional[str] = None,
        level: NotifyLevel = NotifyLevel.INFO,
        **kwargs,
    ) -> NotifyResult:
        """Send a notification."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass


# EOF
