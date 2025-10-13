// Environment configuration using Vite environment variables
// This file loads environment variables from .env and .env.local files

const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

// Debug logging (always show in development, or when debug mode is enabled)
if (isDevelopment || import.meta.env.VITE_DEBUG_MODE === 'true') {
  console.log('🔧 Environment config loading...');
  console.log('isDevelopment:', isDevelopment);
  console.log('isProduction:', isProduction);
  console.log('All import.meta.env:', import.meta.env);
}

// Helper function to get environment variables with fallbacks
const getEnvVar = (key: string, fallback: string = ''): string => {
  const value = import.meta.env[key];
  console.log(`🔍 Getting ${key}:`, value || 'NOT SET');
  return value || fallback;
};

// Environment configuration
export const ENV_CONFIG = {
  // App Configuration
  APP_NAME: getEnvVar('VITE_APP_NAME', 'Style AI'),
  APP_VERSION: getEnvVar('VITE_APP_VERSION', '0.0.1'),
  
  // API Configuration
  API_URL: getEnvVar('VITE_API_URL'),
  API_TIMEOUT: parseInt(getEnvVar('VITE_API_TIMEOUT', '10000'), 10),
  
  // Stripe Configuration
  STRIPE_PUBLISHABLE_KEY: getEnvVar('VITE_STRIPE_PUBLISHABLE_KEY', ''),
  
  // Development flags
  DEBUG_MODE: getEnvVar('VITE_DEBUG_MODE', 'false') === 'true',
  ENABLE_CONSOLE_LOGS: getEnvVar('VITE_ENABLE_CONSOLE_LOGS', 'false') === 'true',
  
  // Environment flags
  IS_DEVELOPMENT: isDevelopment,
  IS_PRODUCTION: isProduction,
};

// Export commonly used values for convenience
export const API_URL = ENV_CONFIG.API_URL;
export const STRIPE_PUBLISHABLE_KEY = ENV_CONFIG.STRIPE_PUBLISHABLE_KEY;
export const APP_NAME = ENV_CONFIG.APP_NAME;

// Always show the final configuration
console.log('🎯 Final Environment Configuration:', {
  API_URL: ENV_CONFIG.API_URL,
  STRIPE_PUBLISHABLE_KEY: ENV_CONFIG.STRIPE_PUBLISHABLE_KEY ? '***SET***' : 'NOT SET',
  APP_NAME: ENV_CONFIG.APP_NAME,
  DEBUG_MODE: ENV_CONFIG.DEBUG_MODE,
  IS_DEVELOPMENT: ENV_CONFIG.IS_DEVELOPMENT,
  IS_PRODUCTION: ENV_CONFIG.IS_PRODUCTION,
});
