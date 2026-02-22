#!/usr/bin/env python3
"""Clew Registry client — remote hash registration via scitex.ai.

Provides optional cloud-based timestamp verification. When a hash is
registered, the server assigns a trusted timestamp proving the data
existed at that point in time.

Configuration (environment variables):
    SCITEX_REGISTRY_URL: Base URL (default: https://scitex.ai)
    SCITEX_API_KEY: API key for authentication
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from ._db import get_db

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_URL = "https://scitex.ai"


class ClewRegistry:
    """HTTP client for the Clew Registry on scitex.ai."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = (
            base_url or os.environ.get("SCITEX_REGISTRY_URL") or DEFAULT_REGISTRY_URL
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("SCITEX_API_KEY")

    def register(
        self,
        hash_value: str,
        source_type: str = "manual",
        session_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a hash with the remote registry.

        Parameters
        ----------
        hash_value : str
            The hash to register (SHA256, up to 64 chars).
        source_type : str
            One of: session, file, stamp, manual.
        session_id : str, optional
            Associated session ID.
        metadata : dict, optional
            Additional metadata.

        Returns
        -------
        dict
            Server response with registered_at timestamp.
        """
        import json
        import urllib.request

        url = f"{self.base_url}/clew/register/"
        payload = {
            "hash": hash_value,
            "source_type": source_type,
            "session_id": session_id,
            "metadata": metadata or {},
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.warning("Clew Registry register failed: %s", e)
            return {"success": False, "error": str(e)}

    def verify(self, hash_value: str) -> Dict[str, Any]:
        """Verify a hash against the remote registry.

        Parameters
        ----------
        hash_value : str
            The hash to verify.

        Returns
        -------
        dict
            {registered: bool, registrations: [...]}
        """
        import json
        import urllib.request

        url = f"{self.base_url}/clew/verify/{hash_value}/"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.warning("Clew Registry verify failed: %s", e)
            return {"success": False, "registered": False, "error": str(e)}

    def register_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Register all hashes from a local session.

        Parameters
        ----------
        session_id : str
            Local session ID whose hashes to register.

        Returns
        -------
        list of dict
            Results for each hash registration.
        """
        db = get_db()
        file_hashes = db.get_file_hashes(session_id)
        run_info = db.get_run(session_id)

        results = []

        # Register combined hash if available
        if run_info and run_info.get("combined_hash"):
            result = self.register(
                run_info["combined_hash"],
                source_type="session",
                session_id=session_id,
                metadata={"type": "combined_hash"},
            )
            results.append(result)

        # Register individual file hashes
        for fh in file_hashes:
            result = self.register(
                fh["hash"],
                source_type="file",
                session_id=session_id,
                metadata={
                    "file_path": fh.get("file_path", ""),
                    "role": fh.get("role", ""),
                },
            )
            results.append(result)

        return results


_registry_instance: Optional[ClewRegistry] = None


def get_registry(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ClewRegistry:
    """Get or create the singleton registry client."""
    global _registry_instance
    if _registry_instance is None or base_url or api_key:
        _registry_instance = ClewRegistry(base_url=base_url, api_key=api_key)
    return _registry_instance


__all__ = ["ClewRegistry", "get_registry"]


# EOF
