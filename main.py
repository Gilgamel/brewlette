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
    save_capsules
)
from src.scraper import scrape_all_capsules, get_sample_capsules
from src.translator import get_text, translate_capsule

# Page configuration
st.set_page_config(
    page_title="Nespresso Pod Picker",
    page_icon="☕",
    layout="wide"
)

# Custom CSS - iOS MarkTime Style
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif');
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
    }
    
    /* iOS System Colors */
    :root {
        --ios-bg: #f2f2f7;
        --ios-card: #ffffff;
        --ios-text: #000000;
        --ios-text-secondary: #8e8e93;
        --ios-blue: #007aff;
        --ios-orange: #ff9500;
        --ios-green: #34c759;
        --ios-red: #ff3b30;
    }
    
    .stApp {
        background: var(--ios-bg);
        color: var(--ios-text);
    }
    
    /* Center the main content - iOS max width */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 680px;
        margin: 0 auto;
    }
    
    /* Center align headers - iOS style */
    h1, h2, h3, h4 {
        font-weight: 600;
        color: #000;
    }
    
    h3 {
        font-size: 22px;
    }
    
    /* Center content */
    .stMarkdown {
        text-align: center;
    }
    
    /* iOS Style Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 14px 20px;
        background: var(--ios-card);
        border: none;
        color: var(--ios-blue);
        font-weight: 500;
        font-size: 17px;
        transition: all 0.15s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: #f2f2f7;
    }
    
    .stButton > button:active {
        background: #e5e5ea;
        transform: scale(0.98);
    }
    
    /* Primary action button - iOS blue */
    .primary-btn > button {
        background: var(--ios-blue) !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .primary-btn > button:hover {
        background: #0066cc !important;
    }
    
    /* iOS Style Inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: var(--ios-card);
        border-radius: 10px;
        border: none;
        color: var(--ios-text);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div {
        background: var(--ios-card);
        border-radius: 10px;
        border: none;
        color: var(--ios-text);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: transparent !important;
    }
    
    /* iOS Style Tabs */
    div[data-testid="stTabs"] {
        background: var(--ios-card);
        border-radius: 12px;
        padding: 4px;
    }
    
    div[data-testid="stTabs"] button {
        background: transparent;
        color: var(--ios-text-secondary);
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
        padding: 8px 16px;
    }
    
    div[data-testid="stTabs"] button[data-selected="true"] {
        background: var(--ios-blue);
        color: #ffffff;
    }
    
    /* iOS Cards */
    .stExpander > div {
        background: var(--ios-card);
        border-radius: 12px;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Result Box - iOS style */
    .result-box {
        background: var(--ios-card);
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        margin: 24px 0;
        border: none;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .result-box h2 {
        color: #000;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .result-box .tasting {
        color: var(--ios-text-secondary);
        font-size: 15px;
        margin-bottom: 12px;
    }
    
    .result-box .details {
        color: var(--ios-text-secondary);
        font-size: 13px;
    }
    
    .result-box .remaining {
        color: var(--ios-text);
        font-size: 17px;
        font-weight: 500;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #e5e5ea;
    }
    
    /* iOS Radio buttons */
    div[data-testid="stRadio"] > div {
        background: var(--ios-card);
        border-radius: 10px;
        padding: 4px;
    }
    
    div[data-testid="stRadio"] label {
        background: transparent;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    div[data-testid="stRadio"] label:has(input:checked) {
        background: var(--ios-blue);
        color: white;
    }
    
    /* Alerts - iOS style */
    .stAlert {
        background: var(--ios-card);
        border-radius: 10px;
        border: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* iOS Focus states */
    input:focus, select:focus {
        box-shadow: 0 0 0 3px rgba(0,122,255,0.3) !important;
    }
    
    /* Spinner */
    .stSpinner {
        color: var(--ios-blue);
    }
    
    /* Success/Error messages - iOS */
    .stSuccess {
        background: #d4edda;
        color: #155724;
        border-radius: 10px;
    }
    
    .stError {
        background: #f8d7da;
        color: #721c24;
        border-radius: 10px;
    }
    
    /* Section headers */
    .section-title {
        font-size: 13px;
        font-weight: 500;
        color: var(--ios-text-secondary);
        margin-bottom: 12px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: var(--ios-text-secondary);
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
    
    # iOS Style Header
    st.markdown("""
    <style>
    .ios-header {
        font-size: 22px;
        font-weight: 600;
        color: #1c1c1e;
        margin-bottom: 20px;
    }
    .ios-section-title {
        font-size: 13px;
        font-weight: 500;
        color: #8e8e93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    .ios-hint {
        font-size: 13px;
        color: #8e8e93;
        margin-bottom: 16px;
        padding: 12px;
        background: #f2f2f7;
        border-radius: 10px;
    }
    .ios-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .ios-capsule-name {
        font-size: 17px;
        font-weight: 500;
        color: #000000;
    }
    .ios-capsule-info {
        font-size: 13px;
        color: #8e8e93;
        margin-top: 4px;
    }
    .ios-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
    }
    .ios-badge-espresso { background: #e8f5e9; color: #2e7d32; }
    .ios-badge-double { background: #fff3e0; color: #ef6c00; }
    .ios-badge-lungo { background: #e3f2fd; color: #1565c0; }
    .ios-badge-coffee { background: #f3e5f5; color: #7b1fa2; }
    .ios-line-original { color: #007aff; }
    .ios-line-vertuo { color: #ff9500; }
    </style>
    """, unsafe_allow_html=True)
    
    # Add new capsule section
    st.markdown('<p class="ios-header">📦 Add to Inventory</p>', unsafe_allow_html=True)
    
    # Size guide hint
    st.markdown("""
    <div class="ios-hint">
        ☕ <b>Espresso</b> 40ml &nbsp;|&nbsp; 
        💪 <b>Double</b> 80ml &nbsp;|&nbsp; 
        🌊 <b>Lungo</b> 150ml &nbsp;|&nbsp; 
        🏔️ <b>Coffee</b> 230ml
    </div>
    """, unsafe_allow_html=True)
    
    # Line filter
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        line_filter = st.radio("Line", ["All", "Original", "Vertuo"], horizontal=True, label_visibility="collapsed")
    
    # Filter capsules
    filtered = all_capsules
    if line_filter != "All":
        filtered = [c for c in filtered if c.get('line') == line_filter]
    
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
                badge_class = f"ios-badge-{pod_type}" if pod_type else ""
                line_class = f"ios-line-{line.lower()}" if line else ""
                
                st.markdown(f"""
                <div class="ios-card">
                    <span class="ios-badge {badge_class}">{size}ml</span>
                    <span class="{line_class}">{line}</span>
                    <div class="ios-capsule-info">{pod_type} • Intensity: {selected_capsule.get('intensity', '-')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("➕ Add to Inventory", key="add_btn", use_container_width=True):
            if selected:
                add_to_inventory(client, user['id'], selected, qty)
                st.success("✅ Added!")
                st.rerun()
    
    st.markdown("---")
    
    # Current inventory
    st.markdown('<p class="ios-header">📋 My Inventory</p>', unsafe_allow_html=True)
    
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
            
            badge_class = f"ios-badge-{pod_type}" if pod_type else ""
            line_class = f"ios-line-{line.lower()}" if line else ""
            
            with st.container():
                st.markdown(f"""
                <div class="ios-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="ios-capsule-name">{name}</div>
                        <div class="ios-capsule-info">
                            <span class="ios-badge {badge_class}">{size}ml</span>
                            <span class="{line_class}">{line}</span>
                        </div>
                    </div>
                    <div style="font-size: 24px; font-weight: 600; color: #000;">{item['quantity']}</div>
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
