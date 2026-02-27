"""
Translator Module
Handles Chinese/English translations for the app
"""

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # App title
        "app_title": "Nespresso Pod Picker",
        
        # User section
        "select_user": "Select User",
        "create_user": "Create New User",
        "enter_username": "Enter username",
        "create": "Create",
        "welcome": "Welcome",
        
        # Navigation
        "tab_random": "Random Pick",
        "tab_inventory": "My Inventory",
        "tab_admin": "Admin",
        
        # Random picker
        "preference": "Today's Preference",
        "no_preference": "No Preference (Random)",
        "espresso_40ml": "Espresso (40ml)",
        "double_80ml": "Double Espresso (80ml)",
        "lungo_150ml": "Lungo (150ml)",
        "coffee_230ml": "Coffee (230ml)",
        "alto_400ml": "Alto (400ml)",
        "pick_random": "🎲 Pick Random Pod",
        "result": "Your Pick!",
        "confirm": "✓ Confirm & Drink",
        "skip": "Skip",
        "confirm_success": "Confirmed! Enjoy your coffee! ☕",
        "remaining": "Remaining",
        
        # Inventory
        "my_inventory": "My Inventory",
        "add_capsule": "Add Capsule",
        "select_capsule": "Select capsule",
        "enter_quantity": "Quantity",
        "add": "Add",
        "update": "Update",
        "delete": "Delete",
        "capsule_name": "Capsule Name",
        "quantity": "Quantity",
        "size": "Size",
        "type": "Type",
        "line": "Line",
        "no_inventory": "No capsules in inventory. Add some first!",
        
        # Admin
        "admin_panel": "Admin Panel",
        "update_capsules": "Update Capsule Data",
        "update_btn": "🔄 Update Now",
        "updating": "Updating capsule data...",
        "update_success": "Capsule data updated successfully!",
        "update_error": "Error updating capsule data",
        "total_capsules": "Total capsules in database",
        "last_update": "Last updated",
        
        # Footer
        "powered_by": "Powered by",
        
        # Messages
        "no_pods_available": "No pods available with this preference",
        "need_inventory": "Please add capsules to your inventory first",
        "user_created": "User created successfully",
        "capsule_added": "Capsule added to inventory",
        "capsule_updated": "Inventory updated",
        "capsule_deleted": "Capsule removed from inventory",
    },
    "zh": {
        # App title
        "app_title": "Nespresso 胶囊抽取器",
        
        # User section
        "select_user": "选择用户",
        "create_user": "创建新用户",
        "enter_username": "输入用户名",
        "create": "创建",
        "welcome": "欢迎",
        
        # Navigation
        "tab_random": "随机抽取",
        "tab_inventory": "我的库存",
        "tab_admin": "管理",
        
        # Random picker
        "preference": "今天的需求",
        "no_preference": "没有特殊偏好 (随机)",
        "espresso_40ml": "浓缩咖啡 (40ml)",
        "double_80ml": "双份浓缩 (80ml)",
        "lungo_150ml": "大杯咖啡 (150ml)",
        "coffee_230ml": "美式咖啡 (230ml)",
        "alto_400ml": "超大杯 (400ml)",
        "pick_random": "🎲 随机抽取胶囊",
        "result": "您抽中了！",
        "confirm": "✓ 确认冲泡",
        "skip": "跳过",
        "confirm_success": "已确认！享受您的咖啡吧！☕",
        "remaining": "剩余",
        
        # Inventory
        "my_inventory": "我的库存",
        "add_capsule": "添加胶囊",
        "select_capsule": "选择胶囊",
        "enter_quantity": "数量",
        "add": "添加",
        "update": "更新",
        "delete": "删除",
        "capsule_name": "胶囊名称",
        "quantity": "数量",
        "size": "容量",
        "type": "类型",
        "line": "系列",
        "no_inventory": "库存中没有胶囊，请先添加！",
        
        # Admin
        "admin_panel": "管理面板",
        "update_capsules": "更新胶囊数据",
        "update_btn": "🔄 立即更新",
        "updating": "正在更新胶囊数据...",
        "update_success": "胶囊数据更新成功！",
        "update_error": "更新胶囊数据时出错",
        "total_capsules": "数据库中的胶囊总数",
        "last_update": "最后更新",
        
        # Footer
        "powered_by": "技术支持",
        
        # Messages
        "no_pods_available": "没有符合您偏好的胶囊",
        "need_inventory": "请先在库存中添加胶囊",
        "user_created": "用户创建成功",
        "capsule_added": "胶囊已添加到库存",
        "capsule_updated": "库存已更新",
        "capsule_deleted": "胶囊已从库存中移除",
    }
}

# Pod type translations
POD_TYPE_TRANSLATIONS = {
    "en": {
        "espresso": "Espresso",
        "double": "Double Espresso",
        "lungo": "Lungo",
        "coffee": "Coffee",
        "alto": "Alto",
    },
    "zh": {
        "espresso": "浓缩咖啡",
        "double": "双份浓缩",
        "lungo": "大杯咖啡",
        "coffee": "美式咖啡",
        "alto": "超大杯",
    }
}

# Line translations
LINE_TRANSLATIONS = {
    "en": {
        "Original": "Original Line",
        "Vertuo": "Vertuo Line",
    },
    "zh": {
        "Original": "Original 系列",
        "Vertuo": "Vertuo 系列",
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """Get translated text by key"""
    lang = lang if lang in TRANSLATIONS else "en"
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def get_pod_type(key: str, lang: str = "en") -> str:
    """Get translated pod type"""
    lang = lang if lang in POD_TYPE_TRANSLATIONS else "en"
    return POD_TYPE_TRANSLATIONS.get(lang, POD_TYPE_TRANSLATIONS["en"]).get(key, key)


def get_line(key: str, lang: str = "en") -> str:
    """Get translated line name"""
    lang = lang if lang in LINE_TRANSLATIONS else "en"
    return LINE_TRANSLATIONS.get(lang, LINE_TRANSLATIONS["en"]).get(key, key)


def translate_capsule(capsule: dict, lang: str = "en") -> dict:
    """
    Translate capsule fields based on language
    Returns a new dictionary with translated fields
    """
    if lang == "zh":
        return {
            "name": capsule.get("name_en", capsule.get("name", "")),
            "tasting_note": capsule.get("tasting_note_en", capsule.get("tasting_note", "")),
            "size_ml": capsule.get("size_ml"),
            "pod_type": get_pod_type(capsule.get("pod_type", "espresso"), "zh"),
            "line": get_line(capsule.get("line", "Original"), "zh"),
            "intensity": capsule.get("intensity"),
            # Keep original IDs
            "id": capsule.get("id"),
        }
    else:
        return {
            "name": capsule.get("name_en", capsule.get("name", "")),
            "tasting_note": capsule.get("tasting_note_en", capsule.get("tasting_note", "")),
            "size_ml": capsule.get("size_ml"),
            "pod_type": get_pod_type(capsule.get("pod_type", "espresso"), "en"),
            "line": get_line(capsule.get("line", "Original"), "en"),
            "intensity": capsule.get("intensity"),
            "id": capsule.get("id"),
        }
