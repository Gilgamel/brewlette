"""
Supabase Client Module
Handles connection to Supabase database for data persistence
"""
import os
import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Supabase credentials - can be set via environment variables or Streamlit secrets
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    # Try to get from Streamlit secrets first (for deployment)
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (for local development)
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase credentials not found. Please set them in "
            ".streamlit/secrets.toml or environment variables."
        )
    
    return create_client(supabase_url, supabase_key)


def init_database(client: Client):
    """Initialize database tables if they don't exist"""
    
    # Create capsules table
    client.table("capsules").execute()
    
    # Create users table
    client.table("users").execute()
    
    # Create inventory table
    client.table("inventory").execute()


def setup_database_schema(client: Client):
    """
    Set up the database schema.
    Run this once to create tables in Supabase.
    """
    
    # Create capsules table
    capsules_sql = """
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
    """
    
    # Create users table
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create inventory table
    inventory_sql = """
    CREATE TABLE IF NOT EXISTS inventory (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        pod_id INTEGER REFERENCES capsules(id),
        quantity INTEGER DEFAULT 0,
        UNIQUE(user_id, pod_id)
    );
    """
    
    # Note: These need to be run manually in Supabase dashboard
    # or via Supabase SQL editor
    print("Please run the SQL schema in Supabase dashboard:")
    print(capsules_sql)
    print(users_sql)
    print(inventory_sql)


# Capsule operations
def get_all_capsules(client: Client) -> list:
    """Get all capsules from database"""
    response = client.table("capsules").select("*").execute()
    return response.data


def get_capsule_by_id(client: Client, capsule_id: int) -> dict:
    """Get a single capsule by ID"""
    response = client.table("capsules").select("*").eq("id", capsule_id).execute()
    return response.data[0] if response.data else None


def save_capsules(client: Client, capsules: list) -> int:
    """Save or update capsules in database"""
    saved_count = 0
    for capsule in capsules:
        # Check if capsule exists
        existing = client.table("capsules").select("id").eq("name", capsule["name"]).execute()
        
        if existing.data:
            # Update existing
            client.table("capsules").update({
                "name_en": capsule.get("name_en"),
                "tasting_note": capsule.get("tasting_note"),
                "tasting_note_en": capsule.get("tasting_note_en"),
                "size_ml": capsule.get("size_ml"),
                "pod_type": capsule.get("pod_type"),
                "line": capsule.get("line"),
                "intensity": capsule.get("intensity"),
                "last_updated": datetime.now().isoformat()
            }).eq("name", capsule["name"]).execute()
        else:
            # Insert new
            client.table("capsules").insert({
                "name": capsule["name"],
                "name_en": capsule.get("name_en"),
                "tasting_note": capsule.get("tasting_note"),
                "tasting_note_en": capsule.get("tasting_note_en"),
                "size_ml": capsule.get("size_ml"),
                "pod_type": capsule.get("pod_type"),
                "line": capsule.get("line"),
                "intensity": capsule.get("intensity")
            }).execute()
        saved_count += 1
    return saved_count


# User operations
def create_user(client: Client, username: str) -> dict:
    """Create a new user"""
    # Check if user exists
    existing = client.table("users").select("*").eq("username", username).execute()
    
    if existing.data:
        return existing.data[0]
    
    response = client.table("users").insert({"username": username}).execute()
    return response.data[0] if response.data else None


def get_user_by_username(client: Client, username: str) -> dict:
    """Get user by username"""
    response = client.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None


def get_all_users(client: Client) -> list:
    """Get all users"""
    response = client.table("users").select("*").execute()
    return response.data


# Inventory operations
def get_user_inventory(client: Client, user_id: int) -> list:
    """Get user's inventory with capsule details"""
    response = client.table("inventory").select(
        "id, quantity, capsules(id, name, name_en, tasting_note, tasting_note_en, size_ml, pod_type, line, intensity)"
    ).eq("user_id", user_id).execute()
    return response.data


def add_to_inventory(client: Client, user_id: int, pod_id: int, quantity: int) -> bool:
    """Add or update inventory item"""
    # Check if item exists
    existing = client.table("inventory").select("*").eq("user_id", user_id).eq("pod_id", pod_id).execute()
    
    if existing.data:
        # Update quantity
        new_quantity = existing.data[0]["quantity"] + quantity
        client.table("inventory").update({"quantity": new_quantity}).eq("id", existing.data[0]["id"]).execute()
    else:
        # Insert new
        client.table("inventory").insert({
            "user_id": user_id,
            "pod_id": pod_id,
            "quantity": quantity
        }).execute()
    return True


def update_inventory_quantity(client: Client, inventory_id: int, quantity: int) -> bool:
    """Update inventory quantity"""
    if quantity <= 0:
        # Remove item if quantity is 0 or less
        client.table("inventory").delete().eq("id", inventory_id).execute()
    else:
        client.table("inventory").update({"quantity": quantity}).eq("id", inventory_id).execute()
    return True


def decrement_inventory(client: Client, inventory_id: int) -> bool:
    """Decrement inventory by 1"""
    # Get current quantity
    response = client.table("inventory").select("quantity").eq("id", inventory_id).execute()
    if not response.data:
        return False
    
    current_qty = response.data[0]["quantity"]
    new_qty = current_qty - 1
    
    return update_inventory_quantity(client, inventory_id, new_qty)


def remove_from_inventory(client: Client, inventory_id: int) -> bool:
    """Remove item from inventory"""
    client.table("inventory").delete().eq("id", inventory_id).execute()
    return True


def get_available_pods_for_user(client: Client, user_id: int, size_filter: str = None) -> list:
    """
    Get pods available for random selection (quantity > 0)
    Optionally filter by size
    """
    # Get inventory items with quantity > 0
    response = client.table("inventory").select(
        "id, quantity, capsules(id, name, name_en, tasting_note, tasting_note_en, size_ml, pod_type, line, intensity)"
    ).eq("user_id", user_id).gt("quantity", 0).execute()
    
    if not response.data:
        return []
    
    pods = response.data
    
    # Apply size filter if specified
    if size_filter:
        size_map = {
            "espresso": 40,
            "double": 80,
            "lungo": 150,
            "230": 230,
            "400": 400
        }
        target_size = size_map.get(size_filter.lower())
        if target_size:
            pods = [p for p in pods if p["capsules"]["size_ml"] == target_size]
    
    return pods


def remove_duplicate_capsules(client: Client) -> int:
    """Remove duplicate capsules, keeping the most recent one"""
    # Get all capsules
    all_capsules = client.table("capsules").select("id, name, line, size_ml, last_updated").execute()
    
    # Find duplicates (same name + line + size_ml)
    seen = {}
    duplicates = []
    
    for c in all_capsules.data:
        key = (c["name"], c.get("line"), c.get("size_ml"))
        if key in seen:
            # Keep the one with more recent last_updated
            existing = seen[key]
            existing_time = existing.get("last_updated", "") or ""
            new_time = c.get("last_updated", "") or ""
            if new_time > existing_time:
                duplicates.append(existing["id"])
                seen[key] = c
            else:
                duplicates.append(c["id"])
        else:
            seen[key] = c
    
    # Delete duplicates
    for dup_id in duplicates:
        client.table("capsules").delete().eq("id", dup_id).execute()
    
    return len(duplicates)


def clear_and_reset_capsules(client: Client, capsules: list) -> int:
    """Clear all capsules and re-import fresh data using batch insert"""
    try:
        # First delete all inventory (due to foreign key constraint)
        client.table("inventory").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"Error deleting inventory: {e}")
    
    try:
        # Then delete all existing capsules
        client.table("capsules").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"Error deleting capsules: {e}")
    
    # Prepare data for batch insert - remove duplicates first
    seen = set()
    insert_data = []
    for capsule in capsules:
        # Create unique key based on name, line, and size
        key = (capsule["name"], capsule.get("line"), capsule.get("size_ml"))
        if key not in seen:
            seen.add(key)
            insert_data.append({
                "name": capsule["name"],
                "name_en": capsule.get("name_en"),
                "tasting_note": capsule.get("tasting_note"),
                "tasting_note_en": capsule.get("tasting_note_en"),
                "size_ml": capsule.get("size_ml"),
                "pod_type": capsule.get("pod_type"),
                "line": capsule.get("line"),
                "intensity": capsule.get("intensity")
            })
    
    # Batch insert (Supabase allows up to 1000 rows per insert)
    if insert_data:
        # Insert in batches of 1000
        for i in range(0, len(insert_data), 1000):
            batch = insert_data[i:i+1000]
            client.table("capsules").insert(batch).execute()
    
    return len(insert_data)
