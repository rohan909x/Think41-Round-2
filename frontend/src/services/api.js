import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send a message and get AI response
  sendMessage: async (message, sessionId = null, userId = 1) => {
    const payload = {
      message,
      user_id: userId,
    };
    
    if (sessionId) {
      payload.session_id = sessionId;
    }
    
    const response = await api.post('/api/chat', payload);
    return response.data;
  },

  // Get a specific chat session
  getSession: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  },

  // List all chat sessions
  getSessions: async () => {
    const response = await api.get('/api/sessions');
    return response.data;
  },

  // Delete a chat session
  deleteSession: async (sessionId) => {
    const response = await api.delete(`/api/sessions/${sessionId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

// Utility function to format timestamps
export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

export default api; 