---
name: freshrss
description: "Fetch news and RSS articles from FreshRSS via CLI for morning digest and news briefing. Use when the user asks for today's news, what's new in RSS feeds, morning briefing, or wants to read/save specific articles. Also use during morning heartbeat to generate a news summary. Credentials stored in ~/.config/freshrss_cli/config.env."
metadata:
  {"openclaw": {"emoji": "📰", "requires": {"bins": ["freshrss_cli"]}}}
---

# freshrss skill

CLI tool for FreshRSS RSS reader integration.

## Quick Reference

```bash
freshrss_cli feeds                          # List all feeds with unread counts
freshrss_cli items --unread --limit 20      # List unread articles
freshrss_cli items --feed ID                # Filter by feed ID
freshrss_cli items --output json            # JSON output for AI processing
freshrss_cli read UID [UID...]              # Mark as read
freshrss_cli unread UID [UID...]            # Mark as unread
freshrss_cli save UID [UID...]              # Save/star item(s)
freshrss_cli digest                         # Morning digest (top 20 unread)
freshrss_cli digest --output json           # Digest as JSON
freshrss_cli config                         # Show config status
freshrss_cli setup                          # Interactive setup wizard
```

## Morning Digest Workflow

```bash
# 1. Get digest as JSON
freshrss_cli digest --output json --limit 20

# 2. Summarize for the user (AI step — pick notable stories)

# 3. Mark summarized items as read
freshrss_cli read 111222333 444555666

# 4. Save anything worth revisiting
freshrss_cli save 777888999
```

## Filtering by Feed

```bash
# First, find feed IDs
freshrss_cli feeds

# Then filter items
freshrss_cli items --feed 42 --unread --limit 10
```

## Config

Credentials: `~/.config/freshrss_cli/config.env`

```env
FRESHRSS_URL=https://freshrss.example.com
FRESHRSS_USERNAME=youruser
FRESHRSS_PASSWORD=yourapipassword
```

Or set env vars: `FRESHRSS_URL`, `FRESHRSS_USERNAME`, `FRESHRSS_PASSWORD`

Run `freshrss_cli setup` for interactive wizard.
