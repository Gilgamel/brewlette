# 主应用
import streamlit as st
import pandas as pd
from datetime import datetime
import random

from src.supabase_db import SupabaseDB
from src.translator import Translator
from src.scraper import NespressoScraper

# 页面配置
st.set_page_config(
    page_title="Nespresso Pod Picker",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化session state
if 'db' not in st.session_state:
    try:
        st.session_state.db = SupabaseDB()
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        st.stop()

if 'translator' not in st.session_state:
    # 从数据库获取语言设置
    try:
        settings = st.session_state.db.get_user_settings()
        lang = settings.get('language', 'en')
        st.session_state.translator = Translator(lang)
    except:
        st.session_state.translator = Translator('en')

if 'last_pick' not in st.session_state:
    st.session_state.last_pick = None

# 获取翻译函数
t = st.session_state.translator.t

# 侧边栏 - 语言选择
with st.sidebar:
    st.title("⚙️ Settings")
    
    # 语言选择
    language = st.selectbox(
        t('language'),
        options=['English', '中文'],
        index=0 if st.session_state.translator.language == 'en' else 1
    )
    
    if language == '中文':
        st.session_state.translator.set_language('zh')
    else:
        st.session_state.translator.set_language('en')
    
    # 保存语言设置到数据库
    try:
        st.session_state.db.update_user_settings(
            {'language': st.session_state.translator.language}
        )
    except:
        pass
    
    st.markdown("---")
    
    # 显示最近抽取历史
    st.subheader(t('history'))
    try:
        history = st.session_state.db.get_pick_history(limit=5)
        for h in history:
            pod = st.session_state.db.get_capsule_by_name(h['capsule_name'])
            display_name = pod.get('display_name_en', h['capsule_name']) if pod else h['capsule_name']
            time_str = h['picked_at'][:10] if h['picked_at'] else ''
            st.caption(f"☕ {display_name} - {time_str}")
    except:
        st.caption("No history yet")

# 主页面
st.title(t('app_title'))
st.markdown(f"*{t('welcome')}*")
st.markdown("---")

# 创建两列布局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"📦 {t('inventory')}")
    
    # 获取所有胶囊和库存
    try:
        all_capsules = st.session_state.db.get_all_capsules()
        inventory = st.session_state.db.get_inventory()
        
        # 创建胶囊名称到显示名称的映射
        capsule_display = {}
        for c in all_capsules:
            name = c['name']
            if st.session_state.translator.language == 'zh' and c.get('display_name_zh'):
                capsule_display[name] = c['display_name_zh']
            else:
                capsule_display[name] = c.get('display_name_en', name)
        
        # 显示当前库存
        if inventory:
            inventory_data = []
            for name, qty in inventory.items():
                if qty > 0:
                    display_name = capsule_display.get(name, name)
                    inventory_data.append({
                        t('pod_name'): display_name,
                        t('quantity'): qty
                    })
            
            if inventory_data:
                df = pd.DataFrame(inventory_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No capsules in inventory")
        else:
            st.info("No capsules in inventory")
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
    
    # 添加/更新胶囊
    with st.expander(f"➕ {t('add_pod')}"):
        if all_capsules:
            # 创建选择列表
            pod_options = {}
            for c in all_capsules:
                display = capsule_display.get(c['name'], c['name'])
                pod_options[display] = c['name']
            
            selected_display = st.selectbox(
                t('pod_name'),
                options=list(pod_options.keys())
            )
            selected_pod = pod_options[selected_display]
            
            quantity = st.number_input(
                t('quantity'), 
                min_value=1, 
                value=1, 
                step=1
            )
            
            if st.button(t('update_inventory'), use_container_width=True):
                try:
                    st.session_state.db.add_to_inventory(selected_pod, quantity)
                    st.success(f"Added {quantity} {selected_display}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

with col2:
    st.subheader(f"🎯 {t('preferences')}")
    
    # 偏好选择
    preference_type = st.radio(
        "Filter by:",
        options=[t('no_preference'), t('size'), t('intensity')],
        horizontal=True
    )
    
    preference = None
    if preference_type == t('size'):
        size_options = ['espresso (40ml)', 'double_espresso (80ml)', 'lungo (110ml)', 'mug (230ml)', 'alto (414ml)']
        selected_size = st.selectbox(t('select_size'), size_options)
        size_map = {
            'espresso (40ml)': 'espresso',
            'double_espresso (80ml)': 'double_espresso',
            'lungo (110ml)': 'lungo',
            'mug (230ml)': 'mug',
            'alto (414ml)': 'alto'
        }
        preference = {'size': size_map[selected_size]}
    
    elif preference_type == t('intensity'):
        min_intensity = st.slider(t('intensity'), 1, 13, (1, 13))
        preference = {'intensity_min': min_intensity[0], 'intensity_max': min_intensity[1]}
    
    # 抽取按钮
    if st.button(t('pick_button'), type="primary", use_container_width=True):
        try:
            # 获取可用胶囊
            inventory = st.session_state.db.get_inventory()
            available_pods = [name for name, qty in inventory.items() if qty > 0]
            
            if not available_pods:
                st.warning("No capsules available!")
                st.stop()
            
            # 根据偏好过滤
            if preference:
                filtered_pods = []
                for pod_name in available_pods:
                    pod_info = st.session_state.db.get_capsule_by_name(pod_name)
                    if pod_info:
                        if preference_type == t('size'):
                            if pod_info.get('size_category') == preference['size']:
                                filtered_pods.append(pod_name)
                        elif preference_type == t('intensity'):
                            intensity = pod_info.get('intensity', 0)
                            if preference['intensity_min'] <= intensity <= preference['intensity_max']:
                                filtered_pods.append(pod_name)
                
                if filtered_pods:
                    st.session_state.last_pick = random.choice(filtered_pods)
                else:
                    st.warning("No pods match your preference!")
            else:
                st.session_state.last_pick = random.choice(available_pods)
            
        except Exception as e:
            st.error(f"Error picking pod: {e}")

# 结果显示
if st.session_state.last_pick:
    st.markdown("---")
    st.subheader(f"✨ {t('result')}")
    
    pod_info = st.session_state.db.get_capsule_by_name(st.session_state.last_pick)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if pod_info:
            display_name = capsule_display.get(st.session_state.last_pick, st.session_state.last_pick)
            st.metric(t('pod_name'), display_name)
    
    with col2:
        if pod_info:
            size_display = f"{pod_info.get('size_ml', '?')}ml"
            st.metric(t('size'), size_display)
    
    with col3:
        if pod_info:
            st.metric(t('intensity'), pod_info.get('intensity', '?'))
    
    with col4:
        current_qty = inventory.get(st.session_state.last_pick, 0)
        st.metric(t('remaining'), current_qty)
    
    if pod_info:
        notes_key = 'tasting_notes_zh' if st.session_state.translator.language == 'zh' else 'tasting_notes_en'
        tasting_notes = pod_info.get(notes_key, '')
        if tasting_notes:
            st.info(f"📝 {t('tasting_notes')}: {tasting_notes}")
    
    # 确认抽取按钮
    if st.button(t('confirm_pick'), type="primary", use_container_width=True):
        try:
            if st.session_state.db.consume_pod(st.session_state.last_pick):
                # 记录抽取历史
                st.session_state.db.add_pick_history(
                    st.session_state.last_pick, 
                    preference
                )
                st.success("Enjoy your coffee! ☕")
                st.session_state.last_pick = None
                st.rerun()
            else:
                st.error("Failed to consume pod")
        except Exception as e:
            st.error(f"Error: {e}")

# 底部信息
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray; padding: 10px;'>{t('powered_by')}</div>",
    unsafe_allow_html=True
)

# 显示最后更新时间
st.caption(f"🔄 Data from Nespresso")