import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and error handling
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get system statistics
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },

  // Get plan count
  getPlanCount: async () => {
    const response = await api.get('/plans/count');
    return response.data;
  },

  // Get list of all plans
  getPlansList: async () => {
    const response = await api.get('/plans/list');
    return response.data;
  },

  // Compare plans with user profile
  comparePlans: async (userProfile) => {
    const response = await api.post('/compare', {
      userProfile,
    });
    return response.data;
  },

  // Direct query to RAG system
  queryPlans: async (userProfile, question = null) => {
    const response = await api.post('/query', {
      userProfile,
      question,
    });
    return response.data;
  },
};

// Error handling utilities
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return `Bad request: ${data.detail || 'Invalid data provided'}`;
      case 401:
        return 'Unauthorized: Please log in again';
      case 403:
        return 'Forbidden: You don\'t have permission to access this resource';
      case 404:
        return 'Not found: The requested resource was not found';
      case 422:
        return `Validation error: ${data.detail || 'Invalid input data'}`;
      case 500:
        return 'Server error: Something went wrong on our end';
      case 503:
        return 'Service unavailable: The system is currently unavailable';
      default:
        return `Error ${status}: ${data.detail || 'An unexpected error occurred'}`;
    }
  } else if (error.request) {
    // Network error
    return 'Network error: Unable to connect to the server. Please check your internet connection.';
  } else {
    // Other error
    return `Error: ${error.message || 'An unexpected error occurred'}`;
  }
};

// Loading states management
export const createLoadingState = () => {
  let loadingCount = 0;
  const listeners = new Set();

  const notifyListeners = () => {
    listeners.forEach(listener => listener(loadingCount > 0));
  };

  return {
    start: () => {
      loadingCount++;
      notifyListeners();
    },
    stop: () => {
      loadingCount = Math.max(0, loadingCount - 1);
      notifyListeners();
    },
    subscribe: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    get isLoading() {
      return loadingCount > 0;
    }
  };
};

// Cache utilities
export const cache = {
  data: new Map(),
  timestamps: new Map(),
  
  set: (key, value, ttl = 5 * 60 * 1000) => { // 5 minutes default
    cache.data.set(key, value);
    cache.timestamps.set(key, Date.now() + ttl);
  },
  
  get: (key) => {
    const timestamp = cache.timestamps.get(key);
    if (timestamp && Date.now() < timestamp) {
      return cache.data.get(key);
    }
    // Remove expired cache
    cache.data.delete(key);
    cache.timestamps.delete(key);
    return null;
  },
  
  clear: () => {
    cache.data.clear();
    cache.timestamps.clear();
  },
  
  remove: (key) => {
    cache.data.delete(key);
    cache.timestamps.delete(key);
  }
};

// Enhanced API service with caching and loading states
export const enhancedApiService = {
  ...apiService,
  
  // Cached version of getStats
  getStatsCached: async () => {
    const cacheKey = 'stats';
    const cached = cache.get(cacheKey);
    if (cached) return cached;
    
    const data = await apiService.getStats();
    cache.set(cacheKey, data, 2 * 60 * 1000); // 2 minutes cache
    return data;
  },
  
  // Cached version of getPlanCount
  getPlanCountCached: async () => {
    const cacheKey = 'planCount';
    const cached = cache.get(cacheKey);
    if (cached) return cached;
    
    const data = await apiService.getPlanCount();
    cache.set(cacheKey, data, 5 * 60 * 1000); // 5 minutes cache
    return data;
  },
  
  // Cached version of getPlansList
  getPlansListCached: async () => {
    const cacheKey = 'plansList';
    const cached = cache.get(cacheKey);
    if (cached) return cached;
    
    const data = await apiService.getPlansList();
    cache.set(cacheKey, data, 10 * 60 * 1000); // 10 minutes cache
    return data;
  },
};

export default api; 