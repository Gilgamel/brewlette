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

# Custom CSS - Clean light minimalist theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: #fafafa;
        color: #1a1a1a;
    }
    
    /* Clean white cards */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 12px 20px;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        color: #1a1a1a;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .stButton > button:hover {
        background: #f5f5f5;
        border-color: #ccc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    
    /* Primary action button */
    .primary-btn > button {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .primary-btn > button:hover {
        background: #333 !important;
    }
    
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        color: #1a1a1a;
    }
    
    .stTextInput > div > div {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        color: #1a1a1a;
    }
    
    .stExpander > div {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }
    
    .result-box {
        background: #ffffff;
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        margin: 30px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    
    .result-box h2 {
        color: #1a1a1a;
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .result-box .tasting {
        color: #666;
        font-size: 16px;
        margin-bottom: 16px;
    }
    
    .result-box .details {
        color: #999;
        font-size: 14px;
    }
    
    .result-box .remaining {
        color: #1a1a1a;
        font-size: 18px;
        font-weight: 500;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    
    .capsule-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px;
        margin: 6px 0;
        border: 1px solid #e8e8e8;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .capsule-card:hover {
        border-color: #ccc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .capsule-name {
        font-weight: 500;
        color: #1a1a1a;
    }
    
    .capsule-qty {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #666;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #999;
        font-size: 12px;
    }
    
    /* Tabs */
    div[data-testid="stTabs"] button {
        background: transparent;
        color: #666;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    
    div[data-testid="stTabs"] button[data-selected="true"] {
        background: #ffffff;
        color: #1a1a1a;
        border-bottom: 2px solid #1a1a1a;
    }
    
    .stAlert {
        background: #f5f5f5;
        border-radius: 8px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input focus states */
    input:focus, select:focus {
        border-color: #1a1a1a !important;
        outline: none;
    }
    
    /* Sidebar expander */
    .stSidebar .stExpander {
        background: #f5f5f5;
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
    """Show inventory management"""
    lang = st.session_state.language
    
    if not user:
        return
    
    inventory = get_user_inventory(client, user['id'])
    all_capsules = get_all_capsules(client)
    
    # Add new capsule
    st.markdown('<p class="section-title">Add Capsule</p>', unsafe_allow_html=True)
    
    # Search
    search = st.text_input("🔍 Search", key="search_capsule", placeholder="Type to search...")
    
    # Filter
    filtered = all_capsules
    if search:
        s = search.lower()
        filtered = [c for c in all_capsules if s in c.get('name', '').lower() or s in c.get('name_en', '').lower()]
    
    # Quick filters
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Original"):
            filtered = [c for c in filtered if c.get('line') == 'Original']
    with c2:
        if st.button("Vertuo"):
            filtered = [c for c in filtered if c.get('line') == 'Vertuo']
    with c3:
        if st.button("Clear"):
            pass
    
    if filtered:
        # Simple name only dropdown
        capsule_options = {c['id']: c.get('name_en', c['name']) for c in filtered}
        
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
        
        if st.button("➕ Add to Inventory", key="add_btn", use_container_width=True):
            if selected:
                add_to_inventory(client, user['id'], selected, qty)
                st.success("✅ Added!")
                st.rerun()
    
    st.markdown("---")
    
    # Current inventory
    st.markdown('<p class="section-title">My Inventory</p>', unsafe_allow_html=True)
    
    if not inventory:
        st.info("No capsules yet. Add some above!")
    else:
        inv_sorted = sorted(inventory, key=lambda x: x['quantity'], reverse=True)
        
        for item in inv_sorted:
            capsule = item['capsules']
            name = capsule.get('name_en', capsule.get('name'))
            
            with st.container():
                st.markdown(f"""
                <div class="capsule-card">
                    <span class="capsule-name">{name}</span>
                    <span class="capsule-qty">{item['quantity']}</span>
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
