import React, { useState, useEffect } from 'react';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonIcon,
  IonToast,
  IonSpinner,
} from '@ionic/react';
import { sparklesOutline, arrowBackOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './PaymentPage.css';

const PaymentPage: React.FC = () => {
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastColor, setToastColor] = useState<'success' | 'danger'>('success');
  
  const { isAuthenticated, token } = useAuth();
  const history = useHistory();

  const showToastMessage = (message: string, color: 'success' | 'danger') => {
    setToastMessage(message);
    setToastColor(color);
    setShowToast(true);
  };

  const handlePayment = () => {
    // Redirect to Stripe payment page
    history.push('/stripe-payment');
  };

  const handleBack = () => {
    history.goBack();
  };

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      history.push('/login');
    }
  }, [isAuthenticated, history]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <IonPage>
      <IonHeader className="modern-header">
        <IonToolbar>
          <IonButton fill="clear" slot="start" onClick={handleBack}>
            <IonIcon icon={arrowBackOutline} />
          </IonButton>
          <IonTitle>Purchase Credits</IonTitle>
        </IonToolbar>
      </IonHeader>
      
      <IonContent className="payment-page-content">
        <div className="payment-page-container">
          <div className="payment-hero">
            <div className="hero-icon">
              <IonIcon icon={sparklesOutline} />
            </div>
            <h1>📸 Professional Photographer in Your Pocket</h1>
            <p className="hero-subtitle">
              Transform your photos into professional masterpieces with AI-powered enhancement
            </p>
          </div>

          <div className="pricing-section">
            <div className="pricing-card">
              <div className="price-display">
                <span className="currency">$</span>
                <span className="amount">5</span>
                <span className="period">for 25 images</span>
              </div>
              <p className="price-description">
                That's just <strong>20¢ per professional photo!</strong><br/>
                <span className="price-note">Free app • Pay only when you use</span>
              </p>
            </div>

            <div className="features-section">
              <h3>What you get:</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <div className="feature-icon">✓</div>
                  <div className="feature-content">
                    <h4>25 High-Quality Images</h4>
                    <p>Professional-grade enhancement for each photo</p>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">✓</div>
                  <div className="feature-content">
                    <h4>Cinematic Lighting</h4>
                    <p>Dramatic shadows and highlights for professional look</p>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">✓</div>
                  <div className="feature-content">
                    <h4>Advanced Color Grading</h4>
                    <p>Perfect color balance and mood enhancement</p>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">✓</div>
                  <div className="feature-content">
                    <h4>Credits Never Expire</h4>
                    <p>Use your credits whenever you want, no rush</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="payment-section">
              <button
                className="purchase-button"
                onClick={handlePayment}
                disabled={paymentLoading}
              >
                {paymentLoading ? (
                  <>
                    <IonSpinner name="crescent" />
                    Processing...
                  </>
                ) : (
                  <>
                    <IonIcon icon={sparklesOutline} />
                    Purchase Credits - $5
                  </>
                )}
              </button>
              
              <p className="payment-note">
                Free app • Pay only when you use • Credits never expire
              </p>
            </div>
          </div>
        </div>

        {/* Toast for notifications */}
        <IonToast
          isOpen={showToast}
          onDidDismiss={() => setShowToast(false)}
          message={toastMessage}
          duration={3000}
          color={toastColor}
          position="top"
        />
      </IonContent>
    </IonPage>
  );
};

export default PaymentPage;
