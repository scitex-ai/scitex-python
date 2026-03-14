#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/_config.py

"""Configuration for notification backends using scitex.config.

Priority resolution (same as ScitexConfig):
    direct → config (YAML) → env → default

Configuration sources:
1. YAML file: ~/.scitex/config.yaml or custom path via SCITEX_UI_CONFIG
2. Environment variables: SCITEX_UI_*

Example YAML (in default.yaml or custom file):
    ui:
      default_backend: audio
      backend_priority:
        - audio
        - desktop
        - email
      level_backends:
        info: [audio]
        warning: [audio, desktop]
        error: [audio, desktop, email]
        critical: [audio, desktop, email]
      timeouts:
        matplotlib: 5.0
        playwright: 5.0

Environment variables:
    SCITEX_UI_CONFIG: Path to custom UI config file
    SCITEX_UI_DEFAULT_BACKEND: audio
    SCITEX_UI_BACKEND_PRIORITY: audio,desktop,email (comma-separated)
    SCITEX_UI_INFO_BACKENDS: audio (comma-separated)
    SCITEX_UI_WARNING_BACKENDS: audio,desktop
    SCITEX_UI_ERROR_BACKENDS: audio,desktop,email
    SCITEX_UI_CRITICAL_BACKENDS: audio,desktop,email
"""

from __future__ import annotations

import importlib.util
import os
from functools import lru_cache
from typing import Optional

from ._types import NotifyLevel

# Backend package requirements
BACKEND_PACKAGES = {
    "audio": None,  # Uses MCP or pyttsx3 (optional)
    "desktop": None,  # Uses PowerShell on WSL (no package needed)
    "emacs": None,  # Uses emacsclient (no Python package needed)
    "matplotlib": "matplotlib",
    "playwright": "playwright",
    "email": None,  # Uses stdlib smtplib
    "webhook": None,  # Uses stdlib urllib
}


@lru_cache(maxsize=16)
def is_package_available(package: str) -> bool:
    """Check if a Python package is available."""
    if package is None:
        return True
    return importlib.util.find_spec(package) is not None


def is_backend_available(backend: str) -> bool:
    """Check if a backend's required packages are available."""
    package = BACKEND_PACKAGES.get(backend)
    return is_package_available(package)


# Default configuration (used if not in YAML)
DEFAULT_CONFIG = {
    "default_backend": "audio",
    "backend_priority": [
        "audio",
        "emacs",
        "desktop",
        "matplotlib",
        "playwright",
        "email",
        "webhook",
    ],
    "level_backends": {
        "info": ["audio"],
        "warning": ["audio", "emacs"],
        "error": ["audio", "emacs", "desktop", "email"],
        "critical": ["audio", "emacs", "desktop", "matplotlib", "email"],
    },
    "timeouts": {
        "matplotlib": 5.0,
        "playwright": 5.0,
    },
}


class UIConfig:
    """Configuration manager for scitex.notify using ScitexConfig pattern."""

    _instance: Optional[UIConfig] = None
    _config: dict

    def __new__(cls, config_path: Optional[str] = None):
        # Allow creating new instance with custom path
        if config_path is not None:
            instance = super().__new__(cls)
            instance._config = {}
            instance._config_path = config_path
            instance._load_config()
            return instance

        # Otherwise use singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
            cls._instance._config_path = None
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from ScitexConfig and environment."""
        self._config = DEFAULT_CONFIG.copy()
        self._config["level_backends"] = DEFAULT_CONFIG["level_backends"].copy()
        self._config["timeouts"] = DEFAULT_CONFIG["timeouts"].copy()

        # Try to load from ScitexConfig (integrates with default.yaml)
        try:
            from scitex.config import get_config

            # Support custom config path via env var or constructor
            config_path = self._config_path or os.getenv("SCITEX_UI_CONFIG")
            scitex_config = get_config(config_path)

            # Get UI section from config
            ui_config = scitex_config.get_nested("ui") or {}

            if ui_config:
                # Update default_backend
                if "default_backend" in ui_config:
                    self._config["default_backend"] = ui_config["default_backend"]

                # Update backend_priority
                if "backend_priority" in ui_config:
                    self._config["backend_priority"] = ui_config["backend_priority"]

                # Update level_backends
                if "level_backends" in ui_config:
                    for level, backends in ui_config["level_backends"].items():
                        self._config["level_backends"][level] = backends

                # Update timeouts
                if "timeouts" in ui_config:
                    self._config["timeouts"].update(ui_config["timeouts"])

        except ImportError:
            pass  # scitex.config not available
        except Exception:
            pass  # Config loading failed

        # Override with environment variables (env has lowest priority after config)
        self._load_env_overrides()

    def _load_env_overrides(self):
        """Load environment variable overrides."""
        if os.getenv("SCITEX_UI_DEFAULT_BACKEND"):
            self._config["default_backend"] = os.getenv("SCITEX_UI_DEFAULT_BACKEND")

        if os.getenv("SCITEX_UI_BACKEND_PRIORITY"):
            self._config["backend_priority"] = os.getenv(
                "SCITEX_UI_BACKEND_PRIORITY"
            ).split(",")

        # Level-specific backends from env
        for level in ["info", "warning", "error", "critical"]:
            env_key = f"SCITEX_UI_{level.upper()}_BACKENDS"
            if os.getenv(env_key):
                self._config["level_backends"][level] = os.getenv(env_key).split(",")

        # Timeouts from env
        for backend in ["matplotlib", "playwright"]:
            env_key = f"SCITEX_UI_TIMEOUT_{backend.upper()}"
            if os.getenv(env_key):
                try:
                    self._config["timeouts"][backend] = float(os.getenv(env_key))
                except ValueError:
                    pass

    @property
    def default_backend(self) -> str:
        return self._config.get("default_backend", "audio")

    @property
    def backend_priority(self) -> list[str]:
        return self._config.get("backend_priority", ["audio"])

    def get_available_backend_priority(self) -> list[str]:
        """Get backend priority filtered by package availability."""
        return [b for b in self.backend_priority if is_backend_available(b)]

    def get_backends_for_level(self, level: NotifyLevel) -> list[str]:
        """Get configured backends for a notification level."""
        level_backends = self._config.get("level_backends", {})
        return level_backends.get(level.value, [self.default_backend])

    def get_available_backends_for_level(self, level: NotifyLevel) -> list[str]:
        """Get backends for level filtered by package availability."""
        backends = self.get_backends_for_level(level)
        return [b for b in backends if is_backend_available(b)]

    def get_first_available_backend(self) -> str:
        """Get first available backend from priority list."""
        for backend in self.backend_priority:
            if is_backend_available(backend):
                return backend
        return self.default_backend

    def get_timeout(self, backend: str) -> float:
        """Get timeout for a backend."""
        timeouts = self._config.get("timeouts", {})
        value = timeouts.get(backend, 5.0)
        return float(value) if value is not None else 5.0

    def reload(self):
        """Reload configuration from files."""
        self._load_config()

    @classmethod
    def reset(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None


def get_config(config_path: Optional[str] = None) -> UIConfig:
    """Get the UI configuration instance.

    Parameters
    ----------
    config_path : str, optional
        Path to custom config file. If provided, creates new instance.
        Otherwise returns cached singleton.
    """
    if config_path:
        return UIConfig(config_path)
    return UIConfig()


# EOF
