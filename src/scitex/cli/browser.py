#!/usr/bin/env python3
"""
SciTeX Browser Commands - Browser automation utilities with session management

Stealth mode uses Xvfb (X Virtual Framebuffer) - browser runs with GUI
but on a virtual display that user doesn't see.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import click

# Browser session storage
BROWSER_STATE_FILE = Path.home() / ".scitex" / "browser" / "sessions.json"
XVFB_DISPLAY = ":99"


def _ensure_xvfb_running():
    """Ensure Xvfb is running on virtual display."""
    # Check if Xvfb is already running on :99
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"Xvfb {XVFB_DISPLAY}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True  # Already running
    except Exception:
        pass

    # Start Xvfb
    try:
        subprocess.Popen(
            ["Xvfb", XVFB_DISPLAY, "-screen", "0", "1920x1080x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import time

        time.sleep(0.5)  # Wait for Xvfb to start
        return True
    except FileNotFoundError:
        click.echo("Warning: Xvfb not found. Install with: sudo apt install xvfb")
        return False


def _load_sessions():
    """Load browser session state."""
    if BROWSER_STATE_FILE.exists():
        return json.loads(BROWSER_STATE_FILE.read_text())
    return {}


def _save_sessions(sessions):
    """Save browser session state."""
    BROWSER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BROWSER_STATE_FILE.write_text(json.dumps(sessions, indent=2))


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def browser(ctx, as_json):
    """
    Browser automation utilities

    \b
    Launch and control Chrome browsers:
    - Interactive mode: Visible browser for user interaction
    - Stealth mode: Headless browser for automation
    - Switch modes dynamically with show/hide commands

    \b
    Examples:
        scitex browser open                    # Open interactive browser
        scitex browser open --stealth          # Open headless browser
        scitex browser show <id>               # Make browser visible
        scitex browser hide <id>               # Make browser headless
        scitex browser list                    # List active browsers
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, browser)
        else:
            click.echo(ctx.get_help())


@browser.command()
@click.argument("url", default="about:blank", required=False)
@click.option("--stealth", is_flag=True, help="Use stealth/headless mode")
@click.option(
    "--timeout", type=int, default=0, help="Auto-close after N seconds (0=manual close)"
)
@click.option("--background", "-b", is_flag=True, help="Run in background, return ID")
def open(url, stealth, timeout, background):
    """
    Open a Chrome browser

    \b
    Examples:
        scitex browser open                           # Open blank page
        scitex browser open google.com                # Open URL
        scitex browser open https://google.com        # Open URL (with scheme)
        scitex browser open google.com --stealth      # Headless mode
    """
    # Add https:// if no scheme provided
    if url != "about:blank" and not url.startswith(("http://", "https://", "about:")):
        url = f"https://{url}"
    from playwright.async_api import async_playwright

    from scitex.browser.core import BrowserMixin

    class SimpleBrowser(BrowserMixin):
        pass

    use_virtual_display = stealth
    original_display = os.environ.get("DISPLAY", ":0")

    # Setup Xvfb for stealth mode
    if use_virtual_display:
        if not _ensure_xvfb_running():
            click.echo("Falling back to visible mode")
            use_virtual_display = False
        else:
            os.environ["DISPLAY"] = XVFB_DISPLAY

    async def run():
        nonlocal use_virtual_display

        # Always launch with GUI (mode=interactive), display controls visibility
        browser_instance = SimpleBrowser(mode="interactive")

        pw = await async_playwright().start()
        browser_obj, context = await browser_instance.create_browser_context_async(pw)
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # Store references for mode switching
        browser_instance._playwright = pw
        browser_instance._browser = browser_obj
        browser_instance.contexts = [context]
        browser_instance.pages = [page]

        # Generate browser ID
        import uuid

        browser_id = str(uuid.uuid4())[:8]

        # Show browser ID in the page title
        await page.evaluate(
            f"""
            document.title = '[{browser_id}] ' + document.title;
        """
        )

        click.echo(f"Browser ID: {browser_id}")
        click.echo(
            f"Display: {XVFB_DISPLAY if use_virtual_display else original_display}"
        )
        click.echo(f"URL: {url}")

        if background:
            # Save session info
            sessions = _load_sessions()
            sessions[browser_id] = {
                "display": XVFB_DISPLAY if use_virtual_display else original_display,
                "url": url,
                "pid": None,  # Would need process management for true background
            }
            _save_sessions(sessions)
            click.echo(f"Use 'scitex browser show {browser_id}' to make visible")
            click.echo(f"Use 'scitex browser hide {browser_id}' to make headless")
            return browser_id

        click.echo("Commands: 's'=show, 'h'=hide, 'q'=quit")

        async def switch_display(to_virtual: bool):
            """Switch browser between real and virtual display."""
            nonlocal pw, browser_obj, context, page, use_virtual_display

            if to_virtual == use_virtual_display:
                return  # Already on target display

            # Ensure Xvfb is running for virtual display
            if to_virtual and not _ensure_xvfb_running():
                click.echo("Cannot switch: Xvfb not available")
                return

            # Get current URL and cookies
            current_url = page.url
            cookies = await context.cookies()

            # Close EVERYTHING - browser and playwright
            await browser_instance.close_all_pages()
            await browser_obj.close()
            await pw.stop()

            # Switch display BEFORE restarting playwright
            os.environ["DISPLAY"] = XVFB_DISPLAY if to_virtual else original_display
            use_virtual_display = to_virtual

            # Restart playwright with new display
            pw = await async_playwright().start()
            browser_obj, context = await browser_instance.create_browser_context_async(
                pw
            )
            await context.add_cookies(cookies)
            page = await context.new_page()
            await page.goto(current_url, wait_until="domcontentloaded")

            # Update references
            browser_instance._playwright = pw
            browser_instance._browser = browser_obj
            browser_instance.contexts = [context]
            browser_instance.pages = [page]

            # Restore browser ID in title
            await page.evaluate(
                f"""
                document.title = '[{browser_id}] ' + document.title;
            """
            )

        if timeout > 0:
            click.echo(f"Auto-closing in {timeout} seconds...")
            await asyncio.sleep(timeout)
        else:
            # Interactive control loop
            import select
            import sys as _sys

            try:
                while True:
                    # Check for keyboard input (non-blocking on Unix)
                    if select.select([_sys.stdin], [], [], 0.5)[0]:
                        cmd = _sys.stdin.readline().strip().lower()
                        if cmd == "s":
                            await switch_display(to_virtual=False)
                            click.echo(f"Browser: visible ({original_display})")
                        elif cmd == "h":
                            await switch_display(to_virtual=True)
                            click.echo(f"Browser: hidden ({XVFB_DISPLAY})")
                        elif cmd == "q":
                            break
                    await asyncio.sleep(0.1)
            except (KeyboardInterrupt, EOFError):
                pass

        await browser_instance.close_all_pages()
        await browser_obj.close()
        await pw.stop()
        click.echo("Browser closed")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        click.echo("\nBrowser closed")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@browser.command()
def list():
    """List browser sessions."""
    sessions = _load_sessions()
    if not sessions:
        click.echo("No browser sessions found")
        return

    click.echo("Browser Sessions:")
    for bid, info in sessions.items():
        click.echo(f"  {bid}: mode={info.get('mode', '?')}, url={info.get('url', '?')}")


@browser.command()
@click.argument("browser_id", required=False)
def show(browser_id):
    """
    Switch browser to visible/interactive mode

    \b
    For running browser, enter 's' in terminal.
    For background browser, use: scitex browser show <id>
    """
    if not browser_id:
        click.echo("For running browser: type 's' + Enter")
        click.echo("For background: scitex browser show <browser_id>")
        return

    click.echo("Note: Background browser control requires process management.")
    click.echo("For running browser, type 's' + Enter in browser terminal.")


@browser.command()
@click.argument("browser_id", required=False)
def hide(browser_id):
    """
    Switch browser to headless/stealth mode

    \b
    For running browser, enter 'h' in terminal.
    For background browser, use: scitex browser hide <id>
    """
    if not browser_id:
        click.echo("For running browser: type 'h' + Enter")
        click.echo("For background: scitex browser hide <browser_id>")
        return

    click.echo("Note: Background browser control requires process management.")
    click.echo("For running browser, type 'h' + Enter in browser terminal.")


# EOF
