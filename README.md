# PatternProtect — MVP

Minimal MVP that adds buyer-specific watermark to PDF patterns, stores the watermarked file, and generates a delivery link.

## What this repo contains
- `app.py` — Streamlit app for upload -> watermark -> deliver flow
- `watermark/watermark.py` — PDF watermark engine
- `utils/email_sender.py` — SendGrid-based email delivery (fallback to console)
- `utils/tracker.py` — Simple CSV-based event logging
- `config.py` — Environment-configured settings
- `requirements.txt` — Python deps

## Quick start (local)
1. Create virtualenv and install deps:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
