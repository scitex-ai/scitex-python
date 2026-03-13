#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: src/scitex/cli/scholar/_utils.py
# ----------------------------------------

"""Shared utilities for Scholar CLI commands."""

from __future__ import annotations

import click
from scitex_dev import Result


def output_json(data: dict) -> None:
    """Output data as a Result envelope JSON.

    Extracts ``success``, ``error``, and ``error_code`` from *data*
    and wraps the remaining keys under ``Result.data``.
    """
    success = data.get("success", True)
    error = data.get("error")
    error_code = data.get("error_code")

    payload = {
        k: v for k, v in data.items() if k not in ("success", "error", "error_code")
    }

    envelope = Result(
        success=success,
        data=payload if payload else None,
        error=error,
        error_code=error_code,
    )
    click.echo(envelope.to_json())


def output_error(exception: Exception) -> None:
    """Output an exception as a Result error envelope JSON."""
    from scitex_dev import classify_exception

    ec = classify_exception(exception)
    envelope = Result(
        success=False,
        error=str(exception),
        error_code=ec.value,
    )
    click.echo(envelope.to_json())


def output_result(data: dict, json_mode: bool) -> None:
    """Output result in appropriate format."""
    from scitex import logging

    logger = logging.getLogger(__name__)

    if json_mode:
        output_json(data)
    else:
        if data.get("success"):
            logger.success(data.get("message", "Success"))
        else:
            logger.error(data.get("error", "Failed"))


# EOF
