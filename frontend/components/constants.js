// API Configuration
export const API_BASE_URL = 'http://localhost:5000/api';

// For different platforms:
// Android Emulator: 'http://10.0.2.2:5000/api'
// Physical Device: 'http://YOUR_IP_ADDRESS:5000/api'

export const API_ENDPOINTS = {
  REGISTER: `${API_BASE_URL}/register`,
  DETECT: `${API_BASE_URL}/detect`,
};

// Colors
export const COLORS = {
  PRIMARY: '#007AFF',
  SUCCESS: '#34C759',
  ERROR: '#FF3B30',
  BACKGROUND: '#f5f5f5',
  WHITE: '#ffffff',
  TEXT: '#333333',
  PLACEHOLDER: '#999999',
};