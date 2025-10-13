import { Redirect, Route, useLocation } from 'react-router-dom';
import {
  IonApp,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
  IonTabBar,
  IonTabButton,
  IonTabs,
  IonSpinner,
  IonContent,
  setupIonicReact
} from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { camera, image } from 'ionicons/icons';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import CameraPage from './pages/CameraPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import GalleryPage from './pages/GalleryPage';
import PaymentPage from './pages/PaymentPage';
import StripePaymentPage from './pages/StripePaymentPage';
import ConfigTest from './components/ConfigTest';

/* Core CSS required for Ionic components to work properly */
import '@ionic/react/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';

/* Optional CSS utils that can be commented out */
import '@ionic/react/css/padding.css';
import '@ionic/react/css/float-elements.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/display.css';

/**
 * Ionic Dark Mode
 * -----------------------------------------------------
 * For more info, please see:
 * https://ionicframework.com/docs/theming/dark-mode
 */

/* import '@ionic/react/css/palettes/dark.always.css'; */
/* import '@ionic/react/css/palettes/dark.class.css'; */
import '@ionic/react/css/palettes/dark.system.css';

/* Theme variables */
import './theme/variables.css';
import './theme/design-system.css';
import './components/ModernNavigation.css';

setupIonicReact();

const AppContent: React.FC = () => {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <IonApp>
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
            <div style={{ color: '#666', fontSize: '16px' }}>Loading Style AI...</div>
          </div>
        </IonContent>
      </IonApp>
    );
  }

  return (
    <IonApp>
      <IonReactRouter>
        <AppWithTabs />
      </IonReactRouter>
    </IonApp>
  );
};

const AppWithTabs: React.FC = () => {
  const location = useLocation();
  
  // Hide tabs on payment pages
  const hideTabs = location.pathname === '/payment' || location.pathname === '/stripe-payment';


  return (
    <IonTabs>
      <IonRouterOutlet>
        <Route exact path="/camera">
          <CameraPage />
        </Route>
        <Route exact path="/gallery">
          <GalleryPage />
        </Route>
        <Route exact path="/login">
          <LoginPage />
        </Route>
        <Route exact path="/register">
          <RegisterPage />
        </Route>
        <Route exact path="/payment">
          <PaymentPage />
        </Route>
        <Route exact path="/stripe-payment">
          <StripePaymentPage />
        </Route>
        <Route exact path="/config-test">
          <ConfigTest />
        </Route>
        <Route exact path="/">
          <Redirect to="/camera" />
        </Route>
      </IonRouterOutlet>
      {!hideTabs && (
        <IonTabBar slot="bottom" className="modern-tab-bar">
          <IonTabButton tab="camera" href="/camera">
            <IonIcon icon={camera} />
            <IonLabel>Camera</IonLabel>
          </IonTabButton>
          <IonTabButton tab="gallery" href="/gallery">
            <IonIcon icon={image} />
            <IonLabel>Gallery</IonLabel>
          </IonTabButton>
        </IonTabBar>
      )}
    </IonTabs>
  );
};

const App: React.FC = () => (
  <AuthProvider>
    <AppContent />
  </AuthProvider>
);

export default App;
