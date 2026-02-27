# Nespresso Pod Picker ☕

A Streamlit web application for randomly selecting Nespresso capsules based on your preferences and inventory.

## Features

- 🎲 Random capsule selection based on your preferences
- 📦 Inventory management (add, update, delete capsules)
- 🌐 Chinese/English language support
- 📱 Mobile-friendly design
- 🔄 Update capsule data from Nespresso website
- 👥 Multi-user support

## Requirements

- Python 3.8+
- Streamlit
- Supabase account (free)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Supabase Setup

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to SQL Editor and run the following SQL:

```sql
-- Create capsules table
CREATE TABLE IF NOT EXISTS capsules (
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

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pod_id INTEGER REFERENCES capsules(id),
    quantity INTEGER DEFAULT 0,
    UNIQUE(user_id, pod_id)
);
```

4. Get your Supabase URL and anon key from Settings → API
5. Update `.streamlit/secrets.toml` with your credentials

## Running Locally

```bash
streamlit run main.py
```

## Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your Supabase credentials in Streamlit Cloud settings
5. Deploy!

## Usage

1. **Create a user**: Enter your username and click "Create"
2. **Add capsules**: Go to "My Inventory" tab, select capsules and add quantity
3. **Random pick**: Go to "Random Pick" tab, select your preference (optional), and click the button!
4. **Confirm**: After confirming, the quantity will decrease by 1

## Project Structure

```
nespresso-pod-app/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── supabase_client.py  # Supabase database operations
│   ├── scraper.py          # Nespresso data scraper
│   └── translator.py       # Language translations
├── .streamlit/
│   ├── config.toml         # Streamlit configuration
│   └── secrets.toml       # API credentials (don't commit!)
└── README.md
```

## License

MIT License
