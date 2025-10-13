import React, { useEffect, useState } from 'react';
import { STRIPE_PUBLISHABLE_KEY, API_URL } from '../config/environment';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonButton } from '@ionic/react';
import { loadStripe } from '@stripe/stripe-js';

const StripeKeyTest: React.FC = () => {
  const [stripeLoaded, setStripeLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string[]>([]);

  const addDebugInfo = (info: string) => {
    setDebugInfo(prev => [...prev, `${new Date().toLocaleTimeString()}: ${info}`]);
  };

  useEffect(() => {
    addDebugInfo('Starting Stripe key test...');
    
    const publishableKey = STRIPE_PUBLISHABLE_KEY;
    addDebugInfo(`Raw env var: ${publishableKey}`);
    addDebugInfo(`Is undefined: ${publishableKey === undefined}`);
    addDebugInfo(`Is placeholder: ${publishableKey === 'pk_test_your_stripe_publishable_key_here'}`);
    addDebugInfo(`Starts with pk_test: ${publishableKey?.startsWith('pk_test_')}`);
    
    if (!publishableKey || publishableKey === 'pk_test_your_stripe_publishable_key_here') {
      setError('❌ Invalid or missing Stripe publishable key');
      addDebugInfo('❌ Error: Invalid key');
      return;
    }

    addDebugInfo('✅ Key looks valid, testing Stripe load...');
    
    loadStripe(publishableKey)
      .then(stripe => {
        if (stripe) {
          addDebugInfo('✅ Stripe loaded successfully!');
          setStripeLoaded(true);
        } else {
          addDebugInfo('❌ Stripe failed to load');
          setError('Failed to load Stripe');
        }
      })
      .catch(err => {
        addDebugInfo(`❌ Stripe load error: ${err.message}`);
        setError(`Stripe load error: ${err.message}`);
      });
  }, []);

  const testPaymentIntent = async () => {
    addDebugInfo('Testing payment intent creation...');
    
    try {
      const response = await fetch(`${API_URL}/auth/create-payment-intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token' // This will fail auth but we can see the error
        },
        body: JSON.stringify({
          amount: 500,
          currency: 'usd',
          description: 'Test payment intent'
        })
      });
      
      const data = await response.json();
      addDebugInfo(`Response: ${JSON.stringify(data)}`);
    } catch (err: any) {
      addDebugInfo(`❌ Request error: ${err.message}`);
    }
  };

  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>Stripe Key Test</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <p><strong>Publishable Key:</strong> {import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'undefined'}</p>
        <p><strong>Status:</strong> {stripeLoaded ? '✅ Loaded' : error || 'Loading...'}</p>
        
        <IonButton onClick={testPaymentIntent} fill="outline">
          Test Backend Connection
        </IonButton>
        
        <h3>Debug Log:</h3>
        <pre style={{ fontSize: '12px', background: '#f5f5f5', padding: '10px', maxHeight: '200px', overflow: 'auto' }}>
          {debugInfo.join('\n')}
        </pre>
      </IonCardContent>
    </IonCard>
  );
};

export default StripeKeyTest;
