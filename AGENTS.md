# AGENTS.md — freshrss_cli

## Purpose

`freshrss_cli` is a Python CLI tool for interacting with a FreshRSS instance via the Fever API. It is designed for:

1. **AI agent consumption** — OpenClaw morning digest workflow
2. **Direct use** — quick CLI for managing RSS feeds and articles

## Architecture (strict 3-layer)

```
config.py   →  credentials only (env vars > config file)
client.py   →  FreshRSS API operations, no CLI logic
main.py     →  Typer CLI entrypoint, no business logic
```

- `config.py`: Loads credentials. Never prints them. Used only by `main.py`.
- `client.py`: All API operations. Returns plain dicts. No `typer`, no `rich`.
- `main.py`: CLI surface only. Calls config + client, formats output with `rich`.

## Code Style

- Python 3.13+, full type hints
- No bare `except:` — always catch specific exceptions
- Never print, log, or return credentials
- Use `rich` for all terminal output in `main.py`
- Docstrings on all public functions

## Key Conventions

- Item IDs are strings in dicts (JSON-safe), but the API expects ints — convert at call sites
- `get_items()` returns unread items (Fever API limitation — no general item listing)
- `mark_unread()` uses a direct `_call()` workaround; may fail on some instances
- All client functions accept `FreshRSSAPI` as first arg (not `connect()` internally)

## Adding New Commands

1. Add a function to `client.py` (returns dict/list, no CLI logic)
2. Add a `@app.command()` to `main.py` (calls client, formats output)
3. **Update the QUICK REFERENCE docstring** at the top of `main.py`
4. Add an example to `README.md`

## Dependencies

| Package | Purpose |
|---|---|
| `freshrss-api` | FreshRSS Fever API client |
| `typer` | CLI framework |
| `rich` | Terminal formatting |
| `python-dotenv` | Config file loading |
| `loguru` | Required by freshrss-api internally |

## Config

- Config file: `~/.config/freshrss_cli/config.env` (chmod 600)
- Env vars: `FRESHRSS_URL`, `FRESHRSS_USERNAME`, `FRESHRSS_PASSWORD`
- Priority: env vars > config file
