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

const ApiMethodTestPage: React.FC = () => {
  const [testResults, setTestResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [testUsername, setTestUsername] = useState('methodtest' + Date.now());
  const [testEmail, setTestEmail] = useState('method' + Date.now() + '@example.com');
  const [testPassword, setTestPassword] = useState('testpass123');

  const addTestResult = (test: string, success: boolean, details: any) => {
    setTestResults(prev => [...prev, {
      test,
      success,
      details,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const testGetRequest = async () => {
    setIsLoading(true);
    addTestResult('GET Request Test', true, `Testing GET request to: ${API_URL}/auth/register`);
    
    try {
      const response = await axios.get(`${API_URL}/auth/register`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      addTestResult('GET Request Test', true, {
        status: response.status,
        data: response.data
      });
    } catch (error: any) {
      addTestResult('GET Request Test', false, {
        error: error.message,
        status: error.response?.status,
        data: error.response?.data,
        method: 'GET'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const testPostRequest = async () => {
    setIsLoading(true);
    addTestResult('POST Request Test', true, `Testing POST request to: ${API_URL}/auth/register`);
    
    const data = {
      username: testUsername,
      email: testEmail,
      password: testPassword
    };
    
    try {
      const response = await axios.post(`${API_URL}/auth/register`, data, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      addTestResult('POST Request Test', true, {
        status: response.status,
        data: response.data
      });
    } catch (error: any) {
      addTestResult('POST Request Test', false, {
        error: error.message,
        status: error.response?.status,
        data: error.response?.data,
        method: 'POST'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const testAxiosConfig = () => {
    const config = {
      API_URL: API_URL,
      axios_defaults: axios.defaults,
      axios_interceptors: axios.interceptors
    };
    
    addTestResult('Axios Configuration', true, config);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>API Method Test</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent>
        <IonCard>
          <IonCardHeader>
            <IonCardTitle>HTTP Method Testing</IonCardTitle>
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
            <IonCardTitle>Test Actions</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <IonGrid>
              <IonRow>
                <IonCol size="6">
                  <IonButton 
                    expand="block" 
                    onClick={testAxiosConfig}
                    disabled={isLoading}
                    color="medium"
                  >
                    Test Axios Config
                  </IonButton>
                </IonCol>
                <IonCol size="6">
                  <IonButton 
                    expand="block" 
                    onClick={testGetRequest}
                    disabled={isLoading}
                    color="warning"
                  >
                    Test GET (Should Fail)
                  </IonButton>
                </IonCol>
                <IonCol size="12">
                  <IonButton 
                    expand="block" 
                    onClick={testPostRequest}
                    disabled={isLoading}
                    color="primary"
                  >
                    {isLoading ? <IonSpinner /> : 'Test POST (Should Work)'}
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

export default ApiMethodTestPage;
