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
  IonButton,
  IonText,
  IonToast,
  IonSpinner,
  IonGrid,
  IonRow,
  IonCol,
  IonInput,
} from '@ionic/react';
import axios from 'axios';
import { API_URL } from '../config/environment';

const ApiDebugPage: React.FC = () => {
  const [testResults, setTestResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [testUsername, setTestUsername] = useState('debuguser' + Date.now());
  const [testEmail, setTestEmail] = useState('debug' + Date.now() + '@example.com');
  const [testPassword, setTestPassword] = useState('testpass123');

  const addTestResult = (test: string, success: boolean, details: any) => {
    setTestResults(prev => [...prev, {
      test,
      success,
      details,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const testApiConnectivity = async () => {
    setIsLoading(true);
    setTestResults([]);
    
    try {
      // Test 1: Basic connectivity
      addTestResult('API Connectivity', true, `Testing connection to: ${API_URL}`);
      
      // Test 2: Registration endpoint
      try {
        const registerResponse = await axios.post(`${API_URL}/auth/register`, {
          username: testUsername,
          email: testEmail,
          password: testPassword
        }, {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        addTestResult('Registration Test', true, {
          status: registerResponse.status,
          data: registerResponse.data
        });
        
        // If registration succeeded, test login
        try {
          const loginResponse = await axios.post(`${API_URL}/auth/login`, {
            username: testUsername,
            password: testPassword
          }, {
            timeout: 10000,
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          addTestResult('Login Test', true, {
            status: loginResponse.status,
            data: loginResponse.data
          });
        } catch (loginError: any) {
          addTestResult('Login Test', false, {
            error: loginError.message,
            status: loginError.response?.status,
            data: loginError.response?.data
          });
        }
        
      } catch (registerError: any) {
        addTestResult('Registration Test', false, {
          error: registerError.message,
          status: registerError.response?.status,
          data: registerError.response?.data,
          headers: registerError.response?.headers
        });
      }
      
    } catch (error: any) {
      addTestResult('API Connectivity', false, {
        error: error.message,
        code: error.code
      });
    } finally {
      setIsLoading(false);
    }
  };

  const testEnvironmentConfig = () => {
    const envInfo = {
      API_URL: API_URL,
      NODE_ENV: process.env.NODE_ENV,
      DEV: import.meta.env.DEV,
      PROD: import.meta.env.PROD,
      allEnvVars: import.meta.env
    };
    
    addTestResult('Environment Config', true, envInfo);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>API Debug Tool</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent>
        <IonCard>
          <IonCardHeader>
            <IonCardTitle>Debug Configuration</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <IonGrid>
              <IonRow>
                <IonCol size="12">
                  <IonItem>
                    <IonLabel position="stacked">Test Username</IonLabel>
                    <IonInput
                      value={testUsername}
                      onIonInput={(e) => setTestUsername(e.detail.value!)}
                    />
                  </IonItem>
                </IonCol>
                <IonCol size="12">
                  <IonItem>
                    <IonLabel position="stacked">Test Email</IonLabel>
                    <IonInput
                      value={testEmail}
                      onIonInput={(e) => setTestEmail(e.detail.value!)}
                    />
                  </IonItem>
                </IonCol>
                <IonCol size="12">
                  <IonItem>
                    <IonLabel position="stacked">Test Password</IonLabel>
                    <IonInput
                      type="password"
                      value={testPassword}
                      onIonInput={(e) => setTestPassword(e.detail.value!)}
                    />
                  </IonItem>
                </IonCol>
              </IonRow>
            </IonGrid>
          </IonCardContent>
        </IonCard>

        <IonCard>
          <IonCardHeader>
            <IonCardTitle>Debug Actions</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <IonGrid>
              <IonRow>
                <IonCol size="6">
                  <IonButton 
                    expand="block" 
                    onClick={testEnvironmentConfig}
                    disabled={isLoading}
                  >
                    Test Environment
                  </IonButton>
                </IonCol>
                <IonCol size="6">
                  <IonButton 
                    expand="block" 
                    onClick={testApiConnectivity}
                    disabled={isLoading}
                    color="primary"
                  >
                    {isLoading ? <IonSpinner /> : 'Test API'}
                  </IonButton>
                </IonCol>
                <IonCol size="12">
                  <IonButton 
                    expand="block" 
                    fill="outline" 
                    onClick={clearResults}
                    disabled={isLoading}
                  >
                    Clear Results
                  </IonButton>
                </IonCol>
              </IonRow>
            </IonGrid>
          </IonCardContent>
        </IonCard>

        {testResults.length > 0 && (
          <IonCard>
            <IonCardHeader>
              <IonCardTitle>Test Results</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              {testResults.map((result, index) => (
                <IonItem key={index}>
                  <IonLabel>
                    <h2>
                      <IonText color={result.success ? 'success' : 'danger'}>
                        {result.success ? '✅' : '❌'} {result.test}
                      </IonText>
                    </h2>
                    <p>{result.timestamp}</p>
                    <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(result.details, null, 2)}
                    </pre>
                  </IonLabel>
                </IonItem>
              ))}
            </IonCardContent>
          </IonCard>
        )}

        <IonToast
          isOpen={showToast}
          onDidDismiss={() => setShowToast(false)}
          message={toastMessage}
          duration={3000}
          position="top"
        />
      </IonContent>
    </IonPage>
  );
};

export default ApiDebugPage;

