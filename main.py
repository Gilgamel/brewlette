"""
Nespresso Pod Picker - Main Application
A Streamlit web app for randomly selecting Nespresso pods
"""
import streamlit as st
import random
from datetime import datetime

# Import our modules
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
    remove_duplicate_capsules,
    clear_and_reset_capsules
)
from src.scraper import scrape_all_capsules, get_sample_capsules
from src.translator import get_text, translate_capsule

# Page configuration
st.set_page_config(
    page_title="Nespresso Pod Picker",
    page_icon="☕",
    layout="centered"
)

# Custom CSS for mobile-friendly design
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 10px;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .capsule-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
    }
    @media (max-width: 768px) {
        .stTextInput, .stSelectbox, .stNumberInput {
            width: 100% !important;
        }
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


def show_language_toggle():
    """Show language toggle button"""
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.language == 'en':
            st.markdown("### ☕ Nespresso Pod Picker")
        else:
            st.markdown("### ☕ Nespresso 胶囊抽取器")
    
    with col2:
        if st.button("中文/EN", key="lang_toggle"):
            st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
            st.rerun()


def show_user_selector(client):
    """Show user selection/creation UI"""
    lang = st.session_state.language
    
    # Get all users
    users = get_all_users(client)
    usernames = [u['username'] for u in users] if users else []
    
    # Create user section
    with st.expander(get_text("select_user", lang), expanded=True):
        col1, col2 = st.columns([2, 1])
        
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
            if st.button(get_text("create_user", lang), key="create_user_btn"):
                st.session_state.show_create_user = True
    
    # Create new user form
    if 'show_create_user' not in st.session_state:
        st.session_state.show_create_user = False
    
    if st.session_state.show_create_user:
        with st.form("create_user_form"):
            new_username = st.text_input(get_text("enter_username", lang), key="new_username")
            submit = st.form_submit_button(get_text("create", lang))
            
            if submit and new_username:
                user = create_user(client, new_username)
                if user:
                    st.session_state.current_user = user
                    st.session_state.show_create_user = False
                    st.rerun()
                else:
                    st.error("Error creating user")
        
        if st.button("Cancel", key="cancel_create"):
            st.session_state.show_create_user = False
            st.rerun()
    
    # Set current user
    if selected and st.session_state.current_user is None:
        user = get_user_by_username(client, selected)
        st.session_state.current_user = user
    
    return st.session_state.current_user


def show_random_picker(client, user):
    """Show random pod picker UI"""
    lang = st.session_state.language
    
    if not user:
        st.warning(get_text("need_inventory", lang))
        return
    
    # Get available pods for user
    available_pods = get_available_pods_for_user(client, user['id'])
    
    if not available_pods:
        st.warning(get_text("need_inventory", lang))
        return
    
    # Preference selection
    st.markdown(f"**{get_text('preference', lang)}:**")
    
    size_options = {
        "": get_text("no_preference", lang),
        "40": get_text("espresso_40ml", lang),
        "80": get_text("double_80ml", lang),
        "150": get_text("lungo_150ml", lang),
        "230": get_text("coffee_230ml", lang),
        "400": get_text("alto_400ml", lang)
    }
    
    preference = st.selectbox(
        get_text("preference", lang),
        options=list(size_options.keys()),
        format_func=lambda x: size_options[x],
        key="preference_select"
    )
    
    # Filter pods based on preference
    filtered_pods = available_pods
    if preference:
        filtered_pods = [p for p in available_pods if p['capsules']['size_ml'] == int(preference)]
    
    if not filtered_pods:
        st.warning(get_text("no_pods_available", lang))
        return
    
    # Random pick button
    if st.button(f"🎲 {get_text('pick_random', lang)}", key="pick_btn", use_container_width=True):
        # Randomly select a pod
        selected = random.choice(filtered_pods)
        st.session_state.selected_pod = selected
        st.rerun()
    
    # Show selected pod
    if st.session_state.selected_pod:
        pod_data = st.session_state.selected_pod
        capsule = pod_data['capsules']
        translated = translate_capsule(capsule, lang)
        
        st.markdown("---")
        st.markdown(f"## 🎉 {get_text('result', lang)}")
        
        # Display capsule info
        with st.container():
            st.markdown(f"""
            <div class="result-box">
                <h2>{translated['name']}</h2>
                <p><strong>{translated['tasting_note']}</strong></p>
                <p>{translated['size_ml']}ml | {translated['pod_type']} | {translated['line']}</p>
                <p>📊 {get_text('remaining', lang)}: {pod_data['quantity']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Confirm/Skip buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"✓ {get_text('confirm', lang)}", key="confirm_btn", use_container_width=True):
                # Decrement inventory
                decrement_inventory(client, pod_data['id'])
                st.success(get_text("confirm_success", lang))
                st.session_state.selected_pod = None
                st.rerun()
        
        with col2:
            if st.button(f"🔄 {get_text('skip', lang)}", key="skip_btn", use_container_width=True):
                st.session_state.selected_pod = None
                st.rerun()


def show_inventory(client, user):
    """Show inventory management UI"""
    lang = st.session_state.language
    
    if not user:
        return
    
    # Get current inventory
    inventory = get_user_inventory(client, user['id'])
    
    # Get all available capsules
    all_capsules = get_all_capsules(client)
    
    # Add new capsule section
    st.markdown(f"### ➕ {get_text('add_capsule', lang)}")
    
    with st.form("add_capsule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Capsule selector
            capsule_options = {c['id']: f"{c.get('name_en', c['name'])} ({c.get('line', '')} - {c.get('size_ml', '?')}ml)" 
                            for c in all_capsules}
            selected_capsule_id = st.selectbox(
                get_text("select_capsule", lang),
                options=list(capsule_options.keys()),
                format_func=lambda x: capsule_options.get(x, ""),
                key="add_capsule_select"
            )
        
        with col2:
            quantity = st.number_input(get_text("enter_quantity", lang), min_value=1, value=10, key="add_quantity")
        
        submit = st.form_submit_button(get_text("add", lang), use_container_width=True)
        
        if submit and selected_capsule_id:
            add_to_inventory(client, user['id'], selected_capsule_id, quantity)
            st.success(get_text("capsule_added", lang))
            st.rerun()
    
    st.markdown("---")
    
    # Show current inventory
    st.markdown(f"### 📦 {get_text('my_inventory', lang)}")
    
    if not inventory:
        st.info(get_text("no_inventory", lang))
    else:
        # Display inventory items
        for item in inventory:
            capsule = item['capsules']
            translated = translate_capsule(capsule, lang)
            
            with st.expander(f"{translated['name']} - {item['quantity']} {get_text('quantity', lang)}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{translated['name']}**")
                    st.caption(f"{translated['size_ml']}ml | {translated['pod_type']} | {translated['line']}")
                    if translated['tasting_note']:
                        st.caption(f"📝 {translated['tasting_note']}")
                
                with col2:
                    new_qty = st.number_input(
                        get_text("quantity", lang),
                        min_value=0,
                        value=item['quantity'],
                        key=f"qty_{item['id']}"
                    )
                    if new_qty != item['quantity']:
                        update_inventory_quantity(client, item['id'], new_qty)
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ {get_text('delete', lang)}", key=f"del_{item['id']}"):
                        remove_from_inventory(client, item['id'])
                        st.rerun()


def show_admin(client):
    """Show admin panel"""
    lang = st.session_state.language
    
    st.markdown(f"### ⚙️ {get_text('admin_panel', lang)}")
    
    # Get capsule count
    capsules = get_all_capsules(client)
    st.info(f"{get_text('total_capsules', lang)}: {len(capsules)}")
    
    # Update capsules button
    if st.button(f"🔄 {get_text('update_btn', lang)}", key="update_btn", use_container_width=True):
        with st.spinner(get_text("updating", lang)):
            try:
                # Scrape new data
                new_capsules = scrape_all_capsules()
                
                # If scraping returns empty, use sample data
                if not new_capsules:
                    new_capsules = get_sample_capsules()
                
                # Save to database
                saved = save_capsules(client, new_capsules)
                st.success(get_text("update_success", lang))
                st.rerun()
            except Exception as e:
                st.error(f"{get_text('update_error', lang)}: {e}")
    
    # Remove duplicates button
    if st.button(f"🧹 Remove Duplicates", key="dedup_btn", use_container_width=True):
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
    
    # Full reset option
    st.markdown("---")
    st.warning("⚠️ **Full Reset** - This will clear all capsules and inventory, then re-import fresh data")
    
    if st.button("♻️ Reset All Data", key="reset_btn", use_container_width=True):
        with st.spinner("Resetting..."):
            try:
                new_capsules = scrape_all_capsules()
                if not new_capsules:
                    new_capsules = get_sample_capsules()
                count = clear_and_reset_capsules(client, new_capsules)
                st.success(f"✅ Reset complete! Imported {count} capsules")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Show sample capsules list
    if capsules:
        with st.expander(f"📋 {get_text('total_capsules', lang)} ({len(capsules)})"):
            for c in capsules:
                st.write(f"- {c.get('name_en', c['name'])} ({c.get('line', '')} - {c.get('size_ml', '?')}ml)")


def show_footer():
    """Show footer banner"""
    lang = st.session_state.language
    powered_by_text = get_text("powered_by", lang)
    st.markdown(f"""
        <div class="footer">
            {powered_by_text} Nespresso Pod Picker ☕
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Initialize connection
    client = init_connection()
    if not client:
        st.warning("Please configure Supabase to continue.")
        st.info("""
        ### Setup Instructions:
        1. Create a free Supabase project at supabase.com
        2. Create tables: `capsules`, `users`, `inventory`
        3. Add credentials to .streamlit/secrets.toml
        """)
        return
    
    # Show language toggle
    show_language_toggle()
    st.markdown("---")
    
    # User selection
    user = show_user_selector(client)
    
    if user:
        st.markdown(f"### 👋 {get_text('welcome', lang='en' if st.session_state.language == 'en' else 'zh')} {user['username']}!")
        st.markdown("---")
        
        # Tab navigation
        lang = st.session_state.language
        tab1, tab2, tab3 = st.tabs([
            f"🎲 {get_text('tab_random', lang)}",
            f"📦 {get_text('tab_inventory', lang)}",
            f"⚙️ {get_text('tab_admin', lang)}"
        ])
        
        with tab1:
            show_random_picker(client, user)
        
        with tab2:
            show_inventory(client, user)
        
        with tab3:
            show_admin(client)
    
    # Show footer
    st.markdown("---")
    show_footer()


if __name__ == "__main__":
    main()
