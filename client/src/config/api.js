// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  CHECK_AUTH: `${API_BASE_URL}/api/auth/check`,
  PROJECTS: `${API_BASE_URL}/api/projects`,
  TODOS: `${API_BASE_URL}/api/todos`,
};

export default API_BASE_URL;
