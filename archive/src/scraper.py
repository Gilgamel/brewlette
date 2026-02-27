# src/supabase_db.py - 使用存储过程版本
import os
import requests
import json
from datetime import datetime
import logging
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("请设置 SUPABASE_URL 和 SUPABASE_KEY 环境变量")
        
        # 确保URL格式正确
        if not self.url.startswith('https://'):
            self.url = f'https://{self.url}'
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        logger.info(f"Supabase客户端初始化成功: {self.url}")
    
    def _request(self, method, table, params=None, data=None):
        """发送HTTP请求到Supabase"""
        url = f"{self.url}/rest/v1/{table}"
        
        # 构建查询参数
        if params:
            param_parts = []
            for key, value in params.items():
                if value is not None:
                    param_parts.append(f"{key}=eq.{value}")
            if param_parts:
                url = f"{url}?{'&'.join(param_parts)}"
        
        try:
            logger.debug(f"发送请求: {method} {url}")
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code >= 400:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
            
            if method.upper() == "DELETE":
                return {"success": True}
            
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None
    
    def _rpc_call(self, function_name, params):
        """调用Supabase RPC函数"""
        url = f"{self.url}/rest/v1/rpc/{function_name}"
        
        try:
            logger.info(f"调用RPC: {function_name}, 参数: {params}")
            response = requests.post(
                url,
                headers=self.headers,
                json=params,
                timeout=10
            )
            
            if response.status_code >= 400:
                logger.error(f"RPC调用失败 {response.status_code}: {response.text}")
                return None
            
            return response.json() if response.content else {"success": True}
            
        except Exception as e:
            logger.error(f"RPC调用异常: {e}")
            return None
    
    # ========== 胶囊管理 ==========
    
    def get_all_capsules(self):
        """获取所有胶囊"""
        result = self._request("GET", "capsules")
        if result is None:
            # 返回默认数据
            return self._get_default_capsules()
        return result
    
    def _get_default_capsules(self):
        """返回默认胶囊数据（当数据库为空时）"""
        return [
            {
                'name': 'ristretto',
                'display_name_en': 'Ristretto',
                'display_name_zh': '芮斯崔朵',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Intense and powerful with cocoa notes',
                'tasting_notes_zh': '浓烈强劲，带有可可香气',
                'intensity': 10,
                'image_url': ''
            },
            {
                'name': 'volluto',
                'display_name_en': 'Volluto',
                'display_name_zh': '沃鲁托',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Sweet and biscuity with fruity notes',
                'tasting_notes_zh': '甜美饼干风味，带有果香',
                'intensity': 4,
                'image_url': ''
            },
            {
                'name': 'livanto',
                'display_name_en': 'Livanto',
                'display_name_zh': '利凡托',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Balanced and rounded with caramel notes',
                'tasting_notes_zh': '平衡圆润，带有焦糖风味',
                'intensity': 6,
                'image_url': ''
            },
            {
                'name': 'roma',
                'display_name_en': 'Roma',
                'display_name_zh': '罗马',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Full and balanced with woody notes',
                'tasting_notes_zh': '饱满平衡，带有木质香气',
                'intensity': 8,
                'image_url': ''
            },
            {
                'name': 'vanilio',
                'display_name_en': 'Vanilio',
                'display_name_zh': '香草',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Sweet vanilla aroma',
                'tasting_notes_zh': '甜美的香草香气',
                'intensity': 5,
                'image_url': ''
            },
            {
                'name': 'caramelito',
                'display_name_en': 'Caramelito',
                'display_name_zh': '焦糖',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Sweet caramel notes',
                'tasting_notes_zh': '甜美的焦糖风味',
                'intensity': 6,
                'image_url': ''
            },
            {
                'name': 'ciocattino',
                'display_name_en': 'Ciocattino',
                'display_name_zh': '巧克力',
                'size_ml': 40,
                'size_category': 'espresso',
                'type': 'original',
                'tasting_notes_en': 'Rich chocolate flavor',
                'tasting_notes_zh': '浓郁的巧克力风味',
                'intensity': 8,
                'image_url': ''
            }
        ]
    
    def get_capsule_by_name(self, name):
        """根据名称获取胶囊"""
        result = self._request("GET", "capsules", {"name": name})
        if result and len(result) > 0:
            return result[0]
        return None
    
    # ========== 库存管理 - 使用存储过程 ==========
    
    def get_inventory(self, user_id='default_user'):
        """获取用户库存 - 使用RPC"""
        try:
            # 方法1: 使用存储过程
            result = self._rpc_call('get_inventory', {'p_user_id': user_id})
            
            if result is not None:
                inventory = {}
                for item in result:
                    inventory[item['capsule_name']] = item['quantity']
                return inventory
            
            # 方法2: 如果RPC失败，回退到直接查询
            result = self._request("GET", "user_inventory", {"user_id": user_id})
            
            inventory = {}
            if result:
                for item in result:
                    inventory[item['capsule_name']] = item['quantity']
            
            return inventory
            
        except Exception as e:
            logger.error(f"获取库存失败: {e}")
            return {}
    
    def update_inventory(self, capsule_name, quantity, user_id='default_user'):
        """更新库存 - 使用upsert存储过程"""
        try:
            # 使用存储过程
            result = self._rpc_call('upsert_inventory', {
                'p_user_id': user_id,
                'p_capsule_name': capsule_name,
                'p_quantity': quantity
            })
            
            if result is not None:
                logger.info(f"库存更新成功: {capsule_name} = {quantity}")
                return True
            else:
                logger.error(f"库存更新失败: {capsule_name}")
                return False
                
        except Exception as e:
            logger.error(f"更新库存异常: {e}")
            return False
    
    def add_to_inventory(self, capsule_name, quantity_to_add, user_id='default_user'):
        """添加胶囊到库存 - 使用存储过程"""
        try:
            # 使用存储过程
            result = self._rpc_call('add_to_inventory', {
                'p_user_id': user_id,
                'p_capsule_name': capsule_name,
                'p_quantity_to_add': quantity_to_add
            })
            
            if result is not None:
                logger.info(f"添加库存成功: {capsule_name} +{quantity_to_add}, 现库存: {result}")
                return True
            else:
                # 如果RPC失败，回退到手动计算
                inventory = self.get_inventory(user_id)
                current_qty = inventory.get(capsule_name, 0)
                new_qty = current_qty + quantity_to_add
                return self.update_inventory(capsule_name, new_qty, user_id)
                
        except Exception as e:
            logger.error(f"添加库存异常: {e}")
            return False
    
    def consume_pod(self, capsule_name, user_id='default_user'):
        """消耗一个胶囊 - 使用存储过程"""
        try:
            # 使用存储过程
            result = self._rpc_call('consume_pod', {
                'p_user_id': user_id,
                'p_capsule_name': capsule_name
            })
            
            if result is True:
                logger.info(f"消耗胶囊成功: {capsule_name}")
                return True
            elif result is False:
                logger.warning(f"胶囊库存不足: {capsule_name}")
                return False
            else:
                # 如果RPC失败，回退到手动消耗
                inventory = self.get_inventory(user_id)
                current_qty = inventory.get(capsule_name, 0)
                
                if current_qty > 0:
                    return self.update_inventory(capsule_name, current_qty - 1, user_id)
                return False
                
        except Exception as e:
            logger.error(f"消耗胶囊异常: {e}")
            return False
    
    # ========== 抽取历史 ==========
    
    def add_pick_history(self, capsule_name, preference=None, user_id='default_user'):
        """记录抽取历史"""
        try:
            data = {
                'user_id': user_id,
                'capsule_name': capsule_name,
                'preference_used': json.dumps(preference) if preference else None,
                'picked_at': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/pick_history",
                headers=self.headers,
                json=data
            )
            
            if response.status_code < 400:
                logger.info(f"记录历史成功: {capsule_name}")
                return True
            else:
                logger.error(f"记录历史失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"记录历史异常: {e}")
            return False
    
    def get_pick_history(self, user_id='default_user', limit=10):
        """获取最近的抽取历史"""
        try:
            url = f"{self.url}/rest/v1/pick_history"
            url += f"?user_id=eq.{user_id}&order=picked_at.desc&limit={limit}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code < 400:
                return response.json()
            return []
            
        except Exception as e:
            logger.error(f"获取历史失败: {e}")
            return []
    
    # ========== 用户设置 ==========
    
    def get_user_settings(self, user_id='default_user'):
        """获取用户设置"""
        try:
            result = self._request("GET", "app_settings", {"user_id": user_id})
            
            if result and len(result) > 0:
                return result[0]
            else:
                # 创建默认设置
                default = {
                    'user_id': user_id,
                    'language': 'en',
                    'created_at': datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.url}/rest/v1/app_settings",
                    headers=self.headers,
                    json=default
                )
                
                if response.status_code < 400:
                    return default
                else:
                    return {'user_id': user_id, 'language': 'en'}
                    
        except Exception as e:
            logger.error(f"获取设置失败: {e}")
            return {'user_id': user_id, 'language': 'en'}
    
    def update_user_settings(self, settings, user_id='default_user'):
        """更新用户设置"""
        try:
            settings['updated_at'] = datetime.now().isoformat()
            
            url = f"{self.url}/rest/v1/app_settings?user_id=eq.{user_id}"
            
            response = requests.patch(
                url,
                headers=self.headers,
                json=settings
            )
            
            return response.status_code < 400
            
        except Exception as e:
            logger.error(f"更新设置失败: {e}")
            return False
    
    # ========== 初始化数据 ==========
    
    def initialize_default_capsules(self):
        """初始化默认胶囊数据到数据库"""
        try:
            default_capsules = self._get_default_capsules()
            
            for capsule in default_capsules:
                # 检查是否已存在
                existing = self.get_capsule_by_name(capsule['name'])
                if not existing:
                    # 插入
                    response = requests.post(
                        f"{self.url}/rest/v1/capsules",
                        headers=self.headers,
                        json=capsule
                    )
                    
                    if response.status_code < 400:
                        logger.info(f"初始化胶囊: {capsule['name']}")
                    else:
                        logger.error(f"初始化失败: {capsule['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化默认胶囊失败: {e}")
            return False