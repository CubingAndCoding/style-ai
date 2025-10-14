import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.styleai.app',
  appName: 'Style AI',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    Camera: {
      permissions: ['camera', 'photos']
    }
  }
};

export default config;

