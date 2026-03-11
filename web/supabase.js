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

            const data = await response.json();
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
        return this.request('inventory', 'DELETE', 'id=gt.0');
    },

    async getCapsuleCount() {
        const result = await this.request('capsules?select=count');
        return result.length;
    }
};

// ==================== Export ====================
window.supabase = supabase;
