import React, { useState, useEffect } from 'react';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonBackButton,
  IonTitle,
  IonContent,
  IonIcon,
  IonSpinner,
  IonToast,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButton
} from '@ionic/react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { arrowBackOutline, cardOutline, checkmarkCircleOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { STRIPE_CONFIG, buildApiUrl, API_CONFIG } from '../utils/apiConfig';
import './StripePaymentPage.css';

// Initialize Stripe with environment variable
const stripePromise = loadStripe(STRIPE_CONFIG.PUBLISHABLE_KEY);

const PaymentForm: React.FC<{
  onPaymentSuccess: (message: string) => void;
  onPaymentError: (message: string) => void;
}> = ({ onPaymentSuccess, onPaymentError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const history = useHistory();
  const { token, refreshUser } = useAuth();
  
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);

    try {
      // Create payment intent on backend
      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.CREATE_PAYMENT_INTENT), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: 500, // $5.00 in cents
          currency: 'usd',
          description: '25 Image Credits - Style AI'
        })
      });

      const { client_secret, error: backendError } = await response.json();

      if (backendError) {
        throw new Error(backendError);
      }

      // Confirm payment with Stripe
      const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: elements.getElement(CardElement)!,
          billing_details: {
            name: 'Style AI User',
          },
        }
      });

      if (error) {
        onPaymentError(`Payment failed: ${error.message}`);
      } else if (paymentIntent.status === 'succeeded') {
        // Confirm payment on backend
        const confirmResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.CONFIRM_PAYMENT), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            payment_intent_id: paymentIntent.id,
            amount: paymentIntent.amount
          })
        });

        if (confirmResponse.ok) {
          onPaymentSuccess('Payment successful! You now have 25 image credits.');
          
          // Refresh user data to get updated credit count
          await refreshUser();
          
          // Redirect to camera page after successful payment
          setTimeout(() => {
            history.push('/camera');
          }, 2000);
        } else {
          throw new Error('Failed to confirm payment');
        }
      }
    } catch (error: any) {
      console.error('Payment error:', error);
      onPaymentError(`Payment failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <IonCard className="payment-card">
        <IonCardHeader>
          <IonCardTitle className="payment-title">
            <IonIcon icon={cardOutline} />
            Complete Your Payment
          </IonCardTitle>
        </IonCardHeader>
        <IonCardContent>
          <div className="payment-summary">
            <div className="summary-item">
              <span className="summary-label">25 Image Credits</span>
              <span className="summary-price">$5.00</span>
            </div>
            <div className="summary-item total">
              <span className="summary-label">Total</span>
              <span className="summary-price">$5.00</span>
            </div>
          </div>

          <div className="card-element-container">
            <label className="card-label">Card Details</label>
            <CardElement
              options={{
                style: {
                  base: {
                    fontSize: '16px',
                    color: 'white',
                    fontFamily: 'Arial, sans-serif',
                    '::placeholder': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  },
                  invalid: {
                    color: '#ff6b6b',
                  },
                },
              }}
            />
          </div>

          <IonButton
            expand="block"
            type="submit"
            disabled={!stripe || loading}
            className="payment-submit-button"
          >
            {loading ? (
              <>
                <IonSpinner name="crescent" />
                Processing...
              </>
            ) : (
              <>
                <IonIcon icon={checkmarkCircleOutline} />
                Pay $5.00
              </>
            )}
          </IonButton>

          <div className="payment-security">
            <IonIcon icon={checkmarkCircleOutline} />
            <span>Secured by Stripe • Your card details are never stored</span>
          </div>
        </IonCardContent>
      </IonCard>
    </form>
  );
};

const StripePaymentPage: React.FC = () => {
  const history = useHistory();
  const { isAuthenticated } = useAuth();
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastColor, setToastColor] = useState<'success' | 'danger'>('success');

  useEffect(() => {
    if (!isAuthenticated) {
      history.push('/login');
    }
  }, [isAuthenticated, history]);

  const handlePaymentSuccess = (message: string) => {
    setToastMessage(message);
    setToastColor('success');
    setShowToast(true);
  };

  const handlePaymentError = (message: string) => {
    setToastMessage(message);
    setToastColor('danger');
    setShowToast(true);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <IonPage className="stripe-payment-page">
      <IonHeader className="modern-header">
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/payment" icon={arrowBackOutline} />
          </IonButtons>
          <IonTitle>Secure Payment</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent className="stripe-payment-content">
        <div className="stripe-payment-container">
          <div className="payment-header">
            <h1>Complete Your Purchase</h1>
            <p>Get 25 professional image credits for just $5</p>
          </div>

          <Elements stripe={stripePromise}>
            <PaymentForm 
              onPaymentSuccess={handlePaymentSuccess}
              onPaymentError={handlePaymentError}
            />
          </Elements>

          <div className="payment-features">
            <h3>What you get:</h3>
            <ul>
              <li>25 high-quality AI-enhanced images</li>
              <li>Latest Gemini 2.0 AI model</li>
              <li>Professional cinematic lighting</li>
              <li>Credits never expire</li>
            </ul>
          </div>
        </div>
      </IonContent>

      <IonToast
        isOpen={showToast}
        onDidDismiss={() => setShowToast(false)}
        message={toastMessage}
        duration={3000}
        color={toastColor}
        position="top"
      />
    </IonPage>
  );
};

export default StripePaymentPage;