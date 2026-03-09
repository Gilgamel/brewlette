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
    managingCapsuleId: null
};

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
    dismissInstall: document.getElementById('dismissInstall')
};

// ==================== Initialization ====================
async function init() {
    await loadCapsulesData();
    await checkLoginStatus();
    setupEventListeners();
    registerServiceWorker();
    checkInstallPrompt();
    renderInventory();
    renderCapsulesGrid();
    applyLanguage(state.language);
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
        const response = await fetch('./data/capsules.json');
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

// ==================== Event Listeners ====================
function setupEventListeners() {
    elements.langToggle.addEventListener('click', toggleLanguage);

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
    if (tabName !== 'pick') {
        elements.result.classList.add('hidden');
    }
    // Render capsules when switching to capsules tab
    if (tabName === 'capsules') {
        renderCapsulesGrid();
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
        if (state.selectedSize && capsule.pod_type !== state.selectedSize) return false;
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
    elements.resultSize.textContent = `${capsule.size_ml}ml`;
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
        return `
            <div class="capsule-card ${invQty > 0 ? 'in-stock' : 'out-of-stock'}" data-id="${capsule.id}">
                <div class="capsule-color-bar" style="background: ${capsule.color || '#6B5344'}"></div>
                <div class="capsule-name">${lang === 'zh' ? (capsule.name_zh || capsule.name_en) : capsule.name_en}</div>
                <div class="capsule-meta">
                    <span class="capsule-line">${capsule.line}</span>
                    <span>${capsule.size_ml}ml | ${capsule.pod_type}</span>
                    ${capsule.intensity ? `<span>Intensity: ${capsule.intensity}</span>` : ''}
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
                            // New version available
                            showToast(
                                state.language === 'en'
                                    ? 'New version available! Refresh to update.'
                                    : '有新版本可用！刷新以更新。',
                                'success'
                            );
                        }
                    });
                });
            })
            .catch(err => console.log('SW registration failed:', err));
    }
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
