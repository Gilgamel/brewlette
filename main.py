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
    layout="centered"
)

# Custom CSS - Modern dark theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 12px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stSelectbox > div > div, .stNumberInput > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .stExpander > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .result-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .result-box h2 {
        color: #fff;
        font-size: 28px;
        margin-bottom: 10px;
    }
    
    .result-box p {
        color: rgba(255, 255, 255, 0.8);
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: rgba(255, 255, 255, 0.5);
        font-size: 12px;
    }
    
    .title-text {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .capsule-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .capsule-card:hover {
        background: rgba(255, 255, 255, 0.12);
    }
    
    div[data-testid="stTabs"] button {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 10px 10px 0 0;
    }
    
    div[data-testid="stTabs"] button[data-selected="true"] {
        background: rgba(102, 126, 234, 0.3);
        color: white;
    }
    
    .stAlert {
        background: rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)


# Session state initialization
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
    except ValueError as e:
        st.error(str(e))
        st.info("Please configure Supabase credentials in .streamlit/secrets.toml")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def show_header():
    """Show app header with language toggle"""
    lang = st.session_state.language
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="title-text">
            {'☕ Nespresso Pod Picker' if lang == 'en' else '☕ Nespresso 胶囊抽取器'}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("中文/EN", key="lang_toggle"):
            st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
            st.rerun()


def show_user_selector(client):
    """Show user selection/creation UI"""
    lang = st.session_state.language
    
    users = get_all_users(client)
    usernames = [u['username'] for u in users] if users else []
    
    with st.expander("👤 " + get_text("select_user", lang), expanded=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if usernames:
                selected = st.selectbox(
                    get_text("select_user", lang),
                    options=usernames,
                    key="user_select"
                )
            else:
                selected = None
        
        with col2:
            if st.button("+" if lang == 'en' else "+"):
                st.session_state.show_create_user = True
    
    if 'show_create_user' not in st.session_state:
        st.session_state.show_create_user = False
    
    if st.session_state.show_create_user:
        col1, col2 = st.columns([3, 1])
        with col1:
            new_username = st.text_input(get_text("enter_username", lang), key="new_username", placeholder="Your name...")
        with col2:
            if st.button("✓" if lang == 'en' else "✓"):
                if new_username:
                    user = create_user(client, new_username)
                    if user:
                        st.session_state.current_user = user
                        st.session_state.show_create_user = False
                        st.rerun()
        
        if st.button("✕ Cancel" if lang == 'en' else "✕ 取消"):
            st.session_state.show_create_user = False
            st.rerun()
    
    if selected and st.session_state.current_user is None:
        user = get_user_by_username(client, selected)
        st.session_state.current_user = user
    
    return st.session_state.current_user


def show_random_picker(client, user):
    """Show random pod picker UI"""
    lang = st.session_state.language
    
    if not user:
        st.warning("👆 " + get_text("need_inventory", lang))
        return
    
    available_pods = get_available_pods_for_user(client, user['id'])
    
    if not available_pods:
        st.warning("📦 " + get_text("need_inventory", lang))
        return
    
    # Size preference selector
    size_options = [
        ("", "🎲 " + get_text("no_preference", lang)),
        ("40", "☕ Espresso (40ml)"),
        ("80", "💪 Double (80ml)"),
        ("150", "🌊 Lungo (150ml)"),
        ("230", "🏔️ Coffee (230ml)"),
    ]
    
    preference = st.selectbox(
        "📍 " + get_text("preference", lang),
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
    
    # Random pick button
    if st.button("🎲 " + get_text("pick_random", lang), key="pick_btn", use_container_width=True):
        selected = random.choice(filtered_pods)
        st.session_state.selected_pod = selected
        st.rerun()
    
    if st.session_state.selected_pod:
        pod_data = st.session_state.selected_pod
        capsule = pod_data['capsules']
        translated = translate_capsule(capsule, lang)
        
        st.markdown("---")
        
        with st.container():
            st.markdown(f"""
            <div class="result-box">
                <h2>✨ {translated['name']}</h2>
                <p style="font-size: 16px;">{translated['tasting_note']}</p>
                <p style="color: rgba(255,255,255,0.6);">
                    {translated['size_ml']}ml • {translated['pod_type']} • {translated['line']}
                </p>
                <p style="margin-top: 15px; font-size: 18px;">
                    📊 {get_text('remaining', lang)}: <strong>{pod_data['quantity']}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✓ " + get_text("confirm", lang), key="confirm_btn", use_container_width=True):
                decrement_inventory(client, pod_data['id'])
                st.balloons()
                st.success("☕ " + get_text("confirm_success", lang))
                st.session_state.selected_pod = None
                st.rerun()
        
        with col2:
            if st.button("🔄 " + get_text("skip", lang), key="skip_btn", use_container_width=True):
                st.session_state.selected_pod = None
                st.rerun()


def show_inventory(client, user):
    """Show inventory management UI"""
    lang = st.session_state.language
    
    if not user:
        return
    
    inventory = get_user_inventory(client, user['id'])
    all_capsules = get_all_capsules(client)
    
    # Add new capsule section with search
    st.markdown("### ➕ " + get_text("add_capsule", lang))
    
    # Search input
    search_query = st.text_input("🔍 " + ("Search capsules..." if lang == 'en' else "搜索胶囊..."), key="search_capsule")
    
    # Filter capsules based on search
    filtered_capsules = all_capsules
    if search_query:
        search_lower = search_query.lower()
        filtered_capsules = [
            c for c in all_capsules 
            if search_lower in c.get('name', '').lower() 
            or search_lower in c.get('name_en', '').lower()
            or search_lower in c.get('line', '').lower()
        ]
    
    # Quick filter buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Original", key="filter_original"):
            filtered_capsules = [c for c in filtered_capsules if c.get('line') == 'Original']
    with col2:
        if st.button("Vertuo", key="filter_vertuo"):
            filtered_capsules = [c for c in filtered_capsules if c.get('line') == 'Vertuo']
    with col3:
        if st.button("All", key="filter_all"):
            pass
    
    if filtered_capsules:
        capsule_options = {c['id']: f"{c.get('name_en', c['name'])} ({c.get('line', '')} {c.get('size_ml', '?')}ml)" for c in filtered_capsules}
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_capsule_id = st.selectbox(
                get_text("select_capsule", lang),
                options=list(capsule_options.keys()),
                format_func=lambda x: capsule_options.get(x, ""),
                key="add_capsule_select"
            )
        
        with col2:
            quantity = st.number_input(get_text("enter_quantity", lang), min_value=1, value=10, key="add_quantity")
        
        if st.button("➕ " + get_text("add", lang), key="add_btn", use_container_width=True):
            if selected_capsule_id:
                add_to_inventory(client, user['id'], selected_capsule_id, quantity)
                st.success("✅ " + get_text("capsule_added", lang))
                st.rerun()
    else:
        st.info("No capsules found" if lang == 'en' else "没有找到胶囊")
    
    st.markdown("---")
    
    # Show current inventory
    st.markdown("### 📦 " + get_text("my_inventory", lang))
    
    if not inventory:
        st.info("📭 " + get_text("no_inventory", lang))
    else:
        # Sort by quantity descending
        inventory_sorted = sorted(inventory, key=lambda x: x['quantity'], reverse=True)
        
        for item in inventory_sorted:
            capsule = item['capsules']
            translated = translate_capsule(capsule, lang)
            
            with st.container():
                st.markdown(f"""
                <div class="capsule-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{translated['name']}</strong>
                            <span style="color: rgba(255,255,255,0.5); font-size: 12px;">
                                {translated['size_ml']}ml • {translated['line']}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 24px; font-weight: bold; color: #667eea;">{item['quantity']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
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
                
                with col3:
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        remove_from_inventory(client, item['id'])
                        st.rerun()


def show_admin(client):
    """Show admin panel"""
    lang = st.session_state.language
    
    st.markdown("### ⚙️ " + get_text("admin_panel", lang))
    
    capsules = get_all_capsules(client)
    st.info(f"📊 {get_text('total_capsules', lang)}: {len(capsules)}")
    
    if st.button("🔄 " + get_text("update_btn", lang), key="update_btn", use_container_width=True):
        with st.spinner("⏳ " + get_text("updating", lang)):
            try:
                new_capsules = scrape_all_capsules()
                
                if not new_capsules:
                    new_capsules = get_sample_capsules()
                
                saved = save_capsules(client, new_capsules)
                st.success("✅ " + get_text("update_success", lang))
                st.rerun()
            except Exception as e:
                st.error(f"❌ {get_text('update_error', lang)}: {e}")
    
    # Show capsules by line
    if capsules:
        orig_caps = [c for c in capsules if c.get('line') == 'Original']
        vert_caps = [c for c in capsules if c.get('line') == 'Vertuo']
        
        with st.expander(f"📋 Original ({len(orig_caps)})"):
            for c in orig_caps:
                st.write(f"• {c.get('name_en', c['name'])} ({c.get('size_ml', '?')}ml)")
        
        with st.expander(f"📋 Vertuo ({len(vert_caps)})"):
            for c in vert_caps:
                st.write(f"• {c.get('name_en', c['name'])} ({c.get('size_ml', '?')}ml)")


def show_footer():
    """Show footer banner"""
    lang = st.session_state.language
    powered_by_text = get_text("powered_by", lang)
    st.markdown(f"""
        <div class="footer">
            ✨ {powered_by_text} Nespresso Pod Picker
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    
    client = init_connection()
    if not client:
        st.warning("⚠️ Please configure Supabase to continue.")
        st.info("""
        ### Setup Instructions:
        1. Create a free Supabase project at [supabase.com](https://supabase.com)
        2. Create tables: `capsules`, `users`, `inventory`
        3. Add credentials to `.streamlit/secrets.toml`
        """)
        return
    
    show_header()
    st.markdown("---")
    
    user = show_user_selector(client)
    
    if user:
        lang = st.session_state.language
        st.markdown(f"### 👋 {get_text('welcome', lang)} {user['username']}!")
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs([
            "🎲 " + get_text('tab_random', lang),
            "📦 " + get_text('tab_inventory', lang),
            "⚙️ " + get_text('tab_admin', lang)
        ])
        
        with tab1:
            show_random_picker(client, user)
        
        with tab2:
            show_inventory(client, user)
        
        with tab3:
            show_admin(client)
    
    st.markdown("---")
    show_footer()


if __name__ == "__main__":
    main()
