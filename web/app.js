// ==================== State Management ====================
const state = {
    language: 'en',
    currentTab: 'pick',
    capsules: [],
    filteredCapsules: [],
    user: null,
    isLoggedIn: false,
    inventory: {},
    selectedSize: null,
    selectedLines: { Original: true, Vertuo: true },
    currentResult: null,
    managingCapsuleId: null,
    // Admin state
    isAdmin: false,
    adminBrands: [],
    adminCapsules: [],
    editingCapsuleId: null,
    // Batch operations state
    selectedCapsules: new Set()
};

// ==================== DOM Elements ====================
const elements = {
    langToggle: document.getElementById('langToggle'),
    refreshBtn: document.getElementById('refreshBtn'),
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
    loginModal: document.getElementById('loginModal'),
    loginUsername: document.getElementById('loginUsername'),
    loginPassword: document.getElementById('loginPassword'),
    loginBtn: document.getElementById('loginBtn'),
    registerBtn: document.getElementById('registerBtn'),
    skipLoginBtn: document.getElementById('skipLoginBtn'),
    closeLoginModal: document.getElementById('closeLoginModal'),
    userModal: document.getElementById('userModal'),
    profileAvatar: document.getElementById('profileAvatar'),
    profileName: document.getElementById('profileName'),
    logoutBtn: document.getElementById('logoutBtn'),
    closeUserModal: document.getElementById('closeUserModal'),
    toast: document.getElementById('toast'),
    installPrompt: document.getElementById('installPrompt'),
    installBtn: document.getElementById('installBtn'),
    dismissInstall: document.getElementById('dismissInstall'),
    // Admin elements
    adminTab: document.getElementById('adminTab'),
    adminPasswordModal: document.getElementById('adminPasswordModal'),
    adminPasswordInput: document.getElementById('adminPasswordInput'),
    verifyAdminPasswordBtn: document.getElementById('verifyAdminPasswordBtn'),
    closeAdminPasswordModal: document.getElementById('closeAdminPasswordModal'),
    brandsList: document.getElementById('brandsList'),
    newBrandName: document.getElementById('newBrandName'),
    addBrandBtn: document.getElementById('addBrandBtn'),
    adminFilterBrand: document.getElementById('adminFilterBrand'),
    adminFilterLine: document.getElementById('adminFilterLine'),
    clearAllCapsulesBtn: document.getElementById('clearAllCapsulesBtn'),
    addCapsuleBtn: document.getElementById('addCapsuleBtn'),
    adminCapsulesBody: document.getElementById('adminCapsulesBody'),
    emptyAdminCapsules: document.getElementById('emptyAdminCapsules'),
    capsuleEditModal: document.getElementById('capsuleEditModal'),
    capsuleEditTitle: document.getElementById('capsuleEditTitle'),
    capsuleEditForm: document.getElementById('capsuleEditForm'),
    capsuleEditId: document.getElementById('capsuleEditId'),
    capsuleEditBrand: document.getElementById('capsuleEditBrand'),
    capsuleEditName: document.getElementById('capsuleEditName'),
    capsuleEditLine: document.getElementById('capsuleEditLine'),
    capsuleEditBestServe: document.getElementById('capsuleEditBestServe'),
    capsuleEditSize: document.getElementById('capsuleEditSize'),
    capsuleEditSize2: document.getElementById('capsuleEditSize2'),
    capsuleEditIntensity: document.getElementById('capsuleEditIntensity'),
    capsuleEditTastingNote: document.getElementById('capsuleEditTastingNote'),
    closeCapsuleEditModal: document.getElementById('closeCapsuleEditModal'),
    // Import modal elements
    importModal: document.getElementById('importModal'),
    importJsonText: document.getElementById('importJsonText'),
    importCapsulesBtn: document.getElementById('importCapsulesBtn'),
    closeImportModal: document.getElementById('closeImportModal'),
    importJsonBtn: document.getElementById('importJsonBtn'),
    // Batch action bar
    batchActionBar: document.getElementById('batchActionBar'),
    batchSelectedCount: document.getElementById('batchSelectedCount'),
    batchEditBtn: document.getElementById('batchEditBtn'),
    batchInventoryBtn: document.getElementById('batchInventoryBtn'),
    batchDeleteBtn: document.getElementById('batchDeleteBtn'),
    batchCancelBtn: document.getElementById('batchCancelBtn'),
    // Batch Import Modal
    batchImportBtn: document.getElementById('batchImportBtn'),
    batchImportModal: document.getElementById('batchImportModal'),
    closeBatchImportModal: document.getElementById('closeBatchImportModal'),
    batchImportRows: document.getElementById('batchImportRows'),
    addImportRowBtn: document.getElementById('addImportRowBtn'),
    loadExampleBtn: document.getElementById('loadExampleBtn'),
    previewImportBtn: document.getElementById('previewImportBtn'),
    batchImportPreview: document.getElementById('batchImportPreview'),
    confirmImportBtn: document.getElementById('confirmImportBtn'),
    // Batch Edit Modal
    batchEditModal: document.getElementById('batchEditModal'),
    closeBatchEditModal: document.getElementById('closeBatchEditModal'),
    batchEditFields: document.getElementById('batchEditFields'),
    batchEditValues: document.getElementById('batchEditValues'),
    confirmBatchEditBtn: document.getElementById('confirmBatchEditBtn'),
    // Batch Inventory Modal
    batchInventoryModal: document.getElementById('batchInventoryModal'),
    closeBatchInventoryModal: document.getElementById('closeBatchInventoryModal'),
    batchInvRadios: document.getElementById('batchInvRadios'),
    batchInvQuantity: document.getElementById('batchInvQuantity'),
    confirmBatchInvBtn: document.getElementById('confirmBatchInvBtn'),
    // Batch Delete Modal
    batchDeleteModal: document.getElementById('batchDeleteModal'),
    closeBatchDeleteModal: document.getElementById('closeBatchDeleteModal'),
    batchDeleteCount: document.getElementById('batchDeleteCount'),
    confirmBatchDeleteBtn: document.getElementById('confirmBatchDeleteBtn')
};

// ==================== Initialization ====================
async function init() {
    await sendHeartbeat(); // Keep Supabase active
    await loadCapsulesData();
    await checkLoginStatus();
    setupEventListeners();
    registerServiceWorker();
    checkInstallPrompt();
    renderInventory();
    renderCapsulesGrid();
    applyLanguage(state.language);
    // Restore admin session
    if (localStorage.getItem('brewlette_admin') === 'true') {
        state.isAdmin = true;
    }
}

// Send heartbeat to keep Supabase active (prevents pause after 7 days inactivity)
async function sendHeartbeat() {
    try {
        if (typeof supabase !== 'undefined') {
            // Lightweight request to keep database active
            await supabase.getCapsuleCount();
            console.log('Heartbeat sent to Supabase');
        }
    } catch (err) {
        console.log('Heartbeat failed:', err);
    }
}

// ==================== Data Loading ====================
async function loadCapsulesData() {
    try {
        // Try to load from Supabase first
        if (typeof supabase !== 'undefined') {
            const capsules = await supabase.getAllCapsules();
            if (capsules && capsules.length > 0) {
                // Transform Supabase data to match app format
                state.capsules = capsules.map(c => ({
                    id: c.id,
                    name: c.name_en || c.name,
                    name_en: c.name_en || c.name,
                    name_zh: c.name_en || c.name,  // Will need translation
                    line: c.line,
                    size_ml: c.size_ml,
                    pod_type: c.pod_type,
                    intensity: c.intensity,
                    tasting_note_en: c.tasting_note_en || c.tasting_note,
                    tasting_note_zh: c.tasting_note_en || c.tasting_note,
                    color: getCapsuleColor(c.line, c.intensity)
                }));
                console.log(`Loaded ${state.capsules.length} capsules from Supabase`);
                state.filteredCapsules = [...state.capsules];
                renderCapsulesGrid();
                return;
            }
        }
    } catch (error) {
        console.log('Using local data:', error.message);
    }

    // Fallback: try to load from local JSON
    try {
        const response = await fetch('./data/capsules.json', { cache: 'no-store' });
        if (response.ok) {
            const data = await response.json();
            state.capsules = data.capsules || [];
        } else {
            state.capsules = getSampleCapsules();
        }
    } catch (error) {
        state.capsules = getSampleCapsules();
    }
    state.filteredCapsules = [...state.capsules];
}

// Helper function to generate capsule color based on line and intensity
function getCapsuleColor(line, intensity) {
    if (line === 'Vertuo') {
        if (intensity >= 9) return '#8B0000';  // Dark red - intense
        if (intensity >= 7) return '#B22222';  // Firebrick
        if (intensity >= 5) return '#CD5C5C'; // Indian red
        return '#F08080';                      // Light coral - mild
    } else {
        // Original Line colors
        if (intensity >= 10) return '#3D2314'; // Very dark brown
        if (intensity >= 8) return '#5C4033';  // Dark brown
        if (intensity >= 6) return '#8B6914';  // Golden brown
        if (intensity >= 4) return '#A89070';   // Light brown
        return '#C4A77D';                       // Tan - mild
    }
}

function getSampleCapsules() {
    return [
        // Original Line - Espresso (40ml)
        { id: 'orig-001', name: 'Ristretto', name_en: 'Ristretto', name_zh: '浓缩瑞斯崔朵', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 10, tasting_note_en: 'Intense and roasted with notes of cereal', tasting_note_zh: '浓郁烘烤，带有谷物香气', color: '#6B3A3A' },
        { id: 'orig-002', name: 'Arpeggio', name_en: 'Arpeggio', name_zh: '琶音', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 9, tasting_note_en: 'Intense and roasted with cocoa notes', tasting_note_zh: '浓郁烘烤，带有可可香气', color: '#4A3728' },
        { id: 'orig-003', name: 'Roma', name_en: 'Roma', name_zh: '罗马', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Balanced and roasted with woody notes', tasting_note_zh: '平衡烘烤，带有木质香气', color: '#5C4033' },
        { id: 'orig-004', name: 'Livanto', name_en: 'Livanto', name_zh: '利凡托', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Round and balanced with caramel notes', tasting_note_zh: '圆润平衡，带有焦糖香气', color: '#8B6914' },
        { id: 'orig-005', name: 'Capriccio', name_en: 'Capriccio', name_zh: '卡普里丘', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Rich and full-bodied with earthy notes', tasting_note_zh: '浓郁醇厚，带有泥土香气', color: '#6B5344' },
        { id: 'orig-006', name: 'Voluto', name_en: 'Voluto', name_zh: '瓦鲁托', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 4, tasting_note_en: 'Light and fruity with floral notes', tasting_note_zh: '清新果香，带有花香', color: '#9B7B5B' },
        { id: 'orig-007', name: 'Kazaar', name_en: 'Kazaar', name_zh: '卡扎尔', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 12, tasting_note_en: 'Exceptionally intense with spicy notes', tasting_note_zh: '极致浓郁，带有辛辣香气', color: '#3D2314' },
        { id: 'orig-008', name: 'Cosi', name_en: 'Cosi', name_zh: '科西', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 4, tasting_note_en: 'Light and mild with cereal notes', tasting_note_zh: '清淡温和，带有谷物香气', color: '#A89070' },
        { id: 'orig-009', name: 'Nicaragua', name_en: 'Nicaragua', name_zh: '尼加拉瓜', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Fruity with citrus notes', tasting_note_zh: '果香，带有柑橘香气', color: '#8B7355' },
        { id: 'orig-010', name: 'India', name_en: 'India', name_zh: '印度', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 11, tasting_note_en: 'Intense and spicy with earthy notes', tasting_note_zh: '浓郁辛辣，带有泥土香气', color: '#5C4033' },
        { id: 'orig-011', name: 'Indonesia', name_en: 'Indonesia', name_zh: '印度尼西亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Rich and earthy with herbal notes', tasting_note_zh: '浓郁泥土，带有草本香气', color: '#6B5344' },
        { id: 'orig-012', name: 'Ethiopia', name_en: 'Ethiopia', name_zh: '埃塞俄比亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 4, tasting_note_en: 'Floral and fruity with citrus', tasting_note_zh: '花香果香，带有柑橘', color: '#9B8B6B' },
        { id: 'orig-013', name: 'Colombia', name_en: 'Colombia', name_zh: '哥伦比亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Balanced with caramel and nuts', tasting_note_zh: '平衡，带有焦糖和坚果', color: '#7A6B5A' },
        { id: 'orig-014', name: 'Brazil', name_en: 'Brazil', name_zh: '巴西', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Smooth with chocolate notes', tasting_note_zh: '顺滑，带有巧克力香气', color: '#6B5344' },
        { id: 'orig-015', name: 'Costa Rica', name_en: 'Costa Rica', name_zh: '哥斯达黎加', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Bright and acidic with honey notes', tasting_note_zh: '明亮酸甜，带有蜂蜜香气', color: '#8B7B5B' },
        { id: 'orig-016', name: 'Guatemala', name_en: 'Guatemala', name_zh: '危地马拉', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 7, tasting_note_en: 'Complex with cocoa and spice', tasting_note_zh: '复杂，带有可可和香料', color: '#5C4A3A' },
        { id: 'orig-017', name: 'Kenya', name_en: 'Kenya', name_zh: '肯尼亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Fruity with berry notes', tasting_note_zh: '果香，带有浆果香气', color: '#7A6A5A' },
        { id: 'orig-018', name: 'Tanzania', name_en: 'Tanzania', name_zh: '坦桑尼亚', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Bright with floral and citrus', tasting_note_zh: '明亮，带有花香和柑橘', color: '#8B7B6B' },
        { id: 'orig-019', name: 'Venezia', name_en: 'Venezia', name_zh: '威尼斯', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 7, tasting_note_en: 'Rich and creamy with cocoa', tasting_note_zh: '浓郁奶油，带有可可', color: '#5C4033' },
        { id: 'orig-020', name: 'Firenze', name_en: 'Firenze', name_zh: '佛罗伦萨', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Intense and bold with roasted notes', tasting_note_zh: '浓郁大胆，带有烘烤香气', color: '#4A3525' },
        { id: 'orig-021', name: 'Milano', name_en: 'Milano', name_zh: '米兰', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Balanced with caramel sweetness', tasting_note_zh: '平衡，带有焦糖甜味', color: '#7A6B5A' },
        { id: 'orig-022', name: 'Napoli', name_en: 'Napoli', name_zh: '那不勒斯', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 10, tasting_note_en: 'Intense and bold', tasting_note_zh: '浓郁大胆', color: '#4A3020' },
        { id: 'orig-023', name: 'Palermo', name_en: 'Palermo', name_zh: '巴勒莫', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 11, tasting_note_en: 'Very intense and smoky', tasting_note_zh: '极浓烟熏', color: '#3D2314' },
        { id: 'orig-024', name: 'Roma Decaffeinato', name_en: 'Roma Decaffeinato', name_zh: '罗马低因', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Balanced and roasted without caffeine', tasting_note_zh: '平衡烘烤，无咖啡因', color: '#6B5A4A' },
        { id: 'orig-025', name: 'Arpeggio Decaffeinato', name_en: 'Arpeggio Decaffeinato', name_zh: '琶音低因', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 9, tasting_note_en: 'Intense and roasted without caffeine', tasting_note_zh: '浓郁烘烤，无咖啡因', color: '#5C4A3A' },
        { id: 'orig-026', name: 'Voluto Decaffeinato', name_en: 'Voluto Decaffeinato', name_zh: '瓦鲁托低因', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 4, tasting_note_en: 'Light and fruity without caffeine', tasting_note_zh: '清新果香，无咖啡因', color: '#9B8B7B' },
        { id: 'orig-027', name: 'Livanto Decaffeinato', name_en: 'Livanto Decaffeinato', name_zh: '利凡托低因', line: 'Original', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Round and balanced without caffeine', tasting_note_zh: '圆润平衡，无咖啡因', color: '#8B7B6B' },
        // Original Line - Lungo (80ml)
        { id: 'orig-028', name: 'Volluto', name_en: 'Volluto', name_zh: '沃鲁托', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 4, tasting_note_en: 'Light and sweet with biscuit', tasting_note_zh: '清淡甜蜜，带有饼干', color: '#9B8B7B' },
        { id: 'orig-029', name: 'Volluto Decaffeinato', name_en: 'Volluto Decaffeinato', name_zh: '沃鲁托低因', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 4, tasting_note_en: 'Light and sweet without caffeine', tasting_note_zh: '清淡甜蜜，无咖啡因', color: '#9B8B7B' },
        { id: 'orig-030', name: 'Café', name_en: 'Café', name_zh: '咖啡', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Rich and balanced with roasted notes', tasting_note_zh: '浓郁平衡，带有烘烤', color: '#6B5344' },
        { id: 'orig-031', name: 'Café Decaffeinato', name_en: 'Café Decaffeinato', name_zh: '咖啡低因', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Rich and balanced without caffeine', tasting_note_zh: '浓郁平衡，无咖啡因', color: '#6B5344' },
        { id: 'orig-032', name: 'Linizio Lungo', name_en: 'Linizio Lungo', name_zh: '利尼齐奥朗戈', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 5, tasting_note_en: 'Mild and balanced with cereal', tasting_note_zh: '温和平衡，带有谷物', color: '#8B7B6B' },
        { id: 'orig-033', name: 'Bukeela ka Ethiopia', name_en: 'Bukeela ka Ethiopia', name_zh: '埃塞俄比亚布基拉', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 3, tasting_note_en: 'Very light with floral notes', tasting_note_zh: '非常清淡，带有花香', color: '#A89888' },
        { id: 'orig-034', name: 'Rosabaya de Colombia', name_en: 'Rosabaya de Colombia', name_zh: '哥伦比亚玫瑰山', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 5, tasting_note_en: 'Fruity and sweet with raspberry', tasting_note_zh: '果香甜蜜，带有覆盆子', color: '#8B6B5B' },
        { id: 'orig-035', name: 'Dulsato de Peru', name_en: 'Dulsato de Peru', name_zh: '秘鲁杜尔萨托', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 5, tasting_note_en: 'Sweet with caramel and nuts', tasting_note_zh: '甜蜜，带有焦糖和坚果', color: '#7A6A5A' },
        { id: 'orig-036', name: 'Intenso', name_en: 'Intenso', name_zh: '浓咖', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 9, tasting_note_en: 'Dark and intense with roasted notes', tasting_note_zh: '深色浓郁，带有烘烤', color: '#4A3020' },
        { id: 'orig-037', name: 'Decaf Intenso', name_en: 'Decaf Intenso', name_zh: '低因浓咖', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 9, tasting_note_en: 'Dark and intense without caffeine', tasting_note_zh: '深色浓郁，无咖啡因', color: '#4A3020' },
        { id: 'orig-038', name: 'Fortissio Lungo', name_en: 'Fortissio Lungo', name_zh: '强劲朗戈', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 8, tasting_note_en: 'Intense and full-bodied', tasting_note_zh: '浓郁醇厚', color: '#5C4033' },
        { id: 'orig-039', name: 'Envivo Lungo', name_en: 'Envivo Lungo', name_zh: '活力朗戈', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 9, tasting_note_en: 'Intense with caramel and roasted', tasting_note_zh: '浓郁，带有焦糖和烘烤', color: '#4A3525' },
        { id: 'orig-040', name: 'Odacio', name_en: 'Odacio', name_zh: '奥达西奥', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 7, tasting_note_en: 'Rich with fruity notes', tasting_note_zh: '浓郁，带有果香', color: '#6B5A4A' },
        { id: 'orig-041', name: 'Sarawak', name_en: 'Sarawak', name_zh: '沙捞越', line: 'Original', size_ml: 80, pod_type: 'lungo', intensity: 8, tasting_note_en: 'Full-bodied with earthy notes', tasting_note_zh: '醇厚，带有泥土', color: '#5C4A3A' },
        // Vertuo Line - Espresso (40ml)
        { id: 'vert-001', name: 'Diavoletto', name_en: 'Diavoletto', name_zh: '小恶魔', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Rich and intense with cocoa', tasting_note_zh: '浓郁，带有可可', color: '#5C3020' },
        { id: 'vert-002', name: 'D Palermo', name_en: 'D Palermo', name_zh: 'D巴勒莫', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 11, tasting_note_en: 'Very dark and smoky', tasting_note_zh: '极深色烟熏', color: '#2D1B0F' },
        { id: 'vert-003', name: 'D Caramel', name_en: 'D Caramel', name_zh: 'D焦糖', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Sweet caramel with vanilla', tasting_note_zh: '甜蜜焦糖，带有香草', color: '#8B6914' },
        { id: 'vert-004', name: 'D Cocoa', name_en: 'D Cocoa', name_zh: 'D可可', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 7, tasting_note_en: 'Rich cocoa with chocolate', tasting_note_zh: '浓郁可可，带有巧克力', color: '#4A3020' },
        { id: 'vert-005', name: 'D Espresso', name_en: 'D Espresso', name_zh: 'D浓缩', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 9, tasting_note_en: 'Classic espresso with caramel', tasting_note_zh: '经典浓缩，带有焦糖', color: '#5C4033' },
        { id: 'vert-006', name: 'D Intenso', name_en: 'D Intenso', name_zh: 'D浓郁', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 10, tasting_note_en: 'Very intense and bold', tasting_note_zh: '极浓大胆', color: '#3D2314' },
        { id: 'vert-007', name: 'D Leggero', name_en: 'D Leggero', name_zh: 'D清淡', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 3, tasting_note_en: 'Light and mild', tasting_note_zh: '清淡温和', color: '#9B8B7B' },
        { id: 'vert-008', name: 'D Decaf', name_en: 'D Decaf', name_zh: 'D低因', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Smooth without caffeine', tasting_note_zh: '顺滑无咖啡因', color: '#7A6B5A' },
        { id: 'vert-009', name: 'Awlack', name_en: 'Awlack', name_zh: '阿瓦拉克', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 10, tasting_note_en: 'Very intense with bitter cocoa', tasting_note_zh: '极浓，带有苦可可', color: '#3D2314' },
        { id: 'vert-010', name: 'Bukeela', name_en: 'Bukeela', name_zh: '布基拉', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Delicate with floral notes', tasting_note_zh: '精致，带有花香', color: '#8B7B6B' },
        { id: 'vert-011', name: 'Dharkan', name_en: 'Dharkan', name_zh: '德卡恩', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 11, tasting_note_en: 'Dark and complex with cocoa', tasting_note_zh: '深色复杂，带有可可', color: '#2D1B0F' },
        { id: 'vert-012', name: 'Nicaragua', name_en: 'Nicaragua', name_zh: '尼加拉瓜', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 5, tasting_note_en: 'Fruity with citrus notes', tasting_note_zh: '果香，带有柑橘', color: '#8B7355' },
        { id: 'vert-013', name: 'Hawaii Kona', name_en: 'Hawaii Kona', name_zh: '夏威夷科纳', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 6, tasting_note_en: 'Smooth with nutty notes', tasting_note_zh: '顺滑，带有坚果', color: '#7A6A5A' },
        { id: 'vert-014', name: 'Caffè Florian', name_en: 'Caffè Florian', name_zh: '弗洛里安咖啡', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 9, tasting_note_en: 'Intense with chocolate', tasting_note_zh: '浓郁，带有巧克力', color: '#5C4033' },
        { id: 'vert-015', name: 'Genova Livorno', name_en: 'Genova Livorno', name_zh: '热那亚里窝那', line: 'Vertuo', size_ml: 40, pod_type: 'espresso', intensity: 8, tasting_note_en: 'Rich and balanced', tasting_note_zh: '浓郁平衡', color: '#5C4A3A' },
        // Vertuo Line - Double (80ml)
        { id: 'vert-016', name: 'Double Espresso Chiaro', name_en: 'Double Espresso Chiaro', name_zh: '双份浓缩浅色', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 6, tasting_note_en: 'Light and balanced', tasting_note_zh: '清淡平衡', color: '#8B7B6B' },
        { id: 'vert-017', name: 'Double Espresso Scuro', name_en: 'Double Espresso Scuro', name_zh: '双份浓缩深色', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 9, tasting_note_en: 'Dark and intense', tasting_note_zh: '深色浓郁', color: '#4A3020' },
        { id: 'vert-018', name: 'Stormio', name_en: 'Stormio', name_zh: '风暴', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 8, tasting_note_en: 'Rich and full-bodied with roasted notes', tasting_note_zh: '浓郁醇厚，带有烘烤', color: '#5C4033' },
        { id: 'vert-019', name: 'Oscuro', name_en: 'Oscuro', name_zh: '深暗', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 10, tasting_note_en: 'Very dark and intense', tasting_note_zh: '极深浓郁', color: '#3D2314' },
        { id: 'vert-020', name: 'Grosso', name_en: 'Grosso', name_zh: '格罗索', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 7, tasting_note_en: 'Smooth with caramel', tasting_note_zh: '顺滑，带有焦糖', color: '#6B5A4A' },
        { id: 'vert-021', name: 'Kazaar', name_en: 'Kazaar', name_zh: '卡扎尔', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 12, tasting_note_en: 'Exceptionally intense with spicy notes', tasting_note_zh: '极致浓郁，带有辛辣', color: '#2D1B0F' },
        { id: 'vert-022', name: 'Cafecito', name_en: 'Cafecito', name_zh: '咖啡西托', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 8, tasting_note_en: 'Rich with dark chocolate', tasting_note_zh: '浓郁，带有黑巧克力', color: '#5C4033' },
        { id: 'vert-023', name: 'Espresso Roast', name_en: 'Espresso Roast', name_zh: '浓缩烘焙', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 8, tasting_note_en: 'Classic espresso roast', tasting_note_zh: '经典浓缩烘焙', color: '#5C4033' },
        { id: 'vert-024', name: 'Master Origin Indonesia', name_en: 'Master Origin Indonesia', name_zh: '大师系列印度尼西亚', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 8, tasting_note_en: 'Full-bodied with earthy notes', tasting_note_zh: '醇厚，带有泥土', color: '#5C4A3A' },
        { id: 'vert-025', name: 'Master Origin Ethiopia', name_en: 'Master Origin Ethiopia', name_zh: '大师系列埃塞俄比亚', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 5, tasting_note_en: 'Fruity with floral notes', tasting_note_zh: '果香，带有花香', color: '#8B7B6B' },
        { id: 'vert-026', name: 'Master Origin Colombia', name_en: 'Master Origin Colombia', name_zh: '大师系列哥伦比亚', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 6, tasting_note_en: 'Balanced with caramel', tasting_note_zh: '平衡，带有焦糖', color: '#7A6B5A' },
        { id: 'vert-027', name: 'Master Origin India', name_en: 'Master Origin India', name_zh: '大师系列印度', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 10, tasting_note_en: 'Intense with spicy notes', tasting_note_zh: '浓郁，带有辛辣', color: '#4A3020' },
        { id: 'vert-028', name: 'Freddo Intenso', name_en: 'Freddo Intenso', name_zh: '冷萃浓郁', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 9, tasting_note_en: 'Cold brew style intense', tasting_note_zh: '冷萃风格浓郁', color: '#4A3020' },
        { id: 'vert-029', name: 'Freddo', name_en: 'Freddo', name_zh: '冷萃', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 5, tasting_note_en: 'Cold brew style light', tasting_note_zh: '冷萃风格清淡', color: '#8B7B6B' },
        { id: 'vert-030', name: 'Firenze', name_en: 'Firenze', name_zh: '佛罗伦萨', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 9, tasting_note_en: 'Intense with cocoa', tasting_note_zh: '浓郁，带有可可', color: '#4A3525' },
        { id: 'vert-031', name: 'Napoli', name_en: 'Napoli', name_zh: '那不勒斯', line: 'Vertuo', size_ml: 80, pod_type: 'double', intensity: 11, tasting_note_en: 'Very intense with bitter notes', tasting_note_zh: '极浓，带有苦味', color: '#3D2314' },
        // Vertuo Line - Lungo (150ml)
        { id: 'vert-032', name: 'Melozio', name_en: 'Melozio', name_zh: '旋律', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Smooth and sweet with cereal', tasting_note_zh: '顺滑甜蜜，带有谷物', color: '#8B7B6B' },
        { id: 'vert-033', name: 'Solelio', name_en: 'Solelio', name_zh: '阳光', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 4, tasting_note_en: 'Light and fruity', tasting_note_zh: '清淡果香', color: '#9B8B7B' },
        { id: 'vert-034', name: 'Fortado', name_en: 'Fortado', name_zh: '强劲', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 8, tasting_note_en: 'Rich and full-bodied', tasting_note_zh: '浓郁醇厚', color: '#5C4033' },
        { id: 'vert-035', name: 'Intenso', name_en: 'Intenso', name_zh: '浓咖', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 9, tasting_note_en: 'Dark and intense with cocoa', tasting_note_zh: '深色浓郁，带有可可', color: '#4A3020' },
        { id: 'vert-036', name: 'Decaf', name_en: 'Decaf', name_zh: '低因', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Smooth without caffeine', tasting_note_zh: '顺滑无咖啡因', color: '#7A6B5A' },
        { id: 'vert-037', name: 'Vanilio', name_en: 'Vanilio', name_zh: '香草', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Sweet vanilla with creamy', tasting_note_zh: '甜蜜香草，奶油', color: '#9B8B6B' },
        { id: 'vert-038', name: 'Caramizio', name_en: 'Caramizio', name_zh: '焦糖', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Rich caramel with sweet', tasting_note_zh: '浓郁焦糖，甜蜜', color: '#8B6914' },
        { id: 'vert-039', name: 'Chiaro', name_en: 'Chiaro', name_zh: '浅色', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 4, tasting_note_en: 'Light and mild', tasting_note_zh: '清淡温和', color: '#9B8B7B' },
        { id: 'vert-040', name: 'Scuro', name_en: 'Scuro', name_zh: '深色', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 9, tasting_note_en: 'Dark and roasted', tasting_note_zh: '深色烘烤', color: '#3D2314' },
        { id: 'vert-041', name: 'Voltesso', name_en: 'Voltesso', name_zh: '沃尔泰索', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 4, tasting_note_en: 'Light and aromatic', tasting_note_zh: '清淡芳香', color: '#9B8B7B' },
        { id: 'vert-042', name: 'Roma', name_en: 'Roma', name_zh: '罗马', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 7, tasting_note_en: 'Balanced with woody notes', tasting_note_zh: '平衡，带有木质', color: '#6B5A4A' },
        { id: 'vert-043', name: 'Venezia', name_en: 'Venezia', name_zh: '威尼斯', line: 'Vertuo', size_ml: 150, pod_type: 'lungo', intensity: 6, tasting_note_en: 'Smooth with caramel', tasting_note_zh: '顺滑，带有焦糖', color: '#7A6B5A' },
        // Vertuo Line - Coffee (230ml)
        { id: 'vert-044', name: 'Altissimo', name_en: 'Altissimo', name_zh: '至高', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 11, tasting_note_en: 'Exceptionally intense', tasting_note_zh: '极致浓郁', color: '#2D1B0F' },
        { id: 'vert-045', name: 'Lungo', name_en: 'Lungo', name_zh: '大杯', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 5, tasting_note_en: 'Smooth with balanced flavor', tasting_note_zh: '顺滑，平衡风味', color: '#7A6B5A' },
        { id: 'vert-046', name: 'Lungo Decaf', name_en: 'Lungo Decaf', name_zh: '大杯低因', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 5, tasting_note_en: 'Smooth without caffeine', tasting_note_zh: '顺滑无咖啡因', color: '#7A6B5A' },
        { id: 'vert-047', name: 'Coffee', name_en: 'Coffee', name_zh: '咖啡', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 6, tasting_note_en: 'Rich and balanced', tasting_note_zh: '浓郁平衡', color: '#6B5A4A' },
        { id: 'vert-048', name: 'Mug', name_en: 'Mug', name_zh: '马克杯', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 7, tasting_note_en: 'Full-bodied with roasted', tasting_note_zh: '醇厚烘烤', color: '#5C4A3A' },
        { id: 'vert-049', name: 'Palermo', name_en: 'Palermo', name_zh: '巴勒莫', line: 'Vertuo', size_ml: 230, pod_type: 'coffee', intensity: 13, tasting_note_en: 'Exceptionally dark and smoky', tasting_note_zh: '极深色烟熏', color: '#1D0B00' }
    ];
}

// ==================== User Authentication ====================
function getUsers() {
    const users = localStorage.getItem('nespresso_users');
    return users ? JSON.parse(users) : {};
}

function saveUsers(users) {
    localStorage.setItem('nespresso_users', JSON.stringify(users));
}

function getCurrentUser() {
    const userId = localStorage.getItem('nespresso_current_user');
    if (!userId) return null;
    const users = getUsers();
    return users[userId] || null;
}

async function checkLoginStatus() {
    const user = getCurrentUser();
    if (user) {
        // Try to get user with ID from Supabase
        try {
            if (typeof supabase !== 'undefined') {
                const supabaseUser = await supabase.getUserByUsername(user.username);
                if (supabaseUser) {
                    state.user = supabaseUser;
                } else {
                    state.user = user;
                }
            } else {
                state.user = user;
            }
        } catch (e) {
            state.user = user;
        }
        state.isLoggedIn = true;
        await loadInventory();
        elements.loginModal.classList.add('hidden');
    } else {
        elements.loginModal.classList.remove('hidden');
    }
}

async function login() {
    const username = elements.loginUsername.value.trim();
    const password = elements.loginPassword.value.trim();
    const lang = state.language;

    if (!username || !password) {
        showToast(lang === 'en' ? 'Please enter username and password' : '请输入用户名和密码', 'error');
        return;
    }

    // First check localStorage (password is stored locally)
    const users = getUsers();
    if (users[username]) {
        // User exists in localStorage, check password
        if (users[username].password !== simpleHash(password)) {
            showToast(lang === 'en' ? 'Wrong password' : '密码错误', 'error');
            return;
        }

        // Login successful with localStorage
        state.user = { username: username };
        state.isLoggedIn = true;
        localStorage.setItem('nespresso_current_user', username);
        elements.loginModal.classList.add('hidden');

        // Try to sync with Supabase in background
        if (typeof supabase !== 'undefined') {
            try {
                const supabaseUser = await supabase.getUserByUsername(username);
                if (supabaseUser) {
                    state.user = supabaseUser;
                } else {
                    // Create user in Supabase if not exists
                    await supabase.createUser(username);
                }
            } catch (e) {
                console.log('Supabase sync skipped');
            }
        }

        await loadInventory();
        renderInventory();
        showToast(lang === 'en' ? `Welcome, ${username}!` : `欢迎，${username}！`, 'success');
        elements.loginPassword.value = '';
        return;
    }

    // User not in localStorage, try Supabase
    try {
        if (typeof supabase !== 'undefined') {
            const user = await supabase.getUserByUsername(username);
            if (user) {
                // User exists in Supabase, save to localStorage and login
                users[username] = {
                    username: username,
                    password: simpleHash(password)
                };
                saveUsers(users);

                state.user = user;
                state.isLoggedIn = true;
                localStorage.setItem('nespresso_current_user', username);
                elements.loginModal.classList.add('hidden');
                await loadInventory();
                renderInventory();
                showToast(lang === 'en' ? `Welcome, ${username}!` : `欢迎，${username}！`, 'success');
                elements.loginPassword.value = '';
                return;
            }
        }
    } catch (error) {
        console.log('Supabase login failed, trying localStorage');
    }

    // No user found anywhere
    showToast(lang === 'en' ? 'User not found. Register first.' : '用户不存在，请先注册', 'error');
}

async function register() {
    const username = elements.loginUsername.value.trim();
    const password = elements.loginPassword.value.trim();
    const lang = state.language;

    if (!username || !password) {
        showToast(lang === 'en' ? 'Please enter username and password' : '请输入用户名和密码', 'error');
        return;
    }

    if (username.length < 3) {
        showToast(lang === 'en' ? 'Username must be at least 3 characters' : '用户名至少3个字符', 'error');
        return;
    }

    if (password.length < 4) {
        showToast(lang === 'en' ? 'Password must be at least 4 characters' : '密码至少4个字符', 'error');
        return;
    }

    // Save to localStorage (needed for password verification)
    const users = getUsers();
    if (users[username]) {
        showToast(lang === 'en' ? 'Username already exists' : '用户名已存在', 'error');
        return;
    }

    // Check Supabase for existing user (only if localStorage doesn't have it)
    let supabaseUser = null;
    try {
        if (typeof supabase !== 'undefined') {
            supabaseUser = await supabase.getUserByUsername(username);
            if (supabaseUser) {
                // User exists in Supabase, save to localStorage and login
                users[username] = {
                    username: username,
                    password: simpleHash(password)
                };
                saveUsers(users);

                // Auto login
                state.user = supabaseUser;
                state.isLoggedIn = true;
                localStorage.setItem('nespresso_current_user', username);
                elements.loginModal.classList.add('hidden');
                await loadInventory();
                renderInventory();
                showToast(lang === 'en' ? `Welcome back, ${username}!` : `欢迎回来，${username}！`, 'success');
                elements.loginPassword.value = '';
                return;
            }
            // Create user in Supabase
            await supabase.createUser(username);
        }
    } catch (error) {
        console.log('Supabase check skipped');
    }

    // Create new user in localStorage
    users[username] = {
        username: username,
        password: simpleHash(password)
    };
    saveUsers(users);

    // Auto login
    state.user = { username: username };
    state.isLoggedIn = true;
    localStorage.setItem('nespresso_current_user', username);
    elements.loginModal.classList.add('hidden');
    await loadInventory();
    renderInventory();
    showToast(lang === 'en' ? `Account created! Welcome, ${username}!` : `账号已创建！欢迎，${username}！`, 'success');
    elements.loginPassword.value = '';
}

function logout() {
    state.user = null;
    state.isLoggedIn = false;
    state.inventory = {};
    localStorage.removeItem('nespresso_current_user');
    elements.loginModal.classList.remove('hidden');
    elements.userModal.classList.add('hidden');
    renderInventory();
    showToast(state.language === 'en' ? 'Logged out' : '已退出登录', 'success');
}

function skipLogin() {
    // Continue as guest (no login required)
    state.user = null;
    state.isLoggedIn = false;
    state.inventory = {};
    elements.loginModal.classList.add('hidden');
    renderInventory();
    renderCapsulesGrid();
}

// Simple hash function for demo (not secure for production)
function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash.toString(16);
}

// ==================== Inventory ====================
async function loadInventory() {
    const username = state.user?.username;
    if (!username) {
        state.inventory = {};
        return;
    }

    // Try to load from Supabase first
    try {
        if (typeof supabase !== 'undefined' && state.user?.id) {
            const supabaseInventory = await supabase.getUserInventory(state.user.id);
            if (supabaseInventory && supabaseInventory.length > 0) {
                const inv = {};
                supabaseInventory.forEach(item => {
                    if (item.capsules) {
                        inv[item.capsules.id] = {
                            ...item.capsules,
                            quantity: item.quantity,
                            inventoryId: item.id
                        };
                    }
                });
                state.inventory = inv;
                // Also save to localStorage as backup
                localStorage.setItem(`nespresso_inv_${username}`, JSON.stringify(state.inventory));
                return;
            }
        }
    } catch (error) {
        console.log('Loading from Supabase failed, using localStorage');
    }

    // Fallback to localStorage
    const savedInventory = localStorage.getItem(`nespresso_inv_${username}`);
    state.inventory = savedInventory ? JSON.parse(savedInventory) : {};
}

async function saveInventory() {
    const username = state.user?.username;
    if (!username) return;

    // Always save to localStorage as backup
    localStorage.setItem(`nespresso_inv_${username}`, JSON.stringify(state.inventory));

    // Try to save to Supabase
    try {
        if (typeof supabase !== 'undefined' && state.user?.id) {
            // Save each inventory item to Supabase
            for (const [capsuleId, item] of Object.entries(state.inventory)) {
                if (item.quantity > 0) {
                    await supabase.addToInventory(state.user.id, capsuleId, item.quantity);
                }
            }
        }
    } catch (error) {
        console.log('Saving to Supabase failed');
    }
}

function setInventoryQuantity(capsuleId, quantity) {
    const capsule = state.capsules.find(c => c.id === capsuleId);
    if (!capsule) return;

    if (quantity <= 0) {
        delete state.inventory[capsuleId];
    } else {
        state.inventory[capsuleId] = {
            ...capsule,
            quantity: quantity
        };
    }
    saveInventory();
    renderInventory();
    renderCapsulesGrid();
}

function getTotalCapsules() {
    return Object.values(state.inventory).reduce((sum, item) => sum + item.quantity, 0);
}

function getInventoryCapsules() {
    return Object.values(state.inventory).filter(item => item.quantity > 0);
}

// ==================== Admin Authentication ====================
function checkAdminAccess() {
    if (state.isAdmin) {
        switchTab('admin');
    } else {
        elements.adminPasswordModal.classList.remove('hidden');
        elements.adminPasswordInput.focus();
    }
}

async function verifyAdminPassword() {
    const password = elements.adminPasswordInput.value.trim();
    if (!password) {
        showToast(state.language === 'en' ? 'Please enter password' : '请输入密码', 'error');
        return;
    }

    try {
        const isValid = await supabase.verifyAdminPassword(password);
        if (isValid) {
            state.isAdmin = true;
            localStorage.setItem('brewlette_admin', 'true');
            elements.adminPasswordModal.classList.add('hidden');
            elements.adminPasswordInput.value = '';
            switchTab('admin');
            await loadAdminData();
            showToast(state.language === 'en' ? 'Admin access granted' : '已获得管理员权限', 'success');
        } else {
            showToast(state.language === 'en' ? 'Wrong password' : '密码错误', 'error');
        }
    } catch (error) {
        showToast(state.language === 'en' ? 'Verification failed' : '验证失败', 'error');
    }
}

function closeAdminPasswordModal() {
    elements.adminPasswordModal.classList.add('hidden');
    elements.adminPasswordInput.value = '';
}

// ==================== Admin Data Loading ====================
async function loadAdminData() {
    await loadAdminBrands();
    await loadAdminCapsules();
}

async function loadAdminBrands() {
    try {
        state.adminBrands = await supabase.getAllBrands();
        renderAdminBrands();
        populateBrandDropdowns();
    } catch (error) {
        console.error('Failed to load brands:', error);
    }
}

async function loadAdminCapsules() {
    try {
        state.adminCapsules = await supabase.getCapsulesWithBrands();
        renderAdminCapsules();
    } catch (error) {
        console.error('Failed to load capsules:', error);
    }
}

// ==================== Brand Management ====================
async function addBrand() {
    const name = elements.newBrandName.value.trim();
    if (!name) {
        showToast(state.language === 'en' ? 'Please enter brand name' : '请输入品牌名称', 'error');
        return;
    }

    try {
        await supabase.createBrand(name);
        elements.newBrandName.value = '';
        await loadAdminBrands();
        showToast(state.language === 'en' ? 'Brand added' : '品牌已添加', 'success');
    } catch (error) {
        showToast(state.language === 'en' ? 'Failed to add brand' : '添加品牌失败', 'error');
    }
}

async function deleteBrand(id) {
    if (!confirm(state.language === 'en' ? 'Delete this brand?' : '删除此品牌？')) return;

    try {
        await supabase.deleteBrand(id);
        await loadAdminBrands();
        showToast(state.language === 'en' ? 'Brand deleted' : '品牌已删除', 'success');
    } catch (error) {
        showToast(state.language === 'en' ? 'Failed to delete brand' : '删除品牌失败', 'error');
    }
}

function renderAdminBrands() {
    if (state.adminBrands.length === 0) {
        elements.brandsList.innerHTML = '<p class="empty-state" style="padding: 12px; font-size: 0.9rem;">No brands yet</p>';
        return;
    }

    elements.brandsList.innerHTML = state.adminBrands.map(brand => {
        let brandName = '-';
        let brandId = null;

        if (typeof brand === 'object' && brand !== null) {
            brandName = brand.name || '-';
            brandId = brand.id;
        } else if (typeof brand === 'string') {
            try {
                const parsed = JSON.parse(brand);
                brandName = parsed.name || '-';
                brandId = parsed.id;
            } catch {
                brandName = brand; // Use as-is if not valid JSON
            }
        }

        return `
            <div class="brand-item">
                <span>${brandName}</span>
                <button class="danger-btn small" onclick="deleteBrand(${brandId})">Delete</button>
            </div>
        `;
    }).join('');
}

// Helper to parse brands from capsules response
function getBrandName(brandsData) {
    if (!brandsData) return '-';

    // If it's already an object with name property, return it directly
    if (typeof brandsData === 'object' && brandsData.name) {
        return brandsData.name;
    }

    // If it's a string, try to parse it
    if (typeof brandsData === 'string') {
        try {
            const parsed = JSON.parse(brandsData);
            // Handle array format like [{"name":"Nespresso"}]
            if (Array.isArray(parsed) && parsed.length > 0) {
                return parsed[0].name || '-';
            }
            // Handle object format like {"name":"Nespresso"}
            if (parsed.name) {
                return parsed.name;
            }
        } catch {
            // If it's not valid JSON, maybe it's just a plain string name
            if (brandsData.trim()) {
                return brandsData;
            }
        }
    }

    return '-';
}

function populateBrandDropdowns() {
    const lang = state.language;
    const allOption = `<option value="all">${lang === 'en' ? 'All Brands' : '所有品牌'}</option>`;
    const selectOption = `<option value="">${lang === 'en' ? 'Select brand...' : '选择品牌...'}</option>`;

    const brandOptions = state.adminBrands.map(b => {
        let brandId = null;
        let brandName = '-';

        if (typeof b === 'object' && b !== null) {
            brandId = b.id;
            brandName = b.name || '-';
        } else if (typeof b === 'string') {
            try {
                const parsed = JSON.parse(b);
                brandId = parsed.id;
                brandName = parsed.name || '-';
            } catch {
                brandId = b;
                brandName = b;
            }
        }

        return `<option value="${brandId}">${brandName}</option>`;
    }).join('');

    elements.adminFilterBrand.innerHTML = allOption + brandOptions;
    elements.capsuleEditBrand.innerHTML = selectOption + brandOptions;
}

// ==================== Capsule Management ====================
function openAddCapsuleModal() {
    state.editingCapsuleId = null;
    elements.capsuleEditTitle.textContent = state.language === 'en' ? 'Add Capsule' : '添加胶囊';
    elements.capsuleEditForm.reset();
    elements.capsuleEditId.value = '';
    // Smart defaults
    elements.capsuleEditLine.value = 'Original';
    elements.capsuleEditSize.value = 40;
    elements.capsuleEditSize2.value = '';
    elements.capsuleEditBestServe.value = getSizeName(40);
    elements.capsuleEditBestServe.dataset.auto = 'true';
    elements.capsuleEditModal.classList.remove('hidden');
}

function copyCapsule(capsule) {
    // Open edit modal but clear the id so it becomes a new capsule
    state.editingCapsuleId = null;
    elements.capsuleEditTitle.textContent = state.language === 'en' ? 'Copy Capsule' : '复制胶囊';
    elements.capsuleEditForm.reset();
    elements.capsuleEditId.value = '';
    elements.capsuleEditBrand.value = capsule.brand_id || '';
    elements.capsuleEditName.value = (capsule.name || '') + ' (copy)';
    elements.capsuleEditLine.value = capsule.line || 'Original';
    elements.capsuleEditBestServe.value = capsule.best_serve || '';
    elements.capsuleEditSize.value = capsule.size_ml || 40;
    elements.capsuleEditSize2.value = capsule.size_ml2 || '';
    elements.capsuleEditIntensity.value = capsule.intensity || '';
    elements.capsuleEditTastingNote.value = capsule.tasting_note || '';
    elements.capsuleEditBestServe.dataset.auto = 'false';
    elements.capsuleEditModal.classList.remove('hidden');
}

function openEditCapsuleModal(capsule) {
    state.editingCapsuleId = capsule.id;
    elements.capsuleEditTitle.textContent = state.language === 'en' ? 'Edit Capsule' : '编辑胶囊';
    elements.capsuleEditId.value = capsule.id;
    elements.capsuleEditBrand.value = capsule.brand_id || '';
    elements.capsuleEditName.value = capsule.name || '';
    elements.capsuleEditLine.value = capsule.line || 'Original';
    elements.capsuleEditBestServe.value = capsule.best_serve || '';
    elements.capsuleEditSize.value = capsule.size_ml || 40;
    elements.capsuleEditSize2.value = capsule.size_ml2 || '';
    elements.capsuleEditIntensity.value = capsule.intensity || '';
    elements.capsuleEditTastingNote.value = capsule.tasting_note || '';
    elements.capsuleEditBestServe.dataset.auto = 'false';
    elements.capsuleEditModal.classList.remove('hidden');
}

function closeCapsuleEditModal() {
    elements.capsuleEditModal.classList.add('hidden');
    state.editingCapsuleId = null;
}

async function saveCapsule(e) {
    e.preventDefault();

    const capsule = {
        brand_id: elements.capsuleEditBrand.value ? parseInt(elements.capsuleEditBrand.value) : null,
        name: elements.capsuleEditName.value.trim(),
        line: elements.capsuleEditLine.value,
        best_serve: elements.capsuleEditBestServe.value.trim(),
        size_ml: parseInt(elements.capsuleEditSize.value),
        size_ml2: elements.capsuleEditSize2.value ? parseInt(elements.capsuleEditSize2.value) : null,
        intensity: elements.capsuleEditIntensity.value ? parseInt(elements.capsuleEditIntensity.value) : null,
        tasting_note: elements.capsuleEditTastingNote.value.trim(),
        last_updated: new Date().toISOString()
    };

    try {
        if (state.editingCapsuleId) {
            await supabase.updateCapsule(state.editingCapsuleId, capsule);
            showToast(state.language === 'en' ? 'Capsule updated' : '胶囊已更新', 'success');
        } else {
            await supabase.createCapsule(capsule);
            showToast(state.language === 'en' ? 'Capsule added' : '胶囊已添加', 'success');
        }
        closeCapsuleEditModal();
        await loadAdminCapsules();
        // Also reload main capsules so Capsules tab shows the new/updated capsule
        await loadCapsulesData();
    } catch (error) {
        showToast(state.language === 'en' ? 'Failed to save capsule' : '保存胶囊失败', 'error');
    }
}

async function deleteCapsule(id) {
    if (!confirm(state.language === 'en' ? 'Delete this capsule?' : '删除此胶囊？')) return;

    try {
        await supabase.deleteCapsule(id);
        // Use string comparison for reliable matching (id might be string or number)
        const targetId = String(id);
        // Remove from admin state
        state.adminCapsules = state.adminCapsules.filter(c => String(c.id) !== targetId);
        renderAdminCapsules();
        // Also remove from main capsules state
        state.capsules = state.capsules.filter(c => String(c.id) !== targetId);
        state.filteredCapsules = state.filteredCapsules.filter(c => String(c.id) !== targetId);
        renderCapsulesGrid();
        showToast(state.language === 'en' ? 'Capsule deleted' : '胶囊已删除', 'success');
    } catch (error) {
        showToast(state.language === 'en' ? 'Failed to delete capsule' : '删除胶囊失败', 'error');
    }
}

async function clearAllCapsules() {
    if (!confirm(state.language === 'en' ? 'Delete ALL capsules? This cannot be undone!' : '删除所有胶囊？此操作无法撤销！')) return;

    try {
        await supabase.deleteAllCapsules();
        state.adminCapsules = [];
        renderAdminCapsules();
        // Also clear main capsules state
        state.capsules = [];
        state.filteredCapsules = [];
        renderCapsulesGrid();
        showToast(state.language === 'en' ? 'All capsules deleted' : '所有胶囊已删除', 'success');
    } catch (error) {
        showToast(state.language === 'en' ? 'Failed to delete capsules' : '删除胶囊失败', 'error');
    }
}

// ==================== Import JSON ====================
function openImportModal() {
    elements.importModal.classList.remove('hidden');
    elements.importJsonText.value = '';
}

function closeImportModal() {
    elements.importModal.classList.add('hidden');
}

async function importCapsulesFromJSON() {
    const jsonText = elements.importJsonText.value.trim();
    if (!jsonText) {
        showToast(state.language === 'en' ? 'Please enter JSON data' : '请输入 JSON 数据', 'error');
        return;
    }

    let capsules;
    try {
        capsules = JSON.parse(jsonText);
    } catch (e) {
        showToast(state.language === 'en' ? 'Invalid JSON format' : 'JSON 格式错误', 'error');
        return;
    }

    if (!Array.isArray(capsules)) {
        showToast(state.language === 'en' ? 'JSON must be an array' : 'JSON 必须是数组', 'error');
        return;
    }

    if (capsules.length === 0) {
        showToast(state.language === 'en' ? 'Array is empty' : '数组为空', 'error');
        return;
    }

    let successCount = 0;
    let errorCount = 0;

    for (const item of capsules) {
        if (!item.name) {
            errorCount++;
            continue;
        }

        const capsule = {
            brand_id: item.brand_id || null,
            name: item.name,
            line: item.line || 'Original',
            best_serve: item.best_serve || item.size_ml ? getSizeName(item.size_ml) : '',
            size_ml: item.size_ml || (item.line === 'Vertuo' ? 80 : 40),
            intensity: item.intensity || null,
            tasting_note: item.tasting_note || '',
            last_updated: new Date().toISOString()
        };

        try {
            await supabase.createCapsule(capsule);
            successCount++;
        } catch (e) {
            errorCount++;
        }
    }

    closeImportModal();
    await loadAdminCapsules();
    await loadCapsulesData();

    if (errorCount === 0) {
        showToast(state.language === 'en' ? `Imported ${successCount} capsules` : `已导入 ${successCount} 个胶囊`, 'success');
    } else {
        showToast(state.language === 'en' ? `Imported ${successCount}, failed ${errorCount}` : `成功 ${successCount}，失败 ${errorCount}`, 'error');
    }
}

function getSizeName(sizeMl) {
    if (sizeMl <= 50) return 'Espresso';
    if (sizeMl <= 100) return 'Double';
    if (sizeMl <= 180) return 'Gran Lungo';
    if (sizeMl <= 250) return 'Coffee';
    if (sizeMl <= 400) return 'Alto';
    return 'Carafe';
}

function mapSizeToCategory(sizeMl) {
    if (sizeMl <= 50) return 'espresso';
    if (sizeMl <= 100) return 'double';
    if (sizeMl <= 180) return 'lungo';
    if (sizeMl <= 250) return 'coffee';
    if (sizeMl <= 400) return 'alto';
    return 'carafe';
}

function getFilteredAdminCapsules() {
    const brandFilter = elements.adminFilterBrand.value;
    const lineFilter = elements.adminFilterLine.value;

    return state.adminCapsules.filter(capsule => {
        if (brandFilter !== 'all' && capsule.brand_id !== parseInt(brandFilter)) return false;
        if (lineFilter !== 'all' && capsule.line !== lineFilter) return false;
        return true;
    });
}

function renderAdminCapsules() {
    const capsules = getFilteredAdminCapsules();

    if (capsules.length === 0) {
        elements.adminCapsulesBody.innerHTML = '';
        elements.emptyAdminCapsules.classList.remove('hidden');
        return;
    }

    elements.emptyAdminCapsules.classList.add('hidden');

    elements.adminCapsulesBody.innerHTML = capsules.map(capsule => `
        <tr class="${state.selectedCapsules.has(capsule.id) ? 'selected-row' : ''}">
            <td class="batch-col">
                <input type="checkbox" class="batch-checkbox"
                    data-id="${capsule.id}"
                    ${state.selectedCapsules.has(capsule.id) ? 'checked' : ''}>
            </td>
            <td>${getBrandName(capsule.brands)}</td>
            <td>${capsule.name || '-'}</td>
            <td>${capsule.line || '-'}</td>
            <td>${capsule.best_serve || '-'}</td>
            <td>${capsule.size_ml ? capsule.size_ml + 'ml' + (capsule.size_ml2 ? '/' + capsule.size_ml2 + 'ml' : '') : '-'}</td>
            <td>${capsule.intensity || '-'}</td>
            <td>${capsule.tasting_note || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="edit-btn" onclick='copyCapsule(${JSON.stringify(capsule).replace(/'/g, "\\'")})'>Copy</button>
                    <button class="edit-btn" onclick='openEditCapsuleModal(${JSON.stringify(capsule).replace(/'/g, "\\'")})'>Edit</button>
                    <button class="danger-btn small" onclick="deleteCapsule(${capsule.id})">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ==================== Batch Operations ====================
function updateBatchActionBar() {
    const count = state.selectedCapsules.size;
    elements.batchSelectedCount.textContent = count;
    if (count > 0) {
        elements.batchActionBar.classList.remove('hidden');
    } else {
        elements.batchActionBar.classList.add('hidden');
    }
}

function toggleCapsuleSelection(id) {
    if (state.selectedCapsules.has(id)) {
        state.selectedCapsules.delete(id);
    } else {
        state.selectedCapsules.add(id);
    }
    updateBatchActionBar();
    // Update checkbox visual state
    const checkbox = document.querySelector(`.batch-checkbox[data-id="${id}"]`);
    if (checkbox) {
        checkbox.checked = state.selectedCapsules.has(id);
    }
    // Update row styling
    const row = checkbox ? checkbox.closest('tr') : null;
    if (row) {
        row.classList.toggle('selected-row', state.selectedCapsules.has(id));
    }
}

function toggleSelectAllCapsules() {
    const capsules = getFilteredAdminCapsules();
    const allSelected = capsules.every(c => state.selectedCapsules.has(c.id));

    if (allSelected) {
        capsules.forEach(c => state.selectedCapsules.delete(c.id));
    } else {
        capsules.forEach(c => state.selectedCapsules.add(c.id));
    }

    document.querySelectorAll('.batch-checkbox').forEach(cb => {
        cb.checked = !allSelected;
    });
    document.querySelectorAll('#adminCapsulesBody tr').forEach(row => {
        row.classList.toggle('selected-row', !allSelected);
    });

    updateBatchActionBar();
}

function clearBatchSelection() {
    state.selectedCapsules.clear();
    document.querySelectorAll('.batch-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('#adminCapsulesBody tr').forEach(row => {
        row.classList.remove('selected-row');
    });
    updateBatchActionBar();
}

function getSelectedCapsuleIds() {
    return Array.from(state.selectedCapsules);
}

// Batch Edit Functions
function openBatchEditModal() {
    if (state.selectedCapsules.size === 0) return;

    // Populate brand dropdown
    const brandSelect = document.getElementById('batchNewBrand');
    brandSelect.innerHTML = '<option value="">Select brand...</option>' +
        state.adminBrands.map(b => `<option value="${b.id}">${b.name}</option>`).join('');

    // Reset checkboxes
    document.querySelectorAll('#batchEditFields .batch-edit-field').forEach(f => {
        f.classList.remove('selected');
        f.querySelector('input').checked = false;
    });
    document.querySelectorAll('#batchEditValues .form-group').forEach(g => {
        g.style.display = 'none';
    });

    elements.batchEditModal.classList.remove('hidden');
}

function closeBatchEditModal() {
    elements.batchEditModal.classList.add('hidden');
}

async function applyBatchEdit() {
    const selectedIds = getSelectedCapsuleIds();
    if (selectedIds.length === 0) return;

    const updates = {};
    let hasUpdates = false;

    if (document.getElementById('batchEditBrand').checked) {
        const val = document.getElementById('batchNewBrand').value;
        if (val) { updates.brand_id = parseInt(val); hasUpdates = true; }
    }
    if (document.getElementById('batchEditLine').checked) {
        updates.line = document.getElementById('batchNewLine').value;
        hasUpdates = true;
    }
    if (document.getElementById('batchEditBestServe').checked) {
        updates.best_serve = document.getElementById('batchNewBestServe').value;
        hasUpdates = true;
    }
    if (document.getElementById('batchEditSize').checked) {
        updates.size_ml = parseInt(document.getElementById('batchNewSize').value);
        hasUpdates = true;
    }
    if (document.getElementById('batchEditIntensity').checked) {
        updates.intensity = parseInt(document.getElementById('batchNewIntensity').value);
        hasUpdates = true;
    }
    if (document.getElementById('batchEditTastingNote').checked) {
        updates.tasting_note = document.getElementById('batchNewTastingNote').value;
        hasUpdates = true;
    }

    if (!hasUpdates) {
        showToast(state.language === 'en' ? 'No fields selected' : '未选择任何字段', 'error');
        return;
    }

    try {
        await supabase.batchUpdateCapsules(selectedIds, updates);
        showToast(state.language === 'en' ? `Updated ${selectedIds.length} capsules` : `已更新 ${selectedIds.length} 个胶囊`, 'success');
        closeBatchEditModal();
        clearBatchSelection();
        await loadAdminData();
    } catch (error) {
        showToast(state.language === 'en' ? 'Update failed' : '更新失败', 'error');
    }
}

// Batch Inventory Functions
function openBatchInventoryModal() {
    if (state.selectedCapsules.size === 0) return;
    elements.batchInvQuantity.value = 1;
    elements.batchInventoryModal.classList.remove('hidden');
}

function closeBatchInventoryModal() {
    elements.batchInventoryModal.classList.add('hidden');
}

async function applyBatchInventory() {
    const selectedIds = getSelectedCapsuleIds();
    if (selectedIds.length === 0) return;

    const action = document.querySelector('input[name="batchInvAction"]:checked').value;
    const quantity = parseInt(elements.batchInvQuantity.value) || 1;

    if (!state.user) {
        showToast(state.language === 'en' ? 'Please login first' : '请先登录', 'error');
        return;
    }

    const updates = selectedIds.map(pod_id => ({ pod_id, action, quantity }));

    try {
        await supabase.batchUpdateInventory(state.user.id, updates);
        showToast(state.language === 'en' ? `Updated inventory for ${selectedIds.length} capsules` : `已更新 ${selectedIds.length} 个胶囊的库存`, 'success');
        closeBatchInventoryModal();
        clearBatchSelection();
        await loadInventory();
    } catch (error) {
        showToast(state.language === 'en' ? 'Inventory update failed' : '库存更新失败', 'error');
    }
}

// Batch Delete Functions
function openBatchDeleteModal() {
    if (state.selectedCapsules.size === 0) return;
    elements.batchDeleteCount.textContent = state.selectedCapsules.size;
    elements.batchDeleteModal.classList.remove('hidden');
}

function closeBatchDeleteModal() {
    elements.batchDeleteModal.classList.add('hidden');
}

async function applyBatchDelete() {
    const selectedIds = getSelectedCapsuleIds();
    if (selectedIds.length === 0) return;

    try {
        await supabase.batchDeleteCapsules(selectedIds);
        showToast(state.language === 'en' ? `Deleted ${selectedIds.length} capsules` : `已删除 ${selectedIds.length} 个胶囊`, 'success');
        closeBatchDeleteModal();
        clearBatchSelection();
        await loadAdminData();
        await loadCapsulesData();
    } catch (error) {
        showToast(state.language === 'en' ? 'Delete failed' : '删除失败', 'error');
    }
}

// Batch Import Visual Functions
function openBatchImportModal() {
    elements.batchImportRows.innerHTML = '';
    elements.batchImportPreview.classList.add('hidden');
    elements.confirmImportBtn.classList.add('hidden');
    addBatchImportRow();
    elements.batchImportModal.classList.remove('hidden');
}

function closeBatchImportModal() {
    elements.batchImportModal.classList.add('hidden');
}

function addBatchImportRow(data = {}) {
    const row = document.createElement('div');
    row.className = 'batch-import-row';
    row.innerHTML = `
        <input type="text" class="import-name" placeholder="Name *" value="${data.name || ''}" required>
        <select class="import-brand">
            <option value="">Brand...</option>
            ${state.adminBrands.map(b => `<option value="${b.id}" ${data.brand_id == b.id ? 'selected' : ''}>${b.name}</option>`).join('')}
        </select>
        <select class="import-line">
            <option value="Original" ${data.line === 'Original' ? 'selected' : ''}>Original</option>
            <option value="Vertuo" ${data.line === 'Vertuo' ? 'selected' : ''}>Vertuo</option>
        </select>
        <select class="import-size">
            <option value="40" ${data.size_ml == 40 ? 'selected' : ''}>40ml</option>
            <option value="80" ${data.size_ml == 80 ? 'selected' : ''}>80ml</option>
            <option value="150" ${data.size_ml == 150 ? 'selected' : ''}>150ml</option>
            <option value="230" ${data.size_ml == 230 ? 'selected' : ''}>230ml</option>
            <option value="355" ${data.size_ml == 355 ? 'selected' : ''}>355ml</option>
            <option value="535" ${data.size_ml == 535 ? 'selected' : ''}>535ml</option>
        </select>
        <select class="import-size2">
            <option value="">--</option>
            <option value="40" ${data.size_ml2 == 40 ? 'selected' : ''}>40ml</option>
            <option value="80" ${data.size_ml2 == 80 ? 'selected' : ''}>80ml</option>
            <option value="150" ${data.size_ml2 == 150 ? 'selected' : ''}>150ml</option>
            <option value="230" ${data.size_ml2 == 230 ? 'selected' : ''}>230ml</option>
            <option value="355" ${data.size_ml2 == 355 ? 'selected' : ''}>355ml</option>
            <option value="535" ${data.size_ml2 == 535 ? 'selected' : ''}>535ml</option>
        </select>
        <input type="number" class="import-intensity" placeholder="1-13" min="1" max="13" value="${data.intensity || ''}">
        <span class="import-bestserveshow">${data.best_serve || 'Espresso'}</span>
        <input type="text" class="import-note" placeholder="Tasting note" value="${data.tasting_note || ''}">
        <label style="display: flex; align-items: center; justify-content: center;">
            <input type="checkbox" class="import-decaffeinato" ${data.decaffeinato ? 'checked' : ''}>
        </label>
        <button class="delete-row-btn" onclick="this.closest('.batch-import-row').remove()">&times;</button>
    `;
    elements.batchImportRows.appendChild(row);

    // Add event listeners to update Best Serve when size changes
    const sizeSelect = row.querySelector('.import-size');
    const size2Select = row.querySelector('.import-size2');
    const bestServeShow = row.querySelector('.import-bestserveshow');

    function updateBestServe() {
        const sizeMl = parseInt(sizeSelect.value) || 40;
        const sizeMl2 = size2Select.value ? parseInt(size2Select.value) : null;
        bestServeShow.textContent = sizeMl2
            ? (sizeMl2 > sizeMl ? getSizeName(sizeMl2) : getSizeName(sizeMl))
            : getSizeName(sizeMl);
    }

    sizeSelect.addEventListener('change', updateBestServe);
    size2Select.addEventListener('change', updateBestServe);
}

function loadExampleImportData() {
    const examples = [
        { name: 'Ristretto', line: 'Original', size_ml: 40, intensity: 10, tasting_note: 'Intense and bold' },
        { name: 'Livanto', line: 'Original', size_ml: 40, intensity: 6, tasting_note: 'Round and balanced' },
        { name: 'Vanilio', line: 'Original', size_ml: 40, intensity: 6, tasting_note: 'Vanilla and sweetness' }
    ];

    elements.batchImportRows.innerHTML = '';
    examples.forEach(ex => addBatchImportRow(ex));
}

function previewBatchImport() {
    const rows = document.querySelectorAll('#batchImportRows .batch-import-row');
    const capsules = [];

    rows.forEach(row => {
        const name = row.querySelector('.import-name').value.trim();
        if (!name) return;

        const capsule = {
            name: name,
            brand_id: row.querySelector('.import-brand').value ? parseInt(row.querySelector('.import-brand').value) : null,
            line: row.querySelector('.import-line').value,
            size_ml: parseInt(row.querySelector('.import-size').value) || 40,
            intensity: row.querySelector('.import-intensity').value ? parseInt(row.querySelector('.import-intensity').value) : null,
            tasting_note: row.querySelector('.import-note').value.trim() || null,
            decaffeinato: row.querySelector('.import-decaffeinato').checked
        };

        capsules.push(capsule);
    });

    if (capsules.length === 0) {
        showToast(state.language === 'en' ? 'No valid capsules to import' : '没有有效的胶囊可导入', 'error');
        return;
    }

    elements.batchImportPreview.textContent = JSON.stringify(capsules, null, 2);
    elements.batchImportPreview.classList.remove('hidden');
    elements.confirmImportBtn.classList.remove('hidden');
}

async function confirmBatchImport() {
    const rows = document.querySelectorAll('#batchImportRows .batch-import-row');
    const capsules = [];

    rows.forEach(row => {
        const name = row.querySelector('.import-name').value.trim();
        if (!name) return;

        const sizeMl = parseInt(row.querySelector('.import-size').value) || 40;
        const sizeMl2 = row.querySelector('.import-size2').value ? parseInt(row.querySelector('.import-size2').value) : null;
        const bestServe = sizeMl2
            ? (sizeMl2 > sizeMl ? getSizeName(sizeMl2) : getSizeName(sizeMl))
            : getSizeName(sizeMl);

        const capsule = {
            name: name,
            brand_id: row.querySelector('.import-brand').value ? parseInt(row.querySelector('.import-brand').value) : null,
            line: row.querySelector('.import-line').value,
            size_ml: sizeMl,
            size_ml2: sizeMl2,
            best_serve: bestServe,
            intensity: row.querySelector('.import-intensity').value ? parseInt(row.querySelector('.import-intensity').value) : null,
            tasting_note: row.querySelector('.import-note').value.trim() || null,
            decaffeinato: row.querySelector('.import-decaffeinato').checked
        };

        capsules.push(capsule);
    });

    if (capsules.length === 0) {
        showToast(state.language === 'en' ? 'No valid capsules to import' : '没有有效的胶囊可导入', 'error');
        return;
    }

    try {
        await supabase.batchUpsertCapsules(capsules);
        showToast(state.language === 'en' ? `Imported ${capsules.length} capsules` : `已导入 ${capsules.length} 个胶囊`, 'success');
        closeBatchImportModal();
        await loadAdminData();
        await loadCapsulesData();
    } catch (error) {
        showToast(state.language === 'en' ? 'Import failed' : '导入失败', 'error');
    }
}

// ==================== Event Listeners ====================
function setupEventListeners() {
    elements.langToggle.addEventListener('click', toggleLanguage);

    // Refresh button - force reload on iOS
    elements.refreshBtn.addEventListener('click', async () => {
        // Try to unregister service worker first
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            for (const reg of registrations) {
                await reg.unregister();
            }
        }
        // Clear caches
        if ('caches' in window) {
            const keys = await caches.keys();
            for (const key of keys) {
                await caches.delete(key);
            }
        }
        // Reload
        window.location.reload(true);
    });

    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    elements.sizeButtons.forEach(btn => {
        btn.addEventListener('click', () => toggleSizeFilter(btn.dataset.size));
    });

    elements.originalLine.addEventListener('change', updateLineFilter);
    elements.vertuoLine.addEventListener('change', updateLineFilter);

    elements.pickBtn.addEventListener('click', pickRandomCapsule);

    elements.confirmBtn.addEventListener('click', confirmPick);
    elements.rerollBtn.addEventListener('click', pickRandomCapsule);

    elements.closeManage.addEventListener('click', closeInventoryManagement);
    elements.qtyMinus.addEventListener('click', () => adjustManageQty(-1));
    elements.qtyPlus.addEventListener('click', () => adjustManageQty(1));
    elements.deleteCapsule.addEventListener('click', () => {
        if (state.managingCapsuleId) {
            delete state.inventory[state.managingCapsuleId];
            saveInventory();
            renderInventory();
            renderCapsulesGrid();
            closeInventoryManagement();
            showToast(state.language === 'en' ? 'Removed from inventory' : '已从库存中移除', 'success');
        }
    });

    elements.searchCapsules.addEventListener('input', filterCapsules);
    elements.filterLine.addEventListener('change', filterCapsules);
    elements.filterType.addEventListener('change', filterCapsules);

    // Login/Register
    elements.loginBtn.addEventListener('click', login);
    elements.registerBtn.addEventListener('click', register);
    elements.skipLoginBtn.addEventListener('click', skipLogin);
    elements.closeLoginModal.addEventListener('click', skipLogin);
    elements.loginModal.addEventListener('click', (e) => {
        if (e.target === elements.loginModal) skipLogin();
    });
    elements.loginPassword.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') login();
    });

    // User modal
    elements.userBtn.addEventListener('click', openUserModal);
    elements.closeUserModal.addEventListener('click', closeUserModal);
    elements.logoutBtn.addEventListener('click', logout);

    elements.userModal.addEventListener('click', (e) => {
        if (e.target === elements.userModal) {
            closeUserModal();
        }
    });

    elements.installBtn.addEventListener('click', installApp);
    elements.dismissInstall.addEventListener('click', dismissInstallPrompt);

    // Admin tab
    elements.adminTab.addEventListener('click', checkAdminAccess);

    // Admin password modal
    elements.verifyAdminPasswordBtn.addEventListener('click', verifyAdminPassword);
    elements.closeAdminPasswordModal.addEventListener('click', closeAdminPasswordModal);
    elements.adminPasswordModal.addEventListener('click', (e) => {
        if (e.target === elements.adminPasswordModal) closeAdminPasswordModal();
    });
    elements.adminPasswordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') verifyAdminPassword();
    });

    // Brand management
    elements.addBrandBtn.addEventListener('click', addBrand);
    elements.newBrandName.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addBrand();
    });

    // Capsule management
    elements.addCapsuleBtn.addEventListener('click', openAddCapsuleModal);
    elements.clearAllCapsulesBtn.addEventListener('click', clearAllCapsules);
    elements.adminFilterBrand.addEventListener('change', renderAdminCapsules);
    elements.adminFilterLine.addEventListener('change', renderAdminCapsules);

    // Capsule edit modal
    elements.capsuleEditForm.addEventListener('submit', saveCapsule);
    elements.closeCapsuleEditModal.addEventListener('click', closeCapsuleEditModal);
    elements.capsuleEditModal.addEventListener('click', (e) => {
        if (e.target === elements.capsuleEditModal) closeCapsuleEditModal();
    });

    // Auto-update size when line changes
    elements.capsuleEditLine.addEventListener('change', () => {
        if (!state.editingCapsuleId) {
            // Only auto-update for new capsules, not edits
            elements.capsuleEditSize.value = elements.capsuleEditLine.value === 'Vertuo' ? 80 : 40;
            // Auto-fill Best Serve when size auto-updates
            if (!elements.capsuleEditBestServe.value ||
                elements.capsuleEditBestServe.dataset.auto === 'true') {
                elements.capsuleEditBestServe.value = getSizeName(parseInt(elements.capsuleEditSize.value));
                elements.capsuleEditBestServe.dataset.auto = 'true';
            }
        }
    });

    // Auto-fill Best Serve based on size selection
    elements.capsuleEditSize.addEventListener('change', function() {
        if (!elements.capsuleEditBestServe.value ||
            elements.capsuleEditBestServe.dataset.auto === 'true') {
            elements.capsuleEditBestServe.value = getSizeName(parseInt(this.value));
            elements.capsuleEditBestServe.dataset.auto = 'true';
        }
    });
    elements.capsuleEditSize2.addEventListener('change', function() {
        if (this.value && (!elements.capsuleEditBestServe.value ||
            elements.capsuleEditBestServe.dataset.auto === 'true')) {
            const primary = parseInt(elements.capsuleEditSize.value) || 0;
            const secondary = parseInt(this.value);
            const bestServe = (secondary > primary)
                ? getSizeName(secondary)
                : getSizeName(primary);
            elements.capsuleEditBestServe.value = bestServe;
            elements.capsuleEditBestServe.dataset.auto = 'true';
        }
    });

    // Import modal
    elements.importCapsulesBtn.addEventListener('click', openImportModal);
    elements.closeImportModal.addEventListener('click', closeImportModal);
    elements.importModal.addEventListener('click', (e) => {
        if (e.target === elements.importModal) closeImportModal();
    });
    elements.importJsonBtn.addEventListener('click', importCapsulesFromJSON);

    // Batch action bar
    elements.batchCancelBtn.addEventListener('click', clearBatchSelection);
    elements.batchEditBtn.addEventListener('click', openBatchEditModal);
    elements.batchInventoryBtn.addEventListener('click', openBatchInventoryModal);
    elements.batchDeleteBtn.addEventListener('click', openBatchDeleteModal);

    // Batch table checkboxes (delegated)
    elements.adminCapsulesBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('batch-checkbox')) {
            const id = parseInt(e.target.dataset.id);
            toggleCapsuleSelection(id);
        }
    });

    // Select all checkbox
    document.getElementById('selectAllCapsules').addEventListener('change', toggleSelectAllCapsules);

    // Batch Import Modal
    elements.batchImportBtn.addEventListener('click', openBatchImportModal);
    elements.closeBatchImportModal.addEventListener('click', closeBatchImportModal);
    elements.batchImportModal.addEventListener('click', (e) => {
        if (e.target === elements.batchImportModal) closeBatchImportModal();
    });
    elements.addImportRowBtn.addEventListener('click', () => addBatchImportRow());
    elements.loadExampleBtn.addEventListener('click', loadExampleImportData);
    elements.previewImportBtn.addEventListener('click', previewBatchImport);
    elements.confirmImportBtn.addEventListener('click', confirmBatchImport);

    // Batch Edit Modal
    elements.closeBatchEditModal.addEventListener('click', closeBatchEditModal);
    elements.batchEditModal.addEventListener('click', (e) => {
        if (e.target === elements.batchEditModal) closeBatchEditModal();
    });
    elements.confirmBatchEditBtn.addEventListener('click', applyBatchEdit);

    // Batch Edit field selection
    document.querySelectorAll('#batchEditFields .batch-edit-field').forEach(field => {
        field.addEventListener('click', () => {
            const checkbox = field.querySelector('input');
            checkbox.checked = !checkbox.checked;
            field.classList.toggle('selected', checkbox.checked);

            const fieldName = field.dataset.field;
            const valueGroup = document.getElementById(`batchValue${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`);
            if (valueGroup) {
                valueGroup.style.display = checkbox.checked ? 'block' : 'none';
            }
        });
    });

    // Batch Inventory Modal
    elements.closeBatchInventoryModal.addEventListener('click', closeBatchInventoryModal);
    elements.batchInventoryModal.addEventListener('click', (e) => {
        if (e.target === elements.batchInventoryModal) closeBatchInventoryModal();
    });
    elements.confirmBatchInvBtn.addEventListener('click', applyBatchInventory);

    // Batch Inventory radio selection
    document.querySelectorAll('#batchInvRadios .batch-inv-radio').forEach(radio => {
        radio.addEventListener('click', () => {
            document.querySelectorAll('#batchInvRadios .batch-inv-radio').forEach(r => r.classList.remove('selected'));
            radio.classList.add('selected');
            radio.querySelector('input').checked = true;
        });
    });

    // Batch Delete Modal
    elements.closeBatchDeleteModal.addEventListener('click', closeBatchDeleteModal);
    elements.batchDeleteModal.addEventListener('click', (e) => {
        if (e.target === elements.batchDeleteModal) closeBatchDeleteModal();
    });
    elements.confirmBatchDeleteBtn.addEventListener('click', applyBatchDelete);
}

// ==================== Tab Switching ====================
function switchTab(tabName) {
    // Check admin access
    if (tabName === 'admin' && !state.isAdmin) {
        checkAdminAccess();
        return;
    }

    state.currentTab = tabName;
    elements.tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
    if (tabName !== 'pick') {
        elements.result.classList.add('hidden');
    }
    // Load admin data when switching to admin tab
    if (tabName === 'admin' && state.isAdmin) {
        loadAdminData();
    }
    // Reload capsules when switching to capsules tab
    if (tabName === 'capsules') {
        loadCapsulesData();
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

    // Update app title based on language
    const titleEl = document.querySelector('header h1');
    if (titleEl) {
        titleEl.innerHTML = lang === 'en' ? '☕ Brewlette' : '☕ 随便喝';
    }

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

    document.querySelectorAll('[data-placeholder-en]').forEach(el => {
        el.placeholder = lang === 'en' ? el.dataset.placeholderEn : el.dataset.placeholderZh;
    });

    document.querySelectorAll('select option[data-en]').forEach(option => {
        option.textContent = lang === 'en' ? option.dataset.en : option.dataset.zh;
    });

    renderInventory();
    renderCapsulesGrid();
    if (state.currentResult) displayResult(state.currentResult);
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
}

function updateLineFilter() {
    state.selectedLines.Original = elements.originalLine.checked;
    state.selectedLines.Vertuo = elements.vertuoLine.checked;
}

function filterCapsules() {
    const search = elements.searchCapsules.value.toLowerCase();
    const lineFilter = elements.filterLine.value;
    const typeFilter = elements.filterType.value;

    state.filteredCapsules = state.capsules.filter(capsule => {
        const name = capsule.name_en?.toLowerCase() || capsule.name?.toLowerCase() || '';
        const nameZh = capsule.name_zh || '';
        if (search && !name.includes(search) && !nameZh.includes(search)) return false;
        if (lineFilter !== 'all' && capsule.line !== lineFilter) return false;
        if (typeFilter !== 'all' && capsule.pod_type !== typeFilter) return false;
        return true;
    });
    renderCapsulesGrid();
}

function getFilteredCapsules() {
    return getInventoryCapsules().filter(capsule => {
        if (state.selectedSize) {
            const primaryCategory = mapSizeToCategory(capsule.size_ml);
            const secondaryCategory = capsule.size_ml2 ? mapSizeToCategory(capsule.size_ml2) : null;
            if (primaryCategory !== state.selectedSize && secondaryCategory !== state.selectedSize) return false;
        }
        if (!state.selectedLines[capsule.line]) return false;
        return true;
    });
}

// ==================== Pick Random ====================
function pickRandomCapsule() {
    const total = getTotalCapsules();
    if (total === 0) {
        showToast(state.language === 'en' ? 'Your inventory is empty! Set it up in Inventory tab.' : '库存为空！请在库存标签页设置。', 'error');
        switchTab('inventory');
        return;
    }

    const available = getFilteredCapsules();
    if (available.length === 0) {
        elements.emptyFilter.classList.remove('hidden');
        elements.result.classList.add('hidden');
        return;
    }

    elements.emptyFilter.classList.add('hidden');
    const randomIndex = Math.floor(Math.random() * available.length);
    const selected = available[randomIndex];
    state.currentResult = selected;
    displayResult(selected);
}

function displayResult(capsule) {
    const lang = state.language;
    elements.resultName.textContent = lang === 'zh' ? (capsule.name_zh || capsule.name_en) : capsule.name_en;
    elements.resultLine.textContent = capsule.line;
    const sizes = capsule.size_ml ? [capsule.size_ml] : [];
    if (capsule.size_ml2) sizes.push(capsule.size_ml2);
    elements.resultSize.textContent = sizes.length ? sizes.join('/') + 'ml' : '-';
    elements.resultIntensity.textContent = capsule.intensity ? `Intensity ${capsule.intensity}` : '';
    elements.resultNote.textContent = lang === 'zh' ? capsule.tasting_note_zh : capsule.tasting_note_en || '';
    elements.result.classList.remove('hidden');
    elements.result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function confirmPick() {
    if (state.currentResult) {
        const capsuleId = state.currentResult.id;
        if (state.inventory[capsuleId]) {
            state.inventory[capsuleId].quantity--;
            if (state.inventory[capsuleId].quantity <= 0) {
                delete state.inventory[capsuleId];
            }
            saveInventory();
            renderInventory();
        }

        // Record consumption to Supabase (prevents database pause)
        if (state.isLoggedIn && state.user && state.user.id) {
            supabase.recordConsumption(state.user.id, capsuleId).catch(err => {
                console.log('Failed to record consumption:', err);
            });
        }

        showToast(state.language === 'en' ? 'Enjoy your coffee! ☕' : '享受你的咖啡！☕', 'success');
        elements.result.classList.add('hidden');
        state.currentResult = null;
    }
}

// ==================== Inventory Rendering ====================
function renderInventory() {
    const items = Object.values(state.inventory);
    elements.totalCapsules.textContent = getTotalCapsules();

    if (items.length === 0) {
        elements.emptyInventory.classList.remove('hidden');
        elements.inventoryList.innerHTML = '';
        elements.inventoryList.appendChild(elements.emptyInventory);
        return;
    }

    elements.emptyInventory.classList.add('hidden');
    const lang = state.language;

    const html = items.map(item => `
        <div class="inventory-item" data-id="${item.id}">
            <div class="inventory-item-left">
                <div class="inventory-color" style="background: ${item.color || '#6B5344'}"></div>
                <div>
                    <div class="inventory-name">${lang === 'zh' ? (item.name_zh || item.name_en) : item.name_en}</div>
                    <div class="inventory-details">${item.line} | ${item.size_ml}ml</div>
                </div>
            </div>
            <div class="inventory-qty">
                <span class="qty-badge">${item.quantity}</span>
            </div>
        </div>
    `).join('');

    elements.inventoryList.innerHTML = html;
    elements.inventoryList.querySelectorAll('.inventory-item').forEach(item => {
        item.addEventListener('click', () => openInventoryManagement(item.dataset.id));
    });
}

function openInventoryManagement(capsuleId) {
    const item = state.inventory[capsuleId];
    if (!item) return;
    state.managingCapsuleId = capsuleId;
    const lang = state.language;
    elements.manageCapsuleName.textContent = lang === 'zh' ? (item.name_zh || item.name_en) : item.name_en;
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

    // Record consumption when decreasing inventory
    if (delta < 0 && state.isLoggedIn && state.user && state.user.id) {
        supabase.recordConsumption(state.user.id, state.managingCapsuleId).catch(err => {
            console.log('Failed to record consumption:', err);
        });
    }

    if (newQty <= 0) {
        delete state.inventory[state.managingCapsuleId];
    } else {
        state.inventory[state.managingCapsuleId].quantity = newQty;
    }
    saveInventory();
    renderInventory();
    renderCapsulesGrid();
    if (newQty > 0) {
        elements.manageQty.textContent = newQty;
    } else {
        closeInventoryManagement();
    }
}

// ==================== Capsules Grid ====================
function renderCapsulesGrid() {
    const capsules = state.filteredCapsules;
    if (capsules.length === 0) {
        elements.emptyCapsules.classList.remove('hidden');
        elements.capsulesList.innerHTML = '';
        return;
    }
    elements.emptyCapsules.classList.add('hidden');
    const lang = state.language;

    const html = capsules.map(capsule => {
        const inInventory = state.inventory[capsule.id];
        const invQty = inInventory ? inInventory.quantity : 0;
        const capsuleName = lang === 'zh' ? (capsule.name_zh || capsule.name_en) : (capsule.name_en || capsule.name || '-');
        const tastingNote = capsule.tasting_note_en || capsule.tasting_note || '';
        const tastingBadges = tastingNote ? tastingNote.split(',').map(note =>
            `<span class="tasting-badge">${note.trim()}</span>`
        ).join('') : '';
        return `
            <div class="capsule-card ${invQty > 0 ? 'in-stock' : 'out-of-stock'}" data-id="${capsule.id}">
                <div class="capsule-color-bar" style="background: ${capsule.color || '#6B5344'}"></div>
                <div class="capsule-name">${capsuleName}</div>
                <div class="capsule-meta">
                    <span class="capsule-line">${capsule.line || '-'}</span>
                    <span>${capsule.size_ml || '-'}ml | ${capsule.pod_type || '-'}</span>
                    ${capsule.intensity ? `<span>Intensity: ${capsule.intensity}</span>` : ''}
                    ${tastingBadges ? `<div class="tasting-notes">${tastingBadges}</div>` : ''}
                    <span class="stock-badge ${invQty > 0 ? 'stock-ok' : 'stock-empty'}">
                        ${invQty > 0 ? `${invQty} ${lang === 'en' ? 'in stock' : '库存'}` : (lang === 'en' ? 'Out of stock' : '无库存')}
                    </span>
                </div>
            </div>
        `;
    }).join('');

    elements.capsulesList.innerHTML = html;
    const cards = elements.capsulesList.querySelectorAll('.capsule-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Use == for type coercion (id might be number or string)
            const capsule = state.capsules.find(c => c.id == card.dataset.id);
            if (capsule) openAddInventoryModal(capsule);
        });
    });
}

function openAddInventoryModal(capsule) {
    const currentQty = state.inventory[capsule.id] ? state.inventory[capsule.id].quantity : 0;
    const lang = state.language;
    const name = lang === 'zh' ? (capsule.name_zh || capsule.name_en) : capsule.name_en;

    const qty = prompt(
        lang === 'zh' ? `设置 ${name} 的库存数量：` : `Set quantity for ${name}:`,
        currentQty.toString()
    );

    if (qty !== null) {
        const numQty = parseInt(qty, 10);
        if (!isNaN(numQty) && numQty >= 0) {
            setInventoryQuantity(capsule.id, numQty);
            showToast(lang === 'en' ? 'Inventory updated!' : '库存已更新！', 'success');
        } else {
            showToast(lang === 'en' ? 'Invalid quantity' : '无效数量', 'error');
        }
    }
}

// ==================== User Modal ====================
function openUserModal() {
    if (!state.isLoggedIn) {
        elements.loginModal.classList.remove('hidden');
        return;
    }
    elements.userModal.classList.remove('hidden');
    elements.profileAvatar.textContent = state.user.username.charAt(0).toUpperCase();
    elements.profileName.textContent = state.user.username;
}

function closeUserModal() {
    elements.userModal.classList.add('hidden');
}

// ==================== Toast ====================
function showToast(message, type = '') {
    elements.toast.textContent = message;
    elements.toast.className = 'toast';
    if (type) elements.toast.classList.add(type);
    elements.toast.classList.remove('hidden');
    setTimeout(() => elements.toast.classList.add('hidden'), 2500);
}

// ==================== Service Worker ====================
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then(reg => {
                console.log('Service Worker registered');
                // Check for updates
                reg.addEventListener('updatefound', () => {
                    const newWorker = reg.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New version available - force activate immediately
                            newWorker.postMessage({ type: 'SKIP_WAITING' });
                            // Reload the page to get fresh content
                            setTimeout(() => {
                                window.location.reload();
                            }, 500);
                        }
                    });
                });
            })
            .catch(err => console.log('SW registration failed:', err));
    }
}

// Check if iOS
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Force refresh for iOS
if (isIOS()) {
    window.addEventListener('load', () => {
        // Clear caches on iOS by unregistering SW
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(registrations => {
                for (let registration of registrations) {
                    registration.unregister().then(() => {
                        console.log('SW unregistered for iOS refresh');
                        window.location.reload();
                    });
                }
            });
        }
    });
}

// ==================== Install Prompt ====================
let deferredPrompt;

function checkInstallPrompt() {
    // Chrome/Edge: Use beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        elements.installPrompt.classList.remove('hidden');
    });
    window.addEventListener('appinstalled', () => {
        elements.installPrompt.classList.add('hidden');
        deferredPrompt = null;
    });

    // Safari: Check if already installed or show manual instructions
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (isSafari) {
        // Check if running in standalone mode (already installed)
        if (window.matchMedia('(display-mode: standalone)').matches) {
            return; // Already installed
        }
        // Show install instructions for Safari
        const installText = document.getElementById('installText');
        const installBtn = document.getElementById('installBtn');
        if (installText) {
            installText.textContent = 'Tap Share > Add to Home Screen';
        }
        if (installBtn) {
            installBtn.style.display = 'none'; // Hide install button for Safari
        }
        setTimeout(() => {
            elements.installPrompt.classList.remove('hidden');
        }, 2000);
    }
}

function installApp() {
    if (deferredPrompt) deferredPrompt.prompt();
}

function dismissInstallPrompt() {
    elements.installPrompt.classList.add('hidden');
}

// ==================== Start App ====================
document.addEventListener('DOMContentLoaded', init);
