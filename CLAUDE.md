# CLAUDE.md

Project instructions for Claude Code.

## Project Overview

Nespresso Pod Picker - A PWA (Progressive Web App) for randomly selecting Nespresso coffee capsules with inventory management.

## Running Locally

```bash
# Option 1: Python simple server
cd web
python -m http.server 8000
# Then open http://localhost:8000

# Option 2: VS Code Live Server
# Right-click index.html > Open with Live Server
```

## Deployment

### Vercel (Recommended for Supabase integration)
1. Push code to GitHub
2. Go to https://vercel.com
3. Import the repository
4. Deploy

### Netlify
1. Push code to GitHub
2. Go to https://netlify.com
3. Drag and drop the `web` folder
4. Or connect to GitHub for automatic deploys

### GitHub Pages
1. Push `web/` folder contents to a GitHub repository
2. Go to Settings > Pages
3. Enable GitHub Pages

## Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Run the following SQL in Supabase SQL Editor:

```sql
-- Capsules table
CREATE TABLE capsules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    tasting_note TEXT,
    tasting_note_en TEXT,
    size_ml INTEGER,
    pod_type VARCHAR(50),
    line VARCHAR(50),
    intensity INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory table
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pod_id INTEGER REFERENCES capsules(id),
    quantity INTEGER DEFAULT 0,
    UNIQUE(user_id, pod_id)
);

-- Enable RLS (optional)
ALTER TABLE capsules ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public read capsules" ON capsules FOR SELECT USING (true);
CREATE POLICY "Public read users" ON users FOR SELECT USING (true);
CREATE POLICY "Public read inventory" ON inventory FOR SELECT USING (true);

-- Allow authenticated insert/update
CREATE POLICY "Authenticated insert users" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Authenticated insert inventory" ON inventory FOR INSERT WITH CHECK (true);
CREATE POLICY "Authenticated update inventory" ON inventory FOR UPDATE USING (true);
CREATE POLICY "Authenticated delete inventory" ON inventory FOR DELETE USING (true);

-- Daily consumption tracking table (prevents Supabase pause)
CREATE TABLE daily_consumption (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pod_id INTEGER REFERENCES capsules(id),
    consumption_date DATE NOT NULL DEFAULT CURRENT_DATE,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, pod_id, consumption_date)
);

-- Enable RLS
ALTER TABLE daily_consumption ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public read daily_consumption" ON daily_consumption FOR SELECT USING (true);

-- Allow authenticated insert
CREATE POLICY "Authenticated insert daily_consumption" ON daily_consumption FOR INSERT WITH CHECK (true);

-- Allow public insert (for guest users)
CREATE POLICY "Public insert daily_consumption" ON daily_consumption FOR INSERT WITH CHECK (true);
```

3. Copy the Supabase URL and anon key
4. Edit `web/supabase.js` and replace the credentials

## Project Structure

```
brewlette/
├── web/                 # PWA application
│   ├── index.html       # Main HTML
│   ├── app.js           # App logic
│   ├── supabase.js      # Supabase client
│   ├── styles.css       # Styles
│   ├── sw.js            # Service worker (PWA)
│   ├── manifest.json    # PWA manifest
│   └── data/
│       └── capsules.json # Local capsule data (fallback)
├── data/                # Data files
│   └── capsules.json
├── src/                 # Source modules (for reference)
│   ├── scraper.py
│   ├── supabase_client.py
│   └── translator.py
└── CLAUDE.md
```

## Features

- Random capsule selection filtered by size
- Multi-user inventory management
- Chinese/English language toggle
- PWA - installable on mobile/desktop
- Works offline with local data fallback

## Tech Stack

- Vanilla JavaScript (no framework)
- Supabase (backend/database)
- PWA (Service Worker + Manifest)
