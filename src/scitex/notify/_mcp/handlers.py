#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_mcp/handlers.py

"""MCP handlers for scitex-notify server."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

__all__ = [
    "notify_handler",
    "notify_by_level_handler",
    "list_backends_handler",
    "available_backends_handler",
    "get_config_handler",
]


async def notify_handler(
    message: str,
    title: Optional[str] = None,
    level: str = "info",
    backend: Optional[str] = None,
    backends: Optional[list[str]] = None,
    timeout: float = 5.0,
) -> dict:
    """Send notification via specified backend(s)."""
    from .._backends import BACKENDS, NotifyLevel, get_backend
    from .._backends._config import get_config

    try:
        # Determine notification level
        try:
            notify_level = NotifyLevel(level.lower())
        except ValueError:
            notify_level = NotifyLevel.INFO

        # Determine backends to use
        config = get_config()
        if backends:
            backend_list = backends
        elif backend:
            backend_list = [backend]
        else:
            backend_list = [config.default_backend]

        results = []
        success_count = 0

        for backend_name in backend_list:
            try:
                if backend_name not in BACKENDS:
                    results.append(
                        {
                            "backend": backend_name,
                            "success": False,
                            "error": f"Unknown backend: {backend_name}",
                        }
                    )
                    continue

                b = get_backend(backend_name)
                result = await b.send(
                    message,
                    title=title,
                    level=notify_level,
                    timeout=timeout,
                )

                results.append(
                    {
                        "backend": backend_name,
                        "success": result.success,
                        "error": result.error,
                        "details": result.details,
                    }
                )

                if result.success:
                    success_count += 1

            except Exception as e:
                results.append(
                    {
                        "backend": backend_name,
                        "success": False,
                        "error": str(e),
                    }
                )

        return {
            "success": success_count > 0,
            "message": message,
            "title": title,
            "level": level,
            "backends_used": backend_list,
            "results": results,
            "success_count": success_count,
            "total_count": len(backend_list),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def notify_by_level_handler(
    message: str,
    title: Optional[str] = None,
    level: str = "info",
) -> dict:
    """Send notification using backends configured for the level."""
    from .._backends import NotifyLevel
    from .._backends._config import get_config

    try:
        # Determine notification level
        try:
            notify_level = NotifyLevel(level.lower())
        except ValueError:
            notify_level = NotifyLevel.INFO

        # Get backends configured for this level
        config = get_config()
        backend_list = config.get_available_backends_for_level(notify_level)

        if not backend_list:
            backend_list = [config.default_backend]

        # Use notify_handler with determined backends
        return await notify_handler(
            message=message,
            title=title,
            level=level,
            backends=backend_list,
        )

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def list_backends_handler() -> dict:
    """List all notification backends with their status."""
    from .._backends import BACKENDS
    from .._backends._config import is_backend_available

    try:
        backends_info = []

        for name, cls in BACKENDS.items():
            try:
                backend = cls()
                is_available = backend.is_available()
                pkg_available = is_backend_available(name)

                backends_info.append(
                    {
                        "name": name,
                        "available": is_available,
                        "package_available": pkg_available,
                        "class": cls.__name__,
                    }
                )
            except Exception as e:
                backends_info.append(
                    {
                        "name": name,
                        "available": False,
                        "error": str(e),
                    }
                )

        return {
            "success": True,
            "backends": backends_info,
            "total_count": len(backends_info),
            "available_count": sum(1 for b in backends_info if b.get("available")),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def available_backends_handler() -> dict:
    """Get list of currently available backends."""
    from .._backends import available_backends

    try:
        available = available_backends()

        return {
            "success": True,
            "available_backends": available,
            "count": len(available),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def get_config_handler() -> dict:
    """Get current notification configuration."""
    from .._backends._config import UIConfig, get_config

    try:
        # Reset to get fresh config
        UIConfig.reset()
        config = get_config()

        return {
            "success": True,
            "config": {
                "default_backend": config.default_backend,
                "backend_priority": config.backend_priority,
                "available_priority": config.get_available_backend_priority(),
                "first_available": config.get_first_available_backend(),
                "level_backends": {
                    "info": config._config.get("level_backends", {}).get("info", []),
                    "warning": config._config.get("level_backends", {}).get(
                        "warning", []
                    ),
                    "error": config._config.get("level_backends", {}).get("error", []),
                    "critical": config._config.get("level_backends", {}).get(
                        "critical", []
                    ),
                },
                "timeouts": config._config.get("timeouts", {}),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# EOF
