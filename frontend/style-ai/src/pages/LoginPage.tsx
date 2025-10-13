import React, { useState } from 'react';
import {
  IonPage,
  IonContent,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonText,
  IonToast,
  IonSpinner,
  IonGrid,
  IonRow,
  IonCol,
} from '@ionic/react';
import { useAuth } from '../contexts/AuthContext';
import { useHistory } from 'react-router-dom';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastColor, setToastColor] = useState<'success' | 'danger'>('danger');
  
  const { login } = useAuth();
  const history = useHistory();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      showToastMessage('Please fill in all fields', 'danger');
      return;
    }

    setIsLoading(true);
    try {
      const success = await login(username.trim(), password);
      
      if (success) {
        showToastMessage('Login successful!', 'success');
        setTimeout(() => {
          history.push('/camera');
        }, 1000);
      } else {
        showToastMessage('Invalid username or password', 'danger');
      }
    } catch (error) {
      showToastMessage('Login failed. Please try again.', 'danger');
    } finally {
      setIsLoading(false);
    }
  };

  const showToastMessage = (message: string, color: 'success' | 'danger') => {
    setToastMessage(message);
    setToastColor(color);
    setShowToast(true);
  };

  return (
    <IonPage>
      <IonHeader className="modern-header">
        <IonToolbar>
          <IonTitle>Style AI - Login</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent className="login-content">
        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <h1 className="login-title">Welcome to Style AI</h1>
              <p className="login-subtitle">
                Sign in to save and manage your enhancement prompts
              </p>
            </div>

            <div className="login-form">
              <form onSubmit={handleLogin}>
                <div className="form-field">
                  <label className="form-label">Username or Email</label>
                  <input
                    type="text"
                    className="form-input"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username or email"
                    required
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="login-button"
                >
                  {isLoading ? 'Signing In...' : 'Sign In'}
                </button>
              </form>

              <div className="login-footer">
                <p>Don't have an account?</p>
                <IonButton
                  fill="clear"
                  onClick={() => history.push('/register')}
                  className="register-link"
                >
                  Create Account
                </IonButton>
              </div>
            </div>
          </div>
        </div>

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

export default LoginPage;
