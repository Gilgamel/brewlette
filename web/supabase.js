/**
 * Supabase Client for PWA
 * Handles all database operations
 *
 * To configure:
 * 1. Go to your Supabase project dashboard
 * 2. Go to Settings > API
 * 3. Copy the "Project URL" and "anon public" key
 * 4. Replace the values below
 */

// ====== TODO: Replace with your Supabase credentials ======
const SUPABASE_URL = 'https://qwqjfsgemtxihpzrcrnv.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cWpmc2dlbXR4aWhwenJjcm52Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxMzUyMTQsImV4cCI6MjA4NzcxMTIxNH0.HOWKRx21UJKiRWZ_vXpUkUXg9NSf4EtV6ZbSalQeMys';
// =========================================================

const supabaseUrl = SUPABASE_URL;
const supabaseKey = SUPABASE_KEY;

// ==================== Supabase Client ====================
const supabase = {
    baseUrl: supabaseUrl,

    async request(endpoint, method = 'GET', body = null) {
        const url = `${supabaseUrl}/rest/v1/${endpoint}`;

        const headers = {
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`,
            'Content-Type': 'application/json',
            'Prefer': method === 'POST' ? 'return=representation' : 'return=minimal'
        };

        const options = {
            method,
            headers,
            mode: 'cors',
            cache: 'no-store'
        };
        if (body) options.body = JSON.stringify(body);

        try {
            const response = await fetch(url, options);

            // Log for debugging
            console.log(`Supabase ${method} ${endpoint}:`, response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Supabase error:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            // Handle empty responses (e.g., DELETE returns 204 No Content)
            const text = await response.text();
            const data = text ? JSON.parse(text) : null;
            return data;
        } catch (error) {
            console.error('Supabase request failed:', error);
            throw error;
        }
    },

    // ==================== Capsule Operations ====================
    async getAllCapsules() {
        return this.request('capsules?select=*&order=line,size_ml');
    },

    async getCapsuleById(id) {
        const result = await this.request(`capsules?id=eq.${id}&select=*`);
        return result[0] || null;
    },

    // ==================== User Operations ====================
    async createUser(username) {
        // Check if user exists first
        const existing = await this.request(`users?username=eq.${username}&select=*`);
        if (existing.length > 0) {
            return existing[0];
        }
        return this.request('users', 'POST', { username });
    },

    async getUserByUsername(username) {
        const result = await this.request(`users?username=eq.${username}&select=*`);
        return result[0] || null;
    },

    async getAllUsers() {
        return this.request('users?select=*&order=username');
    },

    // ==================== Inventory Operations ====================
    async getUserInventory(userId) {
        return this.request(
            `inventory?user_id=eq.${userId}&select=*,capsules(*)&order=capsules(name)`
        );
    },

    async getAvailablePods(userId) {
        return this.request(
            `inventory?user_id=eq.${userId}&quantity=gt.0&select=*,capsules(*)&order=capsules(name)`
        );
    },

    async addToInventory(userId, podId, quantity) {
        // Check if item exists
        const existing = await this.request(
            `inventory?user_id=eq.${userId}&pod_id=eq.${podId}&select=id,quantity`
        );

        if (existing.length > 0) {
            // Update quantity
            const newQty = existing[0].quantity + quantity;
            return this.request(`inventory?id=eq.${existing[0].id}`, 'PATCH', { quantity: newQty });
        } else {
            // Insert new
            return this.request('inventory', 'POST', {
                user_id: userId,
                pod_id: podId,
                quantity
            });
        }
    },

    async updateInventoryQuantity(inventoryId, quantity) {
        if (quantity <= 0) {
            return this.request(`inventory?id=eq.${inventoryId}`, 'DELETE');
        }
        return this.request(`inventory?id=eq.${inventoryId}`, 'PATCH', { quantity });
    },

    async decrementInventory(inventoryId) {
        const current = await this.request(`inventory?id=eq.${inventoryId}&select=quantity`);
        if (current.length > 0) {
            const newQty = current[0].quantity - 1;
            if (newQty <= 0) {
                return this.request(`inventory?id=eq.${inventoryId}`, 'DELETE');
            }
            return this.request(`inventory?id=eq.${inventoryId}`, 'PATCH', { quantity: newQty });
        }
    },

    async removeFromInventory(inventoryId) {
        return this.request(`inventory?id=eq.${inventoryId}`, 'DELETE');
    },

    // ==================== Admin Operations ====================
    async saveCapsules(capsules) {
        const results = [];
        for (const capsule of capsules) {
            const existing = await this.request(`capsules?name=eq.${encodeURIComponent(capsule.name)}&select=id`);
            if (existing.length > 0) {
                await this.request(`capsules?id=eq.${existing[0].id}`, 'PATCH', capsule);
            } else {
                await this.request('capsules', 'POST', capsule);
            }
            results.push(capsule);
        }
        return results;
    },

    async clearCapsules() {
        // First delete all inventory entries
        await this.request('inventory?id=gt.0', 'DELETE');
        // Then delete all capsules
        return this.request('capsules?id=gt.0', 'DELETE');
    },

    async getCapsuleCount() {
        const result = await this.request('capsules?select=count');
        return result.length;
    },

    // ==================== Daily Consumption Operations ====================
    async recordConsumption(userId, podId) {
        // Try to get existing record for today
        const today = new Date().toISOString().split('T')[0];
        const existing = await this.request(
            `daily_consumption?user_id=eq.${userId}&pod_id=eq.${podId}&consumption_date=eq.${today}&select=id,quantity`
        );

        if (existing.length > 0) {
            // Update quantity
            const newQty = existing[0].quantity + 1;
            return this.request(`daily_consumption?id=eq.${existing[0].id}`, 'PATCH', { quantity: newQty });
        } else {
            // Insert new
            return this.request('daily_consumption', 'POST', {
                user_id: userId,
                pod_id: podId,
                quantity: 1,
                consumption_date: today
            });
        }
    },

    async getTodayConsumption(userId) {
        const today = new Date().toISOString().split('T')[0];
        return this.request(
            `daily_consumption?user_id=eq.${userId}&consumption_date=eq.${today}&select=*,capsules(*)&order=capsules(name)`
        );
    },

    async getConsumptionHistory(userId, days = 7) {
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        const startDateStr = startDate.toISOString().split('T')[0];

        return this.request(
            `daily_consumption?user_id=eq.${userId}&consumption_date=gte.${startDateStr}&select=*,capsules(*)&order=consumption_date desc, capsules(name)`
        );
    },

    // ==================== Brand Operations ====================
    async getAllBrands() {
        return this.request('brands?select=*&order=name');
    },

    async createBrand(name) {
        return this.request('brands', 'POST', { name });
    },

    async deleteBrand(id) {
        return this.request(`brands?id=eq.${id}`, 'DELETE');
    },

    async updateBrand(id, name) {
        return this.request(`brands?id=eq.${id}`, 'PATCH', { name });
    },

    // ==================== Capsule Admin Operations ====================
    async createCapsule(capsule) {
        return this.request('capsules', 'POST', capsule);
    },

    async updateCapsule(id, capsule) {
        return this.request(`capsules?id=eq.${id}`, 'PATCH', capsule);
    },

    async deleteCapsule(id) {
        return this.request(`capsules?id=eq.${id}`, 'DELETE');
    },

    async clearAllCapsules() {
        // First delete all inventory entries for these capsules
        await this.request('inventory?pod_id=gt.0', 'DELETE');
        // Then delete all capsules
        return this.request('capsules?id=gt.0', 'DELETE');
    },

    // ==================== Admin Config Operations ====================
    async getAdminConfig(key) {
        const result = await this.request(`admin_config?key=eq.${key}&select=value`);
        return result.length > 0 ? result[0].value : null;
    },

    async setAdminConfig(key, value) {
        const existing = await this.request(`admin_config?key=eq.${key}&select=id`);
        if (existing.length > 0) {
            return this.request(`admin_config?key=eq.${key}`, 'PATCH', { value, updated_at: new Date().toISOString() });
        } else {
            return this.request('admin_config', 'POST', { key, value });
        }
    },

    // ==================== Capsule Join Operations ====================
    async getCapsulesWithBrands() {
        return this.request('capsules?select=*,brands(name)&order=brand_id.asc,line.asc,name.asc');
    },

    // ==================== Admin Operations ====================
    async verifyAdminPassword(password) {
        const stored = await this.getAdminConfig('admin_password');
        return stored === password;
    },

    async deleteAllCapsules() {
        await this.request('daily_consumption?pod_id=gt.0', 'DELETE');
        await this.request('inventory?pod_id=gt.0', 'DELETE');
        return this.request('capsules?id=gt.0', 'DELETE');
    },

    // ==================== Batch Operations ====================
    async batchUpsertCapsules(capsules) {
        const results = [];
        for (const capsule of capsules) {
            if (!capsule.name) continue;
            const existing = await this.request(`capsules?name=eq.${encodeURIComponent(capsule.name)}&select=id`);
            if (existing.length > 0) {
                await this.request(`capsules?id=eq.${existing[0].id}`, 'PATCH', capsule);
            } else {
                await this.request('capsules', 'POST', capsule);
            }
            results.push(capsule);
        }
        return results;
    },

    async batchUpdateCapsules(ids, updates) {
        const results = [];
        for (const id of ids) {
            await this.request(`capsules?id=eq.${id}`, 'PATCH', updates);
            results.push(id);
        }
        return results;
    },

    async batchDeleteCapsules(ids) {
        // Delete related daily_consumption first
        for (const id of ids) {
            await this.request(`daily_consumption?pod_id=eq.${id}`, 'DELETE');
            await this.request(`inventory?pod_id=eq.${id}`, 'DELETE');
            await this.request(`capsules?id=eq.${id}`, 'DELETE');
        }
        return ids;
    },

    async batchUpdateInventory(userId, updates) {
        const results = [];
        for (const update of updates) {
            const { pod_id, action, quantity = 1 } = update;
            const existing = await this.request(
                `inventory?user_id=eq.${userId}&pod_id=eq.${pod_id}&select=id,quantity`
            );

            if (existing.length > 0) {
                const currentQty = existing[0].quantity;
                let newQty;

                switch (action) {
                    case 'add':
                        newQty = currentQty + quantity;
                        break;
                    case 'remove':
                        newQty = currentQty - quantity;
                        break;
                    case 'set':
                        newQty = quantity;
                        break;
                    default:
                        newQty = currentQty;
                }

                if (newQty <= 0) {
                    await this.request(`inventory?id=eq.${existing[0].id}`, 'DELETE');
                } else {
                    await this.request(`inventory?id=eq.${existing[0].id}`, 'PATCH', { quantity: newQty });
                }
            } else if (action === 'add' || action === 'set') {
                const qty = action === 'set' ? quantity : quantity;
                if (qty > 0) {
                    await this.request('inventory', 'POST', {
                        user_id: userId,
                        pod_id: pod_id,
                        quantity: qty
                    });
                }
            }
            results.push({ pod_id, action, quantity });
        }
        return results;
    }
};

// ==================== Export ====================
window.supabase = supabase;
