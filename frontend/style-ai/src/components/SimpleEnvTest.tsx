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
        
      </IonCardContent>
    </IonCard>
  );
};

export default SimpleEnvTest;


