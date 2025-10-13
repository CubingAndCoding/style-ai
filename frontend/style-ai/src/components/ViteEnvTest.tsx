import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';

const ViteEnvTest: React.FC = () => {
  // Test different ways to access environment variables
  const envTest = {
    'import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY': import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY,
    'import.meta.env.VITE_API_URL': import.meta.env.VITE_API_URL,
    'process.env.VITE_STRIPE_PUBLISHABLE_KEY': process.env.VITE_STRIPE_PUBLISHABLE_KEY,
    'process.env.VITE_API_URL': process.env.VITE_API_URL,
  };

  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>Vite Environment Test</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <h3>Environment Variable Access Methods:</h3>
        <pre style={{ fontSize: '12px', background: '#f5f5f5', padding: '10px' }}>
          {Object.entries(envTest).map(([method, value]) => 
            `${method}: ${value || 'undefined'}`
          ).join('\n')}
        </pre>
        
        <h3>All import.meta.env:</h3>
        <pre style={{ fontSize: '10px', background: '#f5f5f5', padding: '10px', maxHeight: '150px', overflow: 'auto' }}>
          {JSON.stringify(import.meta.env, null, 2)}
        </pre>
        
        <h3>All process.env:</h3>
        <pre style={{ fontSize: '10px', background: '#f5f5f5', padding: '10px', maxHeight: '150px', overflow: 'auto' }}>
          {JSON.stringify(process.env, null, 2)}
        </pre>
      </IonCardContent>
    </IonCard>
  );
};

export default ViteEnvTest;


