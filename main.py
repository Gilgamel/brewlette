# 主应用
import streamlit as st
import pandas as pd
from datetime import datetime
import random
import time
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from src.supabase_db import SupabaseDB
from src.translator import Translator

# 页面配置
st.set_page_config(
    page_title="Brewlette",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="auto"
)

# 初始化session state


if 'translator' not in st.session_state:
    try:
        settings = st.session_state.db.get_user_settings()
        lang = settings.get('language', 'en')
        st.session_state.translator = Translator(lang)
    except:
        st.session_state.translator = Translator('en')

if 'last_pick' not in st.session_state:
    st.session_state.last_pick = None

if 'preference' not in st.session_state:
    st.session_state.preference = None

# 获取翻译函数
t = st.session_state.translator.t

# 侧边栏
with st.sidebar:
    st.title(f"⚙️ {t('settings')}")
    
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
    
    # 保存语言设置
    try:
        st.session_state.db.update_user_settings(
            {'language': st.session_state.translator.language}
        )
    except:
        pass
    
    st.markdown("---")
    
    # 显示最近抽取历史
    st.subheader(f"📜 {t('history')}")
    try:
        history = st.session_state.db.get_pick_history(limit=5)
        if history:
            for h in history:
                pod = st.session_state.db.get_capsule_by_name(h['capsule_name'])
                if pod:
                    if st.session_state.translator.language == 'zh':
                        display_name = pod.get('display_name_zh', h['capsule_name'])
                    else:
                        display_name = pod.get('display_name_en', h['capsule_name'])
                else:
                    display_name = h['capsule_name']
                
                time_str = h['picked_at'][:10] if h.get('picked_at') else ''
                st.caption(f"☕ {display_name} - {time_str}")
        else:
            st.caption("No history yet" if language == 'English' else "暂无历史")
    except Exception as e:
        st.caption("Error loading history" if language == 'English' else "加载历史失败")

# 主页面
st.title(f"☕ {t('app_title')}")
st.markdown(f"*{t('welcome')}*")
st.markdown("---")

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
    
    # 创建两列布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"📦 {t('inventory')}")
        
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
                st.info(t('no_pods'))
        else:
            st.info(t('no_pods'))
        
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
                    options=list(pod_options.keys()),
                    key='add_pod_select'
                )
                selected_pod = pod_options[selected_display]
                
                quantity = st.number_input(
                    t('quantity'), 
                    min_value=1, 
                    value=1, 
                    step=1,
                    key='add_quantity'
                )
                
                if st.button(t('update_inventory'), use_container_width=True, key='add_button'):
                    try:
                        with st.spinner("Updating..." if language == 'English' else "更新中..."):
                            if st.session_state.db.add_to_inventory(selected_pod, quantity):
                                st.success(f"{t('added_success')}: +{quantity} {selected_display}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Update failed" if language == 'English' else "更新失败")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader(f"🎯 {t('preferences')}")
        
        # 偏好选择
        preference_type = st.radio(
            t('filter_by'),
            options=[t('no_preference'), t('size'), t('intensity')],
            horizontal=True,
            key='preference_type'
        )
        
        preference = None
        if preference_type == t('size'):
            size_options = [
                'espresso (40ml)', 
                'double_espresso (80ml)', 
                'lungo (110ml)', 
                'mug (230ml)', 
                'alto (414ml)'
            ]
            selected_size = st.selectbox(t('select_size'), size_options, key='size_select')
            size_map = {
                'espresso (40ml)': 'espresso',
                'double_espresso (80ml)': 'double_espresso',
                'lungo (110ml)': 'lungo',
                'mug (230ml)': 'mug',
                'alto (414ml)': 'alto'
            }
            preference = {'size': size_map[selected_size]}
            st.session_state.preference = preference
        
        elif preference_type == t('intensity'):
            min_intensity, max_intensity = st.slider(
                t('intensity'), 
                1, 13, (1, 13),
                key='intensity_slider'
            )
            preference = {
                'intensity_min': min_intensity, 
                'intensity_max': max_intensity
            }
            st.session_state.preference = preference
        
        # 抽取按钮
        if st.button(t('pick_button'), type="primary", use_container_width=True, key='pick_button'):
            try:
                # 获取可用胶囊（有库存的）
                available_pods = [name for name, qty in inventory.items() if qty > 0]
                
                if not available_pods:
                    st.warning(t('no_pods_available'))
                    st.stop()
                
                # 根据偏好过滤
                if preference_type != t('no_preference') and preference:
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
                        st.warning(t('no_pods_match'))
                        st.session_state.last_pick = None
                else:
                    st.session_state.last_pick = random.choice(available_pods)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
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
        if st.button(t('confirm_pick'), type="primary", use_container_width=True, key='confirm_button'):
            try:
                with st.spinner("Updating inventory..." if language == 'English' else "更新库存中..."):
                    success = st.session_state.db.consume_pod(st.session_state.last_pick)
                    
                    if success:
                        # 记录抽取历史
                        st.session_state.db.add_pick_history(
                            st.session_state.last_pick, 
                            st.session_state.preference
                        )
                        st.success(t('enjoy_coffee'))
                        st.session_state.last_pick = None
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(t('failed_consume'))
            except Exception as e:
                st.error(f"Error: {str(e)}")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.exception(e)

# 底部信息
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray; padding: 10px;'>{t('powered_by')}</div>",
    unsafe_allow_html=True
)

# 显示版本信息
st.caption(f"🔄 v1.0.0 | Data from Supabase")