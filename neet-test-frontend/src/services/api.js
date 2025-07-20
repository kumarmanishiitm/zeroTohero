import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging and authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    const tokenStatus = token ? `Token: ${token.substring(0, 20)}...` : 'NO TOKEN';
    console.log('API Request:', config.method?.toUpperCase(), config.url, tokenStatus);
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Token attached to request');
    } else {
      console.warn('⚠️ No token found in localStorage - request will be unauthorized');
    }
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Authentication failed - removing token and redirecting to login');
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    console.error('Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const testAPI = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Auth endpoints
  quickLogin: (username) => api.post('/auth/quick-login', { username }),
  getCurrentUser: () => api.get('/auth/me'),

  // Subjects
  getSubjects: () => api.get('/subjects'),

  // Topics
  getTopicsBySubject: (subjectId) => api.get(`/subjects/${subjectId}/topics`),

  // Questions
  generateQuestions: (data) => api.post('/questions/generate', data),

  // Tests
  startTest: (data) => api.post('/tests/start', data),
  submitTest: (testId, answers, testQuestions = null) => api.post(`/tests/${testId}/submit`, { 
    answers, 
    test_questions: testQuestions 
  }),
  getTestStatus: (testId) => api.get(`/tests/${testId}/status`),
  getTestResults: (testId) => api.get(`/tests/${testId}/results`),
  
  // Test History and Analytics
  getUserTestHistory: () => api.get('/tests/history'),
  getUserAnalytics: () => api.get('/tests/analytics'),
};

export default api;
