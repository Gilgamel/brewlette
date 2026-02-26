# Supabase数据库模块
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

class SupabaseDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("请设置 SUPABASE_URL 和 SUPABASE_KEY 环境变量")
        
        self.supabase = create_client(self.url, self.key)
    
    # ========== 胶囊管理 ==========
    def get_all_capsules(self):
        """获取所有胶囊"""
        response = self.supabase.table('capsules').select('*').execute()
        return response.data
    
    def get_capsule_by_name(self, name):
        """根据名称获取胶囊"""
        response = self.supabase.table('capsules')\
            .select('*')\
            .eq('name', name)\
            .execute()
        return response.data[0] if response.data else None
    
    def update_capsules(self, capsules):
        """批量更新胶囊"""
        for capsule in capsules:
            self.supabase.table('capsules').upsert(capsule).execute()
    
    # ========== 库存管理 ==========
    def get_inventory(self, user_id='default_user'):
        """获取用户库存"""
        response = self.supabase.table('user_inventory')\
            .select('capsule_name, quantity')\
            .eq('user_id', user_id)\
            .execute()
        
        inventory = {}
        for item in response.data:
            inventory[item['capsule_name']] = item['quantity']
        return inventory
    
    def update_inventory(self, capsule_name, quantity, user_id='default_user'):
        """更新库存"""
        data = {
            'user_id': user_id,
            'capsule_name': capsule_name,
            'quantity': quantity,
            'last_updated': datetime.now().isoformat()
        }
        
        self.supabase.table('user_inventory').upsert(data).execute()
    
    def add_to_inventory(self, capsule_name, quantity_to_add, user_id='default_user'):
        """添加胶囊到库存"""
        current = self.get_inventory(user_id)
        current_qty = current.get(capsule_name, 0)
        new_qty = current_qty + quantity_to_add
        self.update_inventory(capsule_name, new_qty, user_id)
    
    def consume_pod(self, capsule_name, user_id='default_user'):
        """消耗一个胶囊"""
        current = self.get_inventory(user_id)
        current_qty = current.get(capsule_name, 0)
        
        if current_qty > 0:
            self.update_inventory(capsule_name, current_qty - 1, user_id)
            return True
        return False
    
    # ========== 抽取历史 ==========
    def add_pick_history(self, capsule_name, preference=None, user_id='default_user'):
        """记录抽取历史"""
        data = {
            'user_id': user_id,
            'capsule_name': capsule_name,
            'preference_used': json.dumps(preference) if preference else None
        }
        self.supabase.table('pick_history').insert(data).execute()
    
    def get_pick_history(self, user_id='default_user', limit=10):
        """获取最近的抽取历史"""
        response = self.supabase.table('pick_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('picked_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    
    # ========== 用户设置 ==========
    def get_user_settings(self, user_id='default_user'):
        """获取用户设置"""
        response = self.supabase.table('app_settings')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if response.data:
            return response.data[0]
        else:
            # 创建默认设置
            default = {'user_id': user_id, 'language': 'en'}
            self.supabase.table('app_settings').insert(default).execute()
            return default
    
    def update_user_settings(self, settings, user_id='default_user'):
        """更新用户设置"""
        settings['updated_at'] = datetime.now().isoformat()
        self.supabase.table('app_settings')\
            .update(settings)\
            .eq('user_id', user_id)\
            .execute()