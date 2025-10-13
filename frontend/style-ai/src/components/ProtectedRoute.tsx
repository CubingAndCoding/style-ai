import React from 'react';
import { Redirect } from 'react-router-dom';
import { IonSpinner, IonContent } from '@ionic/react';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <IonContent className="app-loading">
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100vh',
          gap: '20px'
        }}>
          <IonSpinner name="crescent" style={{ width: '60px', height: '60px' }} />
          <div style={{ color: '#666', fontSize: '16px' }}>Checking authentication...</div>
        </div>
      </IonContent>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }

  // Render protected content if authenticated
  return <>{children}</>;
};

export default ProtectedRoute;
