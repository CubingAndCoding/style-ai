/// <reference types="vitest" />

import legacy from '@vitejs/plugin-legacy'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    legacy()
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
  // Vite automatically loads .env files and makes VITE_ prefixed variables
  // available via import.meta.env - no additional configuration needed
  
  // Explicitly define environment variables
  define: {
    // This ensures environment variables are available at build time
    __VITE_API_URL__: JSON.stringify(process.env.VITE_API_URL),
    __VITE_STRIPE_PUBLISHABLE_KEY__: JSON.stringify(process.env.VITE_STRIPE_PUBLISHABLE_KEY),
  },
  
  // Production build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ionic: ['@ionic/react', '@ionic/react-router'],
          stripe: ['@stripe/react-stripe-js', '@stripe/stripe-js']
        }
      }
    }
  },
  
  // Server configuration for preview
  preview: {
    port: 3000,
    host: '0.0.0.0'
  }
})
