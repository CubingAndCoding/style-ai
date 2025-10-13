import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';
import { ENV_CONFIG } from '../config/environment';

const ConfigTest: React.FC = () => {
  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>Configuration Test</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <h3>API Configuration:</h3>
        <p><strong>BASE_URL:</strong> {ENV_CONFIG.API_URL}</p>
        
        <h3>Stripe Configuration:</h3>
        <p><strong>PUBLISHABLE_KEY:</strong> {ENV_CONFIG.STRIPE_PUBLISHABLE_KEY}</p>
        <p><strong>Key starts with pk_test:</strong> {ENV_CONFIG.STRIPE_PUBLISHABLE_KEY?.startsWith('pk_test_') ? 'Yes' : 'No'}</p>
        <p><strong>Key length:</strong> {ENV_CONFIG.STRIPE_PUBLISHABLE_KEY?.length || 0}</p>
        
        <h3>App Configuration:</h3>
        <p><strong>App Name:</strong> {ENV_CONFIG.APP_NAME}</p>
        <p><strong>Debug Mode:</strong> {ENV_CONFIG.DEBUG_MODE ? 'Yes' : 'No'}</p>
        <p><strong>Is Development:</strong> {ENV_CONFIG.IS_DEVELOPMENT ? 'Yes' : 'No'}</p>
      </IonCardContent>
    </IonCard>
  );
};

export default ConfigTest;


