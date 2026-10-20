// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// Utility: Make authenticated API request
export async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        ...options
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// Auth API
export const authAPI = {
    async register(username, email, password) {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    },

    async login(username, password) {
        return apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },

    async logout() {
        return apiRequest('/auth/logout', { method: 'POST' });
    },

    async getCurrentUser() {
        return apiRequest('/auth/me');
    }
};

// Profile API
export const profileAPI = {
    async getProfile() {
        return apiRequest('/users/me');
    },

    async updateProfile(profileData) {
        return apiRequest('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(profileData)
        });
    }
};

// Posts API
export const postsAPI = {
    async getPosts(offset = 0, limit = 20) {
        return apiRequest(`/posts?offset=${offset}&limit=${limit}`);
    },

    async createPost(title, content, category) {
        return apiRequest('/posts', {
            method: 'POST',
            body: JSON.stringify({ title, content, category })
        });
    },

    async getPost(id) {
        return apiRequest(`/posts/${id}`);
    }
};

// Bikes API
export const bikesAPI = {
    async getBikes() {
        return apiRequest('/bikes/my-bikes');
    },

    async addBike(bikeData) {
        return apiRequest('/bikes', {
            method: 'POST',
            body: JSON.stringify(bikeData)
        });
    }
};
