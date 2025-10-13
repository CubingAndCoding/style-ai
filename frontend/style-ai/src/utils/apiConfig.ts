import { API_URL, STRIPE_PUBLISHABLE_KEY } from '../config/environment';

// API Configuration
export const API_CONFIG = {
  BASE_URL: API_URL,
  ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    UPLOAD: '/upload',
    USAGE_INFO: '/auth/usage-info',
    PURCHASE_CREDITS: '/auth/purchase-credits',
    CREATE_PAYMENT_INTENT: '/auth/create-payment-intent',
    CONFIRM_PAYMENT: '/auth/confirm-payment'
  }
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Stripe Configuration
export const STRIPE_CONFIG = {
  PUBLISHABLE_KEY: STRIPE_PUBLISHABLE_KEY
};

