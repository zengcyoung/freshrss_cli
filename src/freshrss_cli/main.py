"""freshrss_cli — FreshRSS CLI for OpenClaw AI assistant.

QUICK REFERENCE (for AI agents):
  freshrss_cli feeds                          List all feeds with unread counts
  freshrss_cli items [--feed ID] [--unread] [--limit N] [--output table|json]
                                              List articles/items
  freshrss_cli read UID [UID...]              Mark item(s) as read
  freshrss_cli unread UID [UID...]            Mark item(s) as unread
  freshrss_cli save UID [UID...]              Save/star item(s)
  freshrss_cli digest [--limit N] [--output text|json]
                                              Morning digest of top unread items
  freshrss_cli config                         Show config path and credential status
  freshrss_cli setup                          Interactive credential setup wizard

Credential env vars: FRESHRSS_URL, FRESHRSS_USERNAME, FRESHRSS_PASSWORD
Config file: ~/.config/freshrss_cli/config.env
"""

from __future__ import annotations

import json
import sys
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from freshrss_cli import client as rss_client
from freshrss_cli.config import CONFIG_FILE, credential_status, load_config

app = typer.Typer(
    name="freshrss_cli",
    help="FreshRSS CLI — fetch news and manage RSS articles.",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


def _get_client():
    """Load config and return connected API client."""
    try:
        url, username, password = load_config()
        return rss_client.connect(url, username, password)
    except RuntimeError as exc:
        err_console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def feeds() -> None:
    """List all feeds with name, URL, and unread count."""
    cli = _get_client()
    try:
        feed_list = rss_client.get_feeds(cli)
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    table = Table(title="FreshRSS Feeds", show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Unread", justify="right", style="cyan")
    table.add_column("URL", style="dim")

    for f in feed_list:
        table.add_row(f["id"], f["name"], str(f["unread_count"]), f["url"])

    console.print(table)


@app.command()
def items(
    feed: Annotated[Optional[str], typer.Option("--feed", help="Filter by feed ID")] = None,
    unread: Annotated[bool, typer.Option("--unread", help="Only show unread items")] = False,
    limit: Annotated[int, typer.Option("--limit", help="Max items to return")] = 20,
    output: Annotated[str, typer.Option("--output", help="Output format: table or json")] = "table",
) -> None:
    """List articles/items, optionally filtered by feed or unread status."""
    cli = _get_client()
    try:
        item_list = rss_client.get_items(cli, feed_id=feed, unread_only=unread, limit=limit)
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if output == "json":
        print(json.dumps(item_list, indent=2))
        return

    table = Table(title="Items", show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Feed", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Read", justify="center")
    table.add_column("URL", style="dim")

    for item in item_list:
        table.add_row(
            item["id"],
            item["feed_name"],
            item["title"],
            "✓" if item["is_read"] else "·",
            item["url"],
        )

    console.print(table)


@app.command(name="read")
def mark_read_cmd(
    uids: Annotated[list[str], typer.Argument(help="Item UID(s) to mark as read")],
) -> None:
    """Mark one or more items as read."""
    cli = _get_client()
    try:
        rss_client.mark_read(cli, uids)
        console.print(f"[green]Marked {len(uids)} item(s) as read.[/green]")
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command(name="unread")
def mark_unread_cmd(
    uids: Annotated[list[str], typer.Argument(help="Item UID(s) to mark as unread")],
) -> None:
    """Mark one or more items as unread."""
    cli = _get_client()
    try:
        rss_client.mark_unread(cli, uids)
        console.print(f"[green]Marked {len(uids)} item(s) as unread.[/green]")
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def save(
    uids: Annotated[list[str], typer.Argument(help="Item UID(s) to save/star")],
) -> None:
    """Save/star one or more items."""
    cli = _get_client()
    try:
        rss_client.save_item(cli, uids)
        console.print(f"[green]Saved {len(uids)} item(s).[/green]")
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def digest(
    limit: Annotated[int, typer.Option("--limit", help="Max items to include")] = 20,
    output: Annotated[str, typer.Option("--output", help="Output format: text or json")] = "text",
) -> None:
    """Fetch top unread items as a morning digest for AI consumption."""
    cli = _get_client()
    try:
        digest_items = rss_client.get_digest(cli, limit=limit)
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if output == "json":
        print(json.dumps(digest_items, indent=2))
        return

    console.print(f"[bold cyan]📰 Morning Digest — {len(digest_items)} unread items[/bold cyan]\n")
    for i, item in enumerate(digest_items, 1):
        console.print(f"[bold]{i}. {item['title']}[/bold]")
        console.print(f"   Feed: [cyan]{item['feed_name']}[/cyan]  |  ID: [dim]{item['id']}[/dim]")
        console.print(f"   URL: {item['url']}")
        if item["excerpt"]:
            console.print(f"   [dim]{item['excerpt']}[/dim]")
        console.print()


@app.command(name="config")
def config_cmd() -> None:
    """Show config file path and credential status (no secrets printed)."""
    status = credential_status()
    console.print(f"[bold]Config file:[/bold] {status['config_file']}")
    console.print(f"[bold]File exists:[/bold] {status['config_file_exists']}")
    console.print()
    console.print("[bold]Credential status:[/bold]")
    for key in ("FRESHRSS_URL", "FRESHRSS_USERNAME", "FRESHRSS_PASSWORD"):
        color = "green" if "✓" in status[key] else "red"
        console.print(f"  {key}: [{color}]{status[key]}[/{color}]")


@app.command()
def setup() -> None:
    """Interactive wizard to write ~/.config/freshrss_cli/config.env."""
    console.print("[bold cyan]FreshRSS CLI Setup Wizard[/bold cyan]")
    console.print(f"This will write credentials to: [bold]{CONFIG_FILE}[/bold]\n")

    url = typer.prompt("FreshRSS URL (e.g. https://freshrss.example.com)")
    username = typer.prompt("FreshRSS username")
    password = typer.prompt("FreshRSS API password", hide_input=True)

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        f"FRESHRSS_URL={url}\nFRESSHRSS_USERNAME={username}\nFRESSHRSS_PASSWORD={password}\n"
    )
    CONFIG_FILE.chmod(0o600)
    console.print(f"\n[green]✓ Credentials saved to {CONFIG_FILE}[/green]")
    console.print("Run [bold]freshrss_cli config[/bold] to verify.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
