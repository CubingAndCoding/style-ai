import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';

const SimpleEnvTest: React.FC = () => {
  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>Simple Environment Test</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <h3>Direct Tests:</h3>
        <p><strong>VITE_STRIPE_PUBLISHABLE_KEY:</strong> {import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'undefined'}</p>
        <p><strong>VITE_API_URL:</strong> {import.meta.env.VITE_API_URL || 'undefined'}</p>
        
        <h3>All import.meta.env:</h3>
        <pre style={{ fontSize: '10px', background: '#f5f5f5', padding: '10px', maxHeight: '200px', overflow: 'auto' }}>
          {JSON.stringify(import.meta.env, null, 2)}
        </pre>
        
        <h3>Test with console.log:</h3>
        <p>Check browser console for environment variables</p>
        <button onClick={() => {
          console.log('=== ENVIRONMENT VARIABLES TEST ===');
          console.log('import.meta.env:', import.meta.env);
          console.log('VITE_STRIPE_PUBLISHABLE_KEY:', import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);
          console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
          console.log('All keys:', Object.keys(import.meta.env));
        }}>
          Log to Console
        </button>
      </IonCardContent>
    </IonCard>
  );
};

export default SimpleEnvTest;


