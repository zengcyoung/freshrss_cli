# freshrss_cli

FreshRSS CLI for OpenClaw AI assistant — fetch news, manage RSS articles, and generate morning digests.

## Purpose

A command-line tool for interacting with a [FreshRSS](https://freshrss.github.io/) instance via the Fever API. Designed for AI agent consumption (OpenClaw morning news digest) as well as direct use.

## Installation

```bash
# Clone and install
git clone https://github.com/zengcyoung/freshrss_cli.git ~/freshrss_cli
cd ~/freshrss_cli
~/.asdf/shims/uv sync

# Symlink to PATH
ln -sf ~/freshrss_cli/.venv/bin/freshrss_cli ~/.local/bin/freshrss_cli
```

## Configuration

Three options (highest priority first):

### 1. Interactive wizard (recommended)
```bash
freshrss_cli setup
```

### 2. Manual config file
Create `~/.config/freshrss_cli/config.env` (chmod 600):
```env
FRESHRSS_URL=https://freshrss.example.com
FRESHRSS_USERNAME=youruser
FRESHRSS_PASSWORD=yourapipassword
```

### 3. Environment variables
```bash
export FRESHRSS_URL=https://freshrss.example.com
export FRESHRSS_USERNAME=youruser
export FRESHRSS_PASSWORD=yourapipassword
```

> **Note:** The password should be the FreshRSS API/Fever password, not your login password. Generate it in FreshRSS under Profile → API Password.

## Commands

```bash
# List all feeds with unread counts
freshrss_cli feeds

# List recent unread articles
freshrss_cli items --unread --limit 10

# List articles from a specific feed
freshrss_cli items --feed 42

# List articles as JSON (for AI consumption)
freshrss_cli items --unread --output json

# Mark articles as read
freshrss_cli read 123456789 987654321

# Mark articles as unread
freshrss_cli unread 123456789

# Save/star articles
freshrss_cli save 123456789

# Morning digest (top 20 unread, AI-friendly format)
freshrss_cli digest

# Morning digest as JSON
freshrss_cli digest --output json --limit 30

# Show config status
freshrss_cli config

# Setup wizard
freshrss_cli setup
```

## AI Agent Usage

This tool is designed for OpenClaw's morning heartbeat workflow:

```bash
# 1. Get digest as JSON for AI processing
freshrss_cli digest --output json --limit 20

# 2. After AI summarizes, mark items read
freshrss_cli read 111 222 333

# 3. Save interesting items
freshrss_cli save 444
```

## Notes

- Built on the [freshrss-api](https://pypi.org/project/freshrss-api/) Fever API client
- Requires FreshRSS with Fever API enabled (Settings → Authentication → Allow API access)
- The `unread` command may not work on all FreshRSS versions due to Fever API limitations
