// ==================== State Management ====================
const state = {
    language: 'en',
    currentTab: 'pick',
    capsules: [],
    filteredCapsules: [],
    user: null,
    inventory: {},
    selectedSize: null,
    selectedLines: { Original: true, Vertuo: true },
    currentResult: null,
    managingCapsuleId: null
};

// ==================== Supabase Configuration ====================
// Note: Replace with your actual Supabase credentials
const SUPABASE_URL = localStorage.getItem('supabase_url') || '';
const SUPABASE_KEY = localStorage.getItem('supabase_key') || '';

// ==================== DOM Elements ====================
const elements = {
    langToggle: document.getElementById('langToggle'),
    langLabel: document.getElementById('langLabel'),
    userBtn: document.getElementById('userBtn'),
    tabs: document.querySelectorAll('.tab'),
    tabContents: document.querySelectorAll('.tab-content'),
    sizeButtons: document.querySelectorAll('.size-btn'),
    originalLine: document.getElementById('originalLine'),
    vertuoLine: document.getElementById('vertuoLine'),
    pickBtn: document.getElementById('pickBtn'),
    result: document.getElementById('result'),
    resultName: document.getElementById('resultName'),
    resultLine: document.getElementById('resultLine'),
    resultSize: document.getElementById('resultSize'),
    resultIntensity: document.getElementById('resultIntensity'),
    resultNote: document.getElementById('resultNote'),
    confirmBtn: document.getElementById('confirmBtn'),
    rerollBtn: document.getElementById('rerollBtn'),
    emptyFilter: document.getElementById('emptyFilter'),
    inventoryList: document.getElementById('inventoryList'),
    totalCapsules: document.getElementById('totalCapsules'),
    emptyInventory: document.getElementById('emptyInventory'),
    inventoryManagement: document.getElementById('inventoryManagement'),
    manageCapsuleName: document.getElementById('manageCapsuleName'),
    manageQty: document.getElementById('manageQty'),
    closeManage: document.getElementById('closeManage'),
    qtyMinus: document.getElementById('qtyMinus'),
    qtyPlus: document.getElementById('qtyPlus'),
    deleteCapsule: document.getElementById('deleteCapsule'),
    searchCapsules: document.getElementById('searchCapsules'),
    filterLine: document.getElementById('filterLine'),
    filterType: document.getElementById('filterType'),
    capsulesList: document.getElementById('capsulesList'),
    emptyCapsules: document.getElementById('emptyCapsules'),
    userModal: document.getElementById('userModal'),
    modalTitle: document.getElementById('modalTitle'),
    userForm: document.getElementById('userForm'),
    userProfile: document.getElementById('userProfile'),
    userName: document.getElementById('userName'),
    userEmail: document.getElementById('userEmail'),
    saveUser: document.getElementById('saveUser'),
    profileAvatar: document.getElementById('profileAvatar'),
    profileName: document.getElementById('profileName'),
    profileEmail: document.getElementById('profileEmail'),
    logoutBtn: document.getElementById('logoutBtn'),
    closeUserModal: document.getElementById('closeUserModal'),
    toast: document.getElementById('toast'),
    installPrompt: document.getElementById('installPrompt'),
    installBtn: document.getElementById('installBtn'),
    dismissInstall: document.getElementById('dismissInstall')
};

// ==================== Initialization ====================
async function init() {
    // Load capsules data
    await loadCapsulesData();

    // Load user data
    loadUserData();

    // Load inventory
    loadInventory();

    // Setup event listeners
    setupEventListeners();

    // Register service worker
    registerServiceWorker();

    // Check for install prompt
    checkInstallPrompt();

    // Render initial UI
    renderInventory();
    renderCapsulesGrid();

    // Apply saved language
    applyLanguage(state.language);
}

// ==================== Data Loading ====================
async function loadCapsulesData() {
    try {
        // Try to load from local file first (for development)
        const response = await fetch('../data/capsules.json');
        if (response.ok) {
            const data = await response.json();
            state.capsules = data.capsules || [];
        } else {
            // Fallback to embedded sample data
            state.capsules = getSampleCapsules();
        }
    } catch (error) {
        console.log('Using sample capsules data');
        state.capsules = getSampleCapsules();
    }

    state.filteredCapsules = [...state.capsules];
}

function getSampleCapsules() {
    return [
        { id: 'orig-001', name: 'Ristretto', name_en: 'Ristretto', name_zh: '瑞斯崔朵', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 10, tasting_note_en: 'Intense and roasted', tasting_note_zh: '浓郁烘烤', color: '#6B3A3A' },
        { id: 'orig-002', name: 'Arpeggio', name_en: 'Arpeggio', name_zh: '琶音', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 9, tasting_note_en: 'Intense with cocoa', tasting_note_zh: '浓郁可可', color: '#4A3728' },
        { id: 'orig-003', name: 'Roma', name_en: 'Roma', name_zh: '罗马', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Balanced with woody', tasting_note_zh: '平衡木质', color: '#5C4033' },
        { id: 'orig-004', name: 'Livanto', name_en: 'Livanto', name_zh: '利凡托', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Round with caramel', tasting_note_zh: '圆润焦糖', color: '#8B6914' },
        { id: 'orig-005', name: 'Kazaar', name_en: 'Kazaar', name_zh: '卡扎尔', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 12, tasting_note_en: 'Exceptionally intense', tasting_note_zh: '极致浓郁', color: '#3D2314' },
        { id: 'orig-006', name: 'India', name_en: 'India', name_zh: '印度', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 11, tasting_note_en: 'Intense and spicy', tasting_note_zh: '浓郁辛辣', color: '#5C4033' },
        { id: 'orig-007', name: 'Ethiopia', name_en: 'Ethiopia', name_zh: '埃塞俄比亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 4, tasting_note_en: 'Floral and fruity', tasting_note_zh: '花香果香', color: '#9B7B5B' },
        { id: 'orig-008', name: 'Colombia', name_en: 'Colombia', name_zh: '哥伦比亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Balanced with caramel', tasting_note_zh: '平衡焦糖', color: '#7A6B5A' },
        { id: 'vert-001', name: 'Diavoletto', name_en: 'Diavoletto', name_zh: '小恶魔', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Rich with cocoa', tasting_note_zh: '浓郁可可', color: '#5C3020' },
        { id: 'vert-002', name: 'Stormio', name_en: 'Stormio', name_zh: '风暴', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 8, tasting_note_en: 'Rich and full-bodied', tasting_note_zh: '浓郁醇厚', color: '#5C4033' },
        { id: 'vert-003', name: 'Melozio', name_en: 'Melozio', name_zh: '旋律', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Smooth with cereal', tasting_note_zh: '顺滑谷物', color: '#8B7B6B' },
        { id: 'vert-004', name: 'Altissimo', name_en: 'Altissimo', name_zh: '至高', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 11, tasting_note_en: 'Exceptionally intense', tasting_note_zh: '极致浓郁', color: '#2D1B0F' },
        { id: 'vert-005', name: 'Fortado', name_en: 'Fortado', name_zh: '强劲', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 8, tasting_note_en: 'Rich and full-bodied', tasting_note_zh: '浓郁醇厚', color: '#5C4033' },
        { id: 'vert-006', name: 'Vanilio', name_en: 'Vanilio', name_zh: '香草', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Sweet vanilla', tasting_note_zh: '甜蜜香草', color: '#9B8B6B' }
    ];
}

// ==================== User Data ====================
function loadUserData() {
    const savedUser = localStorage.getItem('nespresso_user');
    if (savedUser) {
        state.user = JSON.parse(savedUser);
    }

    const savedLang = localStorage.getItem('nespresso_lang');
    if (savedLang) {
        state.language = savedLang;
    }
}

function saveUserData() {
    localStorage.setItem('nespresso_user', JSON.stringify(state.user));
    localStorage.setItem('nespresso_lang', state.language);
}

// ==================== Inventory ====================
function loadInventory() {
    if (state.user) {
        const savedInventory = localStorage.getItem(`nespresso_inventory_${state.user.id}`);
        if (savedInventory) {
            state.inventory = JSON.parse(savedInventory);
        }
    } else {
        // Guest inventory
        const savedInventory = localStorage.getItem('nespresso_inventory_guest');
        if (savedInventory) {
            state.inventory = JSON.parse(savedInventory);
        }
    }
}

function saveInventory() {
    if (state.user) {
        localStorage.setItem(`nespresso_inventory_${state.user.id}`, JSON.stringify(state.inventory));
    } else {
        localStorage.setItem('nespresso_inventory_guest', JSON.stringify(state.inventory));
    }
}

function addToInventory(capsule) {
    if (state.inventory[capsule.id]) {
        state.inventory[capsule.id].quantity++;
    } else {
        state.inventory[capsule.id] = {
            ...capsule,
            quantity: 1
        };
    }
    saveInventory();
    renderInventory();
    showToast(state.language === 'en' ? 'Added to inventory!' : '已添加到库存！', 'success');
}

function updateInventoryQuantity(capsuleId, quantity) {
    if (quantity <= 0) {
        delete state.inventory[capsuleId];
    } else {
        state.inventory[capsuleId].quantity = quantity;
    }
    saveInventory();
    renderInventory();
}

function removeFromInventory(capsuleId) {
    delete state.inventory[capsuleId];
    saveInventory();
    renderInventory();
    closeInventoryManagement();
    showToast(state.language === 'en' ? 'Removed from inventory' : '已从库存中移除', 'success');
}

function getTotalCapsules() {
    return Object.values(state.inventory).reduce((sum, item) => sum + item.quantity, 0);
}

// ==================== Event Listeners ====================
function setupEventListeners() {
    // Language toggle
    elements.langToggle.addEventListener('click', toggleLanguage);

    // Tab switching
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Size filter buttons
    elements.sizeButtons.forEach(btn => {
        btn.addEventListener('click', () => toggleSizeFilter(btn.dataset.size));
    });

    // Line filters
    elements.originalLine.addEventListener('change', updateLineFilter);
    elements.vertuoLine.addEventListener('change', updateLineFilter);

    // Pick button
    elements.pickBtn.addEventListener('click', pickRandomCapsule);

    // Result actions
    elements.confirmBtn.addEventListener('click', confirmPick);
    elements.rerollBtn.addEventListener('click', pickRandomCapsule);

    // Inventory management
    elements.closeManage.addEventListener('click', closeInventoryManagement);
    elements.qtyMinus.addEventListener('click', () => adjustManageQty(-1));
    elements.qtyPlus.addEventListener('click', () => adjustManageQty(1));
    elements.deleteCapsule.addEventListener('click', () => {
        if (state.managingCapsuleId) {
            removeFromInventory(state.managingCapsuleId);
        }
    });

    // Capsules search and filters
    elements.searchCapsules.addEventListener('input', filterCapsules);
    elements.filterLine.addEventListener('change', filterCapsules);
    elements.filterType.addEventListener('change', filterCapsules);

    // User modal
    elements.userBtn.addEventListener('click', openUserModal);
    elements.closeUserModal.addEventListener('click', closeUserModal);
    elements.saveUser.addEventListener('click', saveUser);
    elements.logoutBtn.addEventListener('click', logoutUser);

    // Install prompt
    elements.installBtn.addEventListener('click', installApp);
    elements.dismissInstall.addEventListener('click', dismissInstallPrompt);

    // Click outside modal to close
    elements.userModal.addEventListener('click', (e) => {
        if (e.target === elements.userModal) {
            closeUserModal();
        }
    });
}

// ==================== Tab Switching ====================
function switchTab(tabName) {
    state.currentTab = tabName;

    elements.tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    // Hide result when switching tabs
    if (tabName !== 'pick') {
        elements.result.classList.add('hidden');
    }
}

// ==================== Language ====================
function toggleLanguage() {
    state.language = state.language === 'en' ? 'zh' : 'en';
    applyLanguage(state.language);
    localStorage.setItem('nespresso_lang', state.language);
}

function applyLanguage(lang) {
    state.language = lang;
    elements.langLabel.textContent = lang === 'en' ? 'EN' : '中';

    // Update all elements with data attributes
    document.querySelectorAll('[data-en]').forEach(el => {
        const key = el.dataset[lang];
        if (key) {
            if (el.tagName === 'INPUT') {
                el.placeholder = key;
            } else {
                el.textContent = key;
            }
        }
    });

    // Update specific elements
    document.querySelectorAll('[data-placeholder-en]').forEach(el => {
        el.placeholder = lang === 'en' ? el.dataset.placeholderEn : el.dataset.placeholderZh;
    });

    // Update select options
    document.querySelectorAll('select option[data-en]').forEach(option => {
        option.textContent = lang === 'en' ? option.dataset.en : option.dataset.zh;
    });

    // Update dynamic content
    renderInventory();
    renderCapsulesGrid();

    if (state.currentResult) {
        displayResult(state.currentResult);
    }
}

// ==================== Filters ====================
function toggleSizeFilter(size) {
    if (state.selectedSize === size) {
        state.selectedSize = null;
    } else {
        state.selectedSize = size;
    }

    elements.sizeButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.size === state.selectedSize);
    });
Filter() {
   }

function updateLine state.selectedLines.Original = elements.originalLine.checked;
    state.selectedLines.Vertuo = elements.vertuoLine.checked;
}

function filterCapsules() {
    const search = elements.searchCapsules.value.toLowerCase();
    const lineFilter = elements.filterLine.value;
    const typeFilter = elements.filterType.value;

    state.filteredCapsules = state.capsules.filter(capsule => {
        // Search filter
        const name = capsule.name_en?.toLowerCase() || capsule.name?.toLowerCase() || '';
        const nameZh = capsule.name_zh || '';
        if (search && !name.includes(search) && !nameZh.includes(search)) {
            return false;
        }

        // Line filter
        if (lineFilter !== 'all' && capsule.line !== lineFilter) {
            return false;
        }

        // Type filter
        if (typeFilter !== 'all' && capsule.pod_type !== typeFilter) {
            return false;
        }

        return true;
    });

    renderCapsulesGrid();
}

function getFilteredCapsules() {
    return state.capsules.filter(capsule => {
        // Size filter
        if (state.selectedSize && capsule.pod_type !== state.selectedSize) {
            return false;
        }

        // Line filter
        if (!state.selectedLines[capsule.line]) {
            return false;
        }

        return true;
    });
}

// ==================== Pick Random ====================
function pickRandomCapsule() {
    const available = getFilteredCapsules();

    if (available.length === 0) {
        elements.emptyFilter.classList.remove('hidden');
        elements.result.classList.add('hidden');
        return;
    }

    elements.emptyFilter.classList.add('hidden');

    // Random selection
    const randomIndex = Math.floor(Math.random() * available.length);
    const selected = available[randomIndex];

    state.currentResult = selected;
    displayResult(selected);
}

function displayResult(capsule) {
    const lang = state.language;

    elements.resultName.textContent = lang === 'zh' ? (capsule.name_zh || capsule.name_en) : capsule.name_en;

    elements.resultLine.textContent = capsule.line;
    elements.resultSize.textContent = `${capsule.size_ml}ml`;
    elements.resultIntensity.textContent = capsule.intensity ? `Intensity ${capsule.intensity}` : '';

    const note = lang === 'zh' ? capsule.tasting_note_zh : capsule.tasting_note_en;
    elements.resultNote.textContent = note || '';

    elements.result.classList.remove('hidden');

    // Scroll to result
    elements.result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function confirmPick() {
    if (state.currentResult) {
        addToInventory(state.currentResult);
        elements.result.classList.add('hidden');
        state.currentResult = null;
    }
}

// ==================== Inventory Rendering ====================
function renderInventory() {
    const items = Object.values(state.inventory);

    // Update total
    elements.totalCapsules.textContent = getTotalCapsules();

    if (items.length === 0) {
        elements.emptyInventory.classList.remove('hidden');
        elements.inventoryList.innerHTML = '';
        elements.inventoryList.appendChild(elements.emptyInventory);
        return;
    }

    elements.emptyInventory.classList.add('hidden');

    const html = items.map(item => `
        <div class="inventory-item" data-id="${item.id}">
            <div class="inventory-item-left">
                <div class="inventory-color" style="background: ${item.color || '#6B5344'}"></div>
                <div>
                    <div class="inventory-name">${state.language === 'zh' ? (item.name_zh || item.name_en) : item.name_en}</div>
                    <div class="inventory-details">${item.line} | ${item.size_ml}ml</div>
                </div>
            </div>
            <div class="inventory-qty">
                <span class="qty-badge">${item.quantity}</span>
            </div>
        </div>
    `).join('');

    elements.inventoryList.innerHTML = html;

    // Add click handlers
    elements.inventoryList.querySelectorAll('.inventory-item').forEach(item => {
        item.addEventListener('click', () => openInventoryManagement(item.dataset.id));
    });
}

function openInventoryManagement(capsuleId) {
    const item = state.inventory[capsuleId];
    if (!item) return;

    state.managingCapsuleId = capsuleId;
    elements.manageCapsuleName.textContent = state.language === 'zh' ? (item.name_zh || item.name_en) : item.name_en;
    elements.manageQty.textContent = item.quantity;
    elements.inventoryManagement.classList.remove('hidden');
}

function closeInventoryManagement() {
    state.managingCapsuleId = null;
    elements.inventoryManagement.classList.add('hidden');
}

function adjustManageQty(delta) {
    if (!state.managingCapsuleId) return;

    const current = state.inventory[state.managingCapsuleId].quantity;
    const newQty = Math.max(0, current + delta);

    updateInventoryQuantity(state.managingCapsuleId, newQty);

    if (newQty > 0) {
        elements.manageQty.textContent = newQty;
    } else {
        closeInventoryManagement();
    }
}

// ==================== Capsules Grid Rendering ====================
function renderCapsulesGrid() {
    const capsules = state.filteredCapsules;

    if (capsules.length === 0) {
        elements.emptyCapsules.classList.remove('hidden');
        elements.capsulesList.innerHTML = '';
        return;
    }

    elements.emptyCapsules.classList.add('hidden');

    const html = capsules.map(capsule => `
        <div class="capsule-card" data-id="${capsule.id}">
            <div class="capsule-color-bar" style="background: ${capsule.color || '#6B5344'}"></div>
            <div class="capsule-name">${state.language === 'zh' ? (capsule.name_zh || capsule.name_en) : capsule.name_en}</div>
            <div class="capsule-meta">
                <span class="capsule-line">${capsule.line}</span>
                <span>${capsule.size_ml}ml | ${capsule.pod_type}</span>
                ${capsule.intensity ? `<span>Intensity: ${capsule.intensity}</span>` : ''}
            </div>
        </div>
    `).join('');

    elements.capsulesList.innerHTML = html;

    // Add click to add to inventory
    elements.capsulesList.querySelectorAll('.capsule-card').forEach(card => {
        card.addEventListener('click', () => {
            const capsule = state.capsules.find(c => c.id === card.dataset.id);
            if (capsule) {
                addToInventory(capsule);
            }
        });
    });
}

// ==================== User Modal ====================
function openUserModal() {
    elements.userModal.classList.remove('hidden');

    if (state.user) {
        elements.modalTitle.textContent = state.language === 'en' ? 'User Profile' : '用户资料';
        elements.userForm.classList.add('hidden');
        elements.userProfile.classList.remove('hidden');
        elements.profileAvatar.textContent = state.user.name?.charAt(0).toUpperCase() || 'U';
        elements.profileName.textContent = state.user.name || 'User';
        elements.profileEmail.textContent = state.user.email || '';
    } else {
        elements.modalTitle.textContent = state.language === 'en' ? 'Welcome!' : '欢迎！';
        elements.userForm.classList.remove('hidden');
        elements.userProfile.classList.add('hidden');
        elements.userName.value = '';
        elements.userEmail.value = '';
    }
}

function closeUserModal() {
    elements.userModal.classList.add('hidden');
}

function saveUser() {
    const name = elements.userName.value.trim();
    const email = elements.userEmail.value.trim();

    if (!name) {
        showToast(state.language === 'en' ? 'Please enter a name' : '请输入名称', 'error');
        return;
    }

    state.user = {
        id: Date.now().toString(),
        name: name,
        email: email
    };

    saveUserData();
    loadInventory();
    renderInventory();
    closeUserModal();
    showToast(state.language === 'en' ? 'Profile saved!' : '资料已保存！', 'success');
}

function logoutUser() {
    state.user = null;
    state.inventory = {};
    localStorage.removeItem('nespresso_user');
    localStorage.removeItem('nespresso_inventory_guest');
    saveUserData();
    renderInventory();
    closeUserModal();
    showToast(state.language === 'en' ? 'Logged out' : '已退出登录', 'success');
}

// ==================== Toast ====================
function showToast(message, type = '') {
    elements.toast.textContent = message;
    elements.toast.className = 'toast';
    if (type) {
        elements.toast.classList.add(type);
    }
    elements.toast.classList.remove('hidden');

    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 2500);
}

// ==================== Service Worker ====================
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    }
}

// ==================== Install Prompt ====================
let deferredPrompt;

function checkInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        elements.installPrompt.classList.remove('hidden');
    });

    window.addEventListener('appinstalled', () => {
        elements.installPrompt.classList.add('hidden');
        deferredPrompt = null;
    });
}

function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
    }
}

function dismissInstallPrompt() {
    elements.installPrompt.classList.add('hidden');
}

// ==================== Start App ====================
document.addEventListener('DOMContentLoaded', init);
