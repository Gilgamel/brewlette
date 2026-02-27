# 翻译模块
TRANSLATIONS = {
    'en': {
        'app_title': 'Brewlette',
        'welcome': 'Welcome to Brewlette',
        'inventory': 'My Inventory',
        'preferences': 'Today\'s Preferences',
        'pick_button': 'Pick a Pod for Me!',
        'result': 'Today\'s Pick',
        'quantity': 'Quantity',
        'pod_name': 'Pod Name',
        'size': 'Size',
        'tasting_notes': 'Tasting Notes',
        'add_pod': 'Add/Update Pod',
        'language': 'Language',
        'no_preference': 'No Preference',
        'powered_by': 'Powered by Gilgamel',
        'update_inventory': 'Update Inventory',
        'confirm_pick': 'Confirm Pick',
        'remaining': 'Remaining',
        'last_update': 'Last Updated',
        'select_size': 'Select Size',
        'intensity': 'Intensity',
        'history': 'Pick History'
    },
    'zh': {
        'app_title': '随便喝',
        'welcome': '欢迎使用随便喝',
        'inventory': '我的胶囊库存',
        'preferences': '今日偏好',
        'pick_button': '为我抽取胶囊！',
        'result': '今日推荐',
        'quantity': '数量',
        'pod_name': '胶囊名称',
        'size': '容量',
        'tasting_notes': '品尝笔记',
        'add_pod': '添加/更新胶囊',
        'language': '语言',
        'no_preference': '无偏好',
        'powered_by': 'Powered by Gilgamel',
        'update_inventory': '更新库存',
        'confirm_pick': '确认抽取',
        'remaining': '剩余',
        'last_update': '最后更新',
        'select_size': '选择容量',
        'intensity': '浓度',
        'history': '抽取历史'
    }
}

class Translator:
    def __init__(self, language='en'):
        self.language = language
        self.translations = TRANSLATIONS
    
    def set_language(self, language):
        if language in self.translations:
            self.language = language
    
    def t(self, key):
        return self.translations[self.language].get(key, key)