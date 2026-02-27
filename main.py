"""
Nespresso Pod Picker - Main Application
A Streamlit web app for randomly selecting Nespresso pods
"""
import streamlit as st
import random

from src.supabase_client import (
    get_supabase_client,
    get_all_capsules,
    get_all_users,
    create_user,
    get_user_by_username,
    get_user_inventory,
    add_to_inventory,
    update_inventory_quantity,
    decrement_inventory,
    remove_from_inventory,
    get_available_pods_for_user,
    save_capsules,
    remove_duplicate_capsules
)
from src.scraper import scrape_all_capsules, get_sample_capsules
from src.translator import get_text, translate_capsule

# Page configuration
st.set_page_config(
    page_title="Nespresso Pod Picker",
    page_icon="☕",
    layout="wide"
)

# Custom CSS - Morandi Color Style
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif');
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
    }
    
    /* Morandi Color Palette */
    :root {
        --m-bg: #f5f3f0;
        --m-card: #ffffff;
        --m-text: #5a5a5a;
        --m-text-light: #9a9a9a;
        --m-accent: #8b9dc3;
        --m-accent-dark: #6b7aa3;
        --m-green: #a8b5a0;
        --m-pink: #d4b8b0;
        --m-cream: #e8e0d5;
        --m-lavender: #b8a9c9;
    }
    
    .stApp {
        background: var(--m-bg);
        color: var(--m-text);
    }
    
    /* Center the main content */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 680px;
        margin: 0 auto;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        font-weight: 500;
        color: var(--m-text);
    }
    
    h3 {
        font-size: 20px;
    }
    
    /* Center content */
    .stMarkdown {
        text-align: center;
    }
    
    /* Buttons - Morandi style */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 14px 20px;
        background: var(--m-card);
        border: 1px solid var(--m-cream);
        color: var(--m-text);
        font-weight: 400;
        font-size: 16px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .stButton > button:hover {
        background: var(--m-cream);
        border-color: #d8d4cd;
    }
    
    .stButton > button:active {
        background: var(--m-cream);
        transform: scale(0.99);
    }
    
    /* Primary action button - Morandi accent */
    .primary-btn > button {
        background: var(--m-accent) !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .primary-btn > button:hover {
        background: var(--m-accent-dark) !important;
    }
    
    /* Inputs - Morandi style */
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: var(--m-card);
        border-radius: 12px;
        border: 1px solid var(--m-cream);
        color: var(--m-text);
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .stTextInput > div > div {
        background: var(--m-card);
        border-radius: 12px;
        border: 1px solid var(--m-cream);
        color: var(--m-text);
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: transparent !important;
        color: var(--m-text) !important;
    }
    
    /* Tabs - Morandi style */
    div[data-testid="stTabs"] {
        background: var(--m-card);
        border-radius: 14px;
        padding: 6px;
    }
    
    div[data-testid="stTabs"] button {
        background: transparent;
        color: var(--m-text-light);
        border-radius: 10px;
        font-weight: 400;
        font-size: 13px;
        padding: 10px 18px;
    }
    
    div[data-testid="stTabs"] button[data-selected="true"] {
        background: var(--m-accent);
        color: #ffffff;
    }
    
    /* Cards */
    .stExpander > div {
        background: var(--m-card);
        border-radius: 14px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    /* Result Box - Morandi style */
    .result-box {
        background: var(--m-card);
        padding: 32px;
        border-radius: 18px;
        text-align: center;
        margin: 24px 0;
        border: none;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    }
    
    .result-box h2 {
        color: var(--m-text);
        font-size: 26px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .result-box .tasting {
        color: var(--m-text-light);
        font-size: 14px;
        margin-bottom: 12px;
    }
    
    .result-box .details {
        color: var(--m-text-light);
        font-size: 13px;
    }
    
    .result-box .remaining {
        color: var(--m-text);
        font-size: 15px;
        font-weight: 400;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--m-cream);
    }
    
    /* Radio buttons - Morandi style */
    div[data-testid="stRadio"] > div {
        background: var(--m-card);
        border-radius: 12px;
        padding: 6px;
    }
    
    div[data-testid="stRadio"] label {
        background: transparent;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 13px;
        color: var(--m-text);
    }
    
    div[data-testid="stRadio"] label:has(input:checked) {
        background: var(--m-accent);
        color: white;
    }
    
    /* Alerts - Morandi style */
    .stAlert {
        background: var(--m-card);
        border-radius: 12px;
        border: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Focus states */
    input:focus, select:focus {
        box-shadow: 0 0 0 2px rgba(139,157,195,0.3) !important;
    }
    
    /* Spinner */
    .stSpinner {
        color: var(--m-accent);
    }
    
    /* Success/Error messages - Morandi */
    .stSuccess {
        background: #e8efe6;
        color: #5a7a52;
        border-radius: 10px;
    }
    
    .stError {
        background: #f5e6e4;
        color: #8a5a52;
        border-radius: 10px;
    }
    
    /* Section headers */
    .section-title {
        font-size: 13px;
        font-weight: 400;
        color: var(--m-text-light);
        margin-bottom: 12px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: var(--m-text-light);
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)


# Session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'selected_pod' not in st.session_state:
    st.session_state.selected_pod = None


def init_connection():
    """Initialize Supabase connection"""
    try:
        client = get_supabase_client()
        return client
    except (ValueError, Exception) as e:
        st.error(str(e))
        st.info("Please configure Supabase credentials in .streamlit/secrets.toml")
        return None


def show_header():
    """Show app header"""
    lang = st.session_state.language
    title = "Nespresso Pod Picker" if lang == 'en' else "Nespresso 胶囊抽取器"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### ☕ {title}")
    with col2:
        if st.button("中文/EN"):
            st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
            st.rerun()


def show_user_selector(client):
    """Show user selection"""
    lang = st.session_state.language
    users = get_all_users(client)
    usernames = [u['username'] for u in users] if users else []
    
    # User selector area
    st.markdown("👤 **Select User**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if usernames:
            selected = st.selectbox(
                "Select user",
                options=usernames,
                key="user_select",
                label_visibility="collapsed"
            )
        else:
            selected = None
            st.info("No users yet. Create one below!")
    with col2:
        if st.button("+ New"):
            st.session_state.show_create_user = True
    
    if 'show_create_user' not in st.session_state:
        st.session_state.show_create_user = False
    
    if st.session_state.show_create_user:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            new_username = st.text_input("Username", key="new_username", placeholder="Your name...")
        with col2:
            if st.button("✓ Create", key="create_user_btn"):
                if new_username:
                    user = create_user(client, new_username)
                    if user:
                        st.session_state.current_user = user
                        st.session_state.show_create_user = False
                        st.rerun()
        
        if st.button("✕ Cancel", key="cancel_user_btn"):
            st.session_state.show_create_user = False
            st.rerun()
    
    if selected and st.session_state.current_user is None:
        user = get_user_by_username(client, selected)
        st.session_state.current_user = user
    
    return st.session_state.current_user


def show_random_picker(client, user):
    """Show random pod picker"""
    lang = st.session_state.language
    
    if not user:
        st.warning("👆 " + get_text("need_inventory", lang))
        return
    
    available_pods = get_available_pods_for_user(client, user['id'])
    
    if not available_pods:
        st.warning("📦 " + get_text("need_inventory", lang))
        return
    
    # Size preference
    size_options = [
        ("", "🎲 All"),
        ("40", "☕ Espresso"),
        ("80", "💪 Double"),
        ("150", "🌊 Lungo"),
        ("230", "🏔️ Coffee"),
    ]
    
    preference = st.selectbox(
        "Preference",
        options=[x[0] for x in size_options],
        format_func=lambda x: next((y[1] for y in size_options if y[0] == x), ""),
        key="preference_select"
    )
    
    filtered_pods = available_pods
    if preference:
        filtered_pods = [p for p in available_pods if p['capsules']['size_ml'] == int(preference)]
    
    if not filtered_pods:
        st.warning("😔 " + get_text("no_pods_available", lang))
        return
    
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("🎲 Pick Random", key="pick_btn", use_container_width=True):
        selected = random.choice(filtered_pods)
        st.session_state.selected_pod = selected
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_pod:
        pod_data = st.session_state.selected_pod
        capsule = pod_data['capsules']
        
        st.markdown("---")
        
        with st.container():
            st.markdown(f"""
            <div class="result-box">
                <h2>✨ {capsule.get('name_en', capsule.get('name'))}</h2>
                <p class="tasting">{capsule.get('tasting_note', '')}</p>
                <p class="details">{capsule.get('size_ml')}ml • {capsule.get('pod_type')} • {capsule.get('line')}</p>
                <p class="remaining">Remaining: {pod_data['quantity']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✓ Confirm", key="confirm_btn", use_container_width=True):
                decrement_inventory(client, pod_data['id'])
                st.balloons()
                st.success("☕ Enjoy your coffee!")
                st.session_state.selected_pod = None
                st.rerun()
        
        with col2:
            if st.button("🔄 Skip", key="skip_btn", use_container_width=True):
                st.session_state.selected_pod = None
                st.rerun()


def show_inventory(client, user):
    """Show inventory management - iOS MarkTime style"""
    lang = st.session_state.language
    
    if not user:
        return
    
    inventory = get_user_inventory(client, user['id'])
    all_capsules = get_all_capsules(client)
    
    # Morandi Style Header
    st.markdown("""
    <style>
    .m-header {
        font-size: 20px;
        font-weight: 500;
        color: #5a5a5a;
        margin-bottom: 16px;
    }
    .m-hint {
        font-size: 13px;
        color: #9a9a9a;
        margin-bottom: 16px;
        padding: 14px;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .m-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .m-capsule-name {
        font-size: 16px;
        font-weight: 500;
        color: #5a5a5a;
    }
    .m-capsule-info {
        font-size: 13px;
        color: #9a9a9a;
        margin-top: 4px;
    }
    .m-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 400;
        margin-right: 8px;
    }
    /* Morandi badges - softer colors */
    .m-badge-espresso { background: #e8e4df; color: #6b6b6b; }
    .m-badge-double { background: #e6dccf; color: #7a6b5a; }
    .m-badge-lungo { background: #dfe4e8; color: #5a6670; }
    .m-badge-coffee { background: #e0dde4; color: #6b5a70; }
    .m-line-original { color: #8b9dc3; }
    .m-line-vertuo { color: #c3a98b; }
    </style>
    """, unsafe_allow_html=True)
    
    # Add new capsule section
    st.markdown('<p class="m-header">📦 Add to Inventory</p>', unsafe_allow_html=True)
    
    # Size guide hint
    st.markdown("""
    <div class="m-hint">
        ☕ <b>Espresso</b> 40ml &nbsp;|&nbsp; 
        💪 <b>Double</b> 80ml &nbsp;|&nbsp; 
        🌊 <b>Lungo</b> 150ml &nbsp;|&nbsp; 
        🏔️ <b>Coffee</b> 230ml
    </div>
    """, unsafe_allow_html=True)
    
    # Line filter - use selectbox instead of radio for better horizontal display
    line_filter = st.selectbox("Line", ["All", "Original", "Vertuo"], label_visibility="collapsed")
    
    # Filter capsules - also deduplicate by name+line+size
    filtered = all_capsules
    if line_filter != "All":
        filtered = [c for c in filtered if c.get('line') == line_filter]
    
    # Deduplicate: keep only unique capsules by name+line+size
    seen = set()
    unique_capsules = []
    for c in filtered:
        key = (c.get('name'), c.get('line'), c.get('size_ml'))
        if key not in seen:
            seen.add(key)
            unique_capsules.append(c)
    filtered = unique_capsules
    
    # Search
    search = st.text_input("🔍 Search capsule...", key="search_capsule", placeholder="Type name...")
    
    if search:
        s = search.lower()
        filtered = [c for c in filtered if s in c.get('name', '').lower() or s in c.get('name_en', '').lower()]
    
    # Sort by size (small to large)
    filtered = sorted(filtered, key=lambda x: x.get('size_ml', 0))
    
    if filtered:
        # Build options with size info
        def format_capsule_option(c):
            name = c.get('name_en', c.get('name', ''))
            size = c.get('size_ml', 0)
            line = c.get('line', '')
            pod_type = c.get('pod_type', '')
            # Short format: Name | Size | Type
            return f"{name} | {size}ml"
        
        capsule_options = {c['id']: format_capsule_option(c) for c in filtered}
        
        # Show selection
        col1, col2 = st.columns([3, 1])
        with col1:
            selected = st.selectbox(
                "Select capsule",
                options=list(capsule_options.keys()),
                format_func=lambda x: capsule_options.get(x, ""),
                key="add_capsule_select",
                label_visibility="collapsed"
            )
        with col2:
            qty = st.number_input("Qty", min_value=1, value=10, key="add_quantity", label_visibility="collapsed")
        
        # Show selected capsule details
        if selected:
            selected_capsule = next((c for c in filtered if c['id'] == selected), None)
            if selected_capsule:
                size = selected_capsule.get('size_ml', 0)
                line = selected_capsule.get('line', '')
                pod_type = selected_capsule.get('pod_type', '')
                
                # Get badge class
                badge_class = f"m-badge-{pod_type}" if pod_type else ""
                line_class = f"m-line-{line.lower()}" if line else ""
                
                st.markdown(f"""
                <div class="m-card">
                    <span class="m-badge {badge_class}">{size}ml</span>
                    <span class="{line_class}">{line}</span>
                    <div class="m-capsule-info">{pod_type} • Intensity: {selected_capsule.get('intensity', '-')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("➕ Add to Inventory", key="add_btn", use_container_width=True):
            if selected:
                add_to_inventory(client, user['id'], selected, qty)
                st.success("✅ Added!")
                st.rerun()
    
    st.markdown("---")
    
    # Current inventory
    st.markdown('<p class="m-header">📋 My Inventory</p>', unsafe_allow_html=True)
    
    if not inventory:
        st.info("No capsules yet. Add some above!")
    else:
        # Sort by quantity
        inv_sorted = sorted(inventory, key=lambda x: x['quantity'], reverse=True)
        
        for item in inv_sorted:
            capsule = item['capsules']
            name = capsule.get('name_en', capsule.get('name'))
            size = capsule.get('size_ml', 0)
            line = capsule.get('line', '')
            pod_type = capsule.get('pod_type', '')
            
            badge_class = f"m-badge-{pod_type}" if pod_type else ""
            line_class = f"m-line-{line.lower()}" if line else ""
            
            with st.container():
                st.markdown(f"""
                <div class="m-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="m-capsule-name">{name}</div>
                        <div class="m-capsule-info">
                            <span class="m-badge {badge_class}">{size}ml</span>
                            <span class="{line_class}">{line}</span>
                        </div>
                    </div>
                    <div style="font-size: 22px; font-weight: 500; color: #5a5a5a;">{item['quantity']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([3, 1])
                with c1:
                    new_qty = st.number_input(
                        "Qty",
                        min_value=0,
                        value=item['quantity'],
                        key=f"qty_{item['id']}",
                        label_visibility="collapsed"
                    )
                    if new_qty != item['quantity']:
                        update_inventory_quantity(client, item['id'], new_qty)
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        remove_from_inventory(client, item['id'])
                        st.rerun()


def show_admin(client):
    """Show admin panel"""
    lang = st.session_state.language
    
    capsules = get_all_capsules(client)
    st.info(f"📊 Total: {len(capsules)} capsules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update Data", key="update_btn", use_container_width=True):
            with st.spinner("Updating..."):
                try:
                    new_capsules = scrape_all_capsules()
                    if not new_capsules:
                        new_capsules = get_sample_capsules()
                    saved = save_capsules(client, new_capsules)
                    st.success("✅ Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        if st.button("🧹 Remove Duplicates", key="dedup_btn", use_container_width=True):
            with st.spinner("Removing duplicates..."):
                try:
                    removed = remove_duplicate_capsules(client)
                    if removed > 0:
                        st.success(f"✅ Removed {removed} duplicates!")
                    else:
                        st.info("No duplicates found")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


def main():
    """Main app"""
    client = init_connection()
    if not client:
        st.warning("⚠️ Configure Supabase to continue")
        return
    
    show_header()
    st.markdown("---")
    
    user = show_user_selector(client)
    
    if user:
        lang = st.session_state.language
        st.markdown(f"### 👋 Hi, {user['username']}!")
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs([
            "🎲 Pick",
            "📦 Inventory",
            "⚙️ Settings"
        ])
        
        with tab1:
            show_random_picker(client, user)
        
        with tab2:
            show_inventory(client, user)
        
        with tab3:
            show_admin(client)
    
    st.markdown("---")
    st.markdown('<p class="footer">☕ Nespresso Pod Picker</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
