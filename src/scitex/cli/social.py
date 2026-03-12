#!/usr/bin/env python3
# Timestamp: 2026-01-22
# File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/social.py

"""
SciTeX CLI - Social Media Commands

Thin wrapper around socialia CLI with SCITEX_ environment variable prefix.
All commands delegate to socialia for reproducibility.
"""

import subprocess
import sys

import click


def _run_socialia(*args, json_output: bool = False) -> int:
    """Run socialia CLI command."""
    cmd = [sys.executable, "-m", "socialia"]
    if json_output:
        cmd.append("--json")
    cmd.extend(args)

    result = subprocess.run(cmd)
    return result.returncode


def _check_socialia() -> bool:
    """Check if socialia is available."""
    try:
        import socialia  # noqa: F401

        return True
    except ImportError:
        return False


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def social(ctx, help_recursive, as_json):
    """
    Social media management (powered by socialia)

    \b
    Platforms:
      twitter   - Twitter/X posting and management
      linkedin  - LinkedIn posting
      reddit    - Reddit posting
      youtube   - YouTube video uploads

    \b
    Examples:
      scitex social post twitter "Hello from SciTeX!"
      scitex social post linkedin "Research update"
      scitex social status
      scitex social analytics twitter

    \b
    Environment Variables (SCITEX_SOCIAL_ prefix):
      SCITEX_SOCIAL_X_CONSUMER_KEY          Twitter API keys
      SCITEX_SOCIAL_LINKEDIN_ACCESS_TOKEN   LinkedIn OAuth token
      SCITEX_SOCIAL_REDDIT_CLIENT_ID        Reddit app credentials
      SCITEX_SOCIAL_YOUTUBE_API_KEY         YouTube API key

    Note: Falls back to SOCIALIA_ prefix if SCITEX_SOCIAL_ not set.
    """
    if not _check_socialia():
        click.secho("Error: socialia not installed", fg="red", err=True)
        click.echo("\nInstall with: pip install socialia")
        ctx.exit(1)

    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, social)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, social)
        else:
            click.echo(ctx.get_help())


@social.command()
@click.argument(
    "platform", type=click.Choice(["twitter", "linkedin", "reddit", "youtube"])
)
@click.argument("text", required=False)
@click.option(
    "-f", "--file", type=click.Path(exists=True), help="Read content from file"
)
@click.option("--reply-to", help="Post ID to reply to (Twitter)")
@click.option("--quote", help="Post ID to quote (Twitter)")
@click.option("-s", "--subreddit", default="test", help="Target subreddit (Reddit)")
@click.option("-t", "--title", help="Post title (Reddit/YouTube)")
@click.option("--dry-run", is_flag=True, help="Preview without posting")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def post(platform, text, file, reply_to, quote, subreddit, title, dry_run, as_json):
    """
    Post content to a social platform

    \b
    Examples:
      scitex social post twitter "Hello world!"
      scitex social post twitter --file tweet.txt
      scitex social post reddit "Check this out" -s python -t "Cool project"
      scitex social post linkedin "Professional update"
      scitex social post twitter "Test" --dry-run
    """
    args = ["post", platform]

    if text:
        args.append(text)
    if file:
        args.extend(["--file", file])
    if reply_to:
        args.extend(["--reply-to", reply_to])
    if quote:
        args.extend(["--quote", quote])
    if subreddit and platform == "reddit":
        args.extend(["--subreddit", subreddit])
    if title:
        args.extend(["--title", title])
    if dry_run:
        args.append("--dry-run")

    sys.exit(_run_socialia(*args, json_output=as_json))


@social.command()
@click.argument("platform", type=click.Choice(["twitter", "linkedin", "reddit"]))
@click.argument("post_id")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be deleted without deleting"
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def delete(platform, post_id, dry_run, as_json):
    """
    Delete a post from a platform

    \b
    Examples:
      scitex social delete twitter 1234567890
      scitex social delete reddit abc123
      scitex social delete twitter 1234567890 --dry-run
    """
    if dry_run:
        click.echo(f"[dry-run] Would delete post {post_id} from {platform}")
        sys.exit(0)
    sys.exit(_run_socialia("delete", platform, post_id, json_output=as_json))


@social.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status(as_json):
    """
    Check configuration and authentication status

    \b
    Example:
      scitex social status
      scitex social status --json
    """
    sys.exit(_run_socialia("status", json_output=as_json))


@social.command()
@click.argument(
    "platform",
    type=click.Choice(["twitter", "linkedin", "reddit", "youtube"]),
    required=False,
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def check(platform, as_json):
    """
    Check platform connection status.

    \b
    Examples:
      scitex social check              # Check all platforms
      scitex social check twitter      # Check specific platform
    """
    args = ["check"]
    if platform:
        args.append(platform)
    sys.exit(_run_socialia(*args, json_output=as_json))


@social.command()
@click.argument(
    "platform",
    type=click.Choice(["twitter", "linkedin", "reddit"]),
    required=False,
)
@click.option("--limit", "-l", type=int, default=10, help="Number of posts to fetch")
@click.option("--mentions", is_flag=True, help="Get mentions/notifications instead")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def feed(platform, limit, mentions, as_json):
    """
    Get recent posts from platform feeds.

    \b
    Examples:
      scitex social feed                    # All platforms
      scitex social feed twitter --limit 5  # Specific platform
      scitex social feed --mentions         # Get mentions
    """
    args = ["feed"]
    if platform:
        args.append(platform)
    args.extend(["--limit", str(limit)])
    if mentions:
        args.append("--mentions")
    sys.exit(_run_socialia(*args, json_output=as_json))


@social.command()
@click.argument("platform", type=click.Choice(["twitter", "linkedin", "reddit"]))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def me(platform, as_json):
    """
    Get user profile information.

    \b
    Examples:
      scitex social me twitter
      scitex social me linkedin --json
    """
    sys.exit(_run_socialia("me", platform, json_output=as_json))


@social.command()
@click.argument("platform", type=click.Choice(["twitter", "youtube", "ga"]))
@click.option("--days", "-d", type=int, default=7, help="Number of days to analyze")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def analytics(platform, days, as_json):
    """
    Get analytics for a platform

    \b
    Platforms:
      twitter  - Tweet engagement metrics
      youtube  - Channel and video statistics
      ga       - Google Analytics reports

    \b
    Examples:
      scitex social analytics twitter
      scitex social analytics youtube --days 30
      scitex social analytics ga --json
    """
    args = ["analytics", platform, "--days", str(days)]
    sys.exit(_run_socialia(*args, json_output=as_json))


@social.command()
@click.argument("platform", type=click.Choice(["twitter"]))
@click.option(
    "-f", "--file", type=click.Path(exists=True), required=True, help="Thread file"
)
@click.option("--delay", type=int, default=2, help="Delay between posts (seconds)")
@click.option("--dry-run", is_flag=True, help="Preview without posting")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def thread(platform, file, delay, dry_run, as_json):
    """
    Post a thread (multiple connected posts)

    \b
    Thread file format (--- separates posts):
      First tweet in the thread
      ---
      Second tweet, replying to first
      ---
      Third tweet, and so on...

    \b
    Example:
      scitex social thread twitter --file thread.txt
      scitex social thread twitter --file thread.txt --dry-run
    """
    args = ["thread", platform, "--file", file, "--delay", str(delay)]
    if dry_run:
        args.append("--dry-run")
    sys.exit(_run_socialia(*args, json_output=as_json))


@social.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def mcp(ctx, as_json):
    """
    MCP (Model Context Protocol) server operations

    \b
    Commands:
      start        - Start the MCP server
      doctor       - Check MCP server health
      list-tools   - List available MCP tools
      installation - Show Claude Desktop configuration

    \b
    Examples:
      scitex social mcp start
      scitex social mcp doctor
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, mcp)
        else:
            click.echo(ctx.get_help())


@mcp.command()
def start():
    """
    Start the MCP server

    \b
    Example:
      scitex social mcp start
    """
    sys.exit(_run_socialia("mcp", "start"))


@mcp.command()
def doctor():
    """
    Check MCP server health

    \b
    Example:
      scitex social mcp doctor
    """
    sys.exit(_run_socialia("mcp", "doctor"))


@mcp.command("list-tools")
def list_tools():
    """
    List available MCP tools

    \b
    Example:
      scitex social mcp list-tools
    """
    sys.exit(_run_socialia("mcp", "list-tools"))


@mcp.command()
def installation():
    """
    Show Claude Desktop configuration

    \b
    Example:
      scitex social mcp installation
    """
    sys.exit(_run_socialia("mcp", "installation"))


if __name__ == "__main__":
    social()

# EOF
