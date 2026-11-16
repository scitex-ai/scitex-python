#!/usr/bin/env python3
"""Shared helpers for introspect CLI commands."""

import sys

import click


def command_help(summary, example):
    """Use the shared CLI help contract for each introspection capability."""
    from scitex_dev.ecosystem import CliHelp, Example, SpecCommand

    return {
        "cls": SpecCommand,
        "help_spec": CliHelp(
            summary=summary,
            examples=(
                Example("{prog} " + example, "Return a structured JSON result."),
            ),
        ),
    }


def echo_json_result(data):
    """Emit a Result-envelope JSON success response and return."""
    from scitex_dev import Result

    click.echo(Result(success=True, data=data).to_json())


def echo_json_error(error_msg):
    """Emit a Result-envelope JSON error response and exit."""
    from scitex_dev import Result

    click.echo(Result(success=False, error=error_msg).to_json())
    sys.exit(1)
