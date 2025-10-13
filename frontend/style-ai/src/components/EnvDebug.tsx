import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';

const EnvDebug: React.FC = () => {
  const envVars = {
    'VITE_API_URL': import.meta.env.VITE_API_URL,
    'VITE_STRIPE_PUBLISHABLE_KEY': import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY,
    'NODE_ENV': import.meta.env.NODE_ENV,
    'MODE': import.meta.env.MODE,
    'DEV': import.meta.env.DEV,
    'PROD': import.meta.env.PROD,
  };

  const allEnvVars = import.meta.env;

  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>Environment Variables Debug</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <h3>Specific Variables:</h3>
        <pre style={{ fontSize: '12px', background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
          {Object.entries(envVars).map(([key, value]) => 
            `${key}: ${value || 'undefined'}`
          ).join('\n')}
        </pre>
        
        <h3>All Environment Variables:</h3>
        <pre style={{ fontSize: '10px', background: '#f5f5f5', padding: '10px', overflow: 'auto', maxHeight: '200px' }}>
          {Object.entries(allEnvVars).map(([key, value]) => 
            `${key}: ${value}`
          ).join('\n')}
        </pre>
        
        <h3>Stripe Key Analysis:</h3>
        <p>
          <strong>Key found:</strong> {envVars.VITE_STRIPE_PUBLISHABLE_KEY ? 'Yes' : 'No'}<br/>
          <strong>Key starts with pk_test:</strong> {envVars.VITE_STRIPE_PUBLISHABLE_KEY?.startsWith('pk_test_') ? 'Yes' : 'No'}<br/>
          <strong>Key length:</strong> {envVars.VITE_STRIPE_PUBLISHABLE_KEY?.length || 0}<br/>
          <strong>Is placeholder:</strong> {envVars.VITE_STRIPE_PUBLISHABLE_KEY === 'pk_test_your_stripe_publishable_key_here' ? 'Yes' : 'No'}
        </p>
      </IonCardContent>
    </IonCard>
  );
};

export default EnvDebug;


