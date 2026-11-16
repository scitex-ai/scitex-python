"""Invocation adapter for an installed owner's ordinary console launcher."""

import subprocess
import sys

import click

# Mirrors Python's generated console script, in a child so argparse/SystemExit
# and sys.argv remain the leaf's responsibility. This is never run by discovery.
_RUN = """
import importlib
import sys
module, attribute, program, *arguments = sys.argv[1:]
sys.argv = [program, *arguments]
command = importlib.import_module(module)
for part in attribute.split('.'):
    command = getattr(command, part)
sys.exit(command())
"""


def console_command(name, target, summary, console_script=None):
    """Build a Click view without invoking the metadata-qualified launcher."""
    module, _, attribute = target.partition(":")

    @click.pass_context
    def invoke(ctx):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                _RUN,
                module,
                attribute,
                console_script or name,
                *ctx.args,
            ],
            check=False,
        )
        ctx.exit(
            result.returncode if result.returncode >= 0 else 128 - result.returncode
        )

    return click.Command(
        name,
        callback=invoke,
        help=summary,
        add_help_option=False,
        context_settings={
            "ignore_unknown_options": True,
            "allow_extra_args": True,
            "allow_interspersed_args": False,
        },
    )
