# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nespresso Pod Picker is a Streamlit web application for randomly selecting Nespresso coffee capsules based on user preferences and inventory tracking. Supports both Original Line and Vertuo Line capsules with Chinese/English language toggle.

## Running the Application

```bash
streamlit run main.py
```

The app runs on port 8501 by default (configured in `.streamlit/config.toml`).

## Dependencies

```
streamlit>=1.28.0
supabase>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pandas>=2.0.0
```

Install with: `pip install -r requirements.txt`

## Architecture

### Core Components

- **main.py** - Streamlit UI with tabs: Random Pick, My Inventory, Admin Panel
- **src/supabase_client.py** - Database operations (capsules, users, inventory tables)
- **src/scraper.py** - Web scraping for Nespresso data + fallback sample data
- **src/translator.py** - i18n for Chinese/English

### Database Schema (Supabase)

Three tables: `capsules` (master pod data), `users` (multi-user support), `inventory` (user pod quantities). SQL schema provided in README.md.

### Key Features

- Random capsule selection filtered by size (40ml espresso, 80ml double, 150ml lungo, 230ml coffee)
- Multi-user inventory management with quantity tracking
- Admin panel to scrape/update capsule data from Nespresso Canada website
- Language toggle between English and Chinese

## Configuration

Supabase credentials must be set in `.streamlit/secrets.toml`:
```toml
[supabase]
url = "your-supabase-url"
key = "your-anon-key"
```

Or via environment variables: `SUPABASE_URL` and `SUPABASE_KEY`.
