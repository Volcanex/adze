# Docs Guide

This directory is the **single source of truth** for Adze Studio documentation.

## Files

| File | Audience | Purpose |
|------|----------|---------|
| `00-behaviour.md` | AI only | Vibe Coder tone, rules, sandboxing |
| `01-architecture.md` | AI + devs | How Adze works end-to-end |
| `02-site-format.md` | AI + artists | content.md format, pages, config, api.py |
| `03-api.md` | AI + devs | Full API endpoint reference |
| `04-widgets.md` | AI + devs | Widget development guide |

## How the system prompt works

`_get_artist_system_prompt()` in `admin_api.py` reads all `*.md` files from this directory in filename order, concatenates them, then appends runtime context (artist slug, pages, config, etc.).

**To update AI behaviour or docs: edit the files in this directory. That's it.**

The `/docs` route in `admin_api.py` renders these same files as a web page, available at `https://adze.studio/docs` (no login required).

## Adding a new doc file

Name it `NN-name.md` where `NN` keeps it in the right order. It will be automatically included in the system prompt and rendered at `/docs`.
