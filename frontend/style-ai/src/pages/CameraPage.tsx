import React, { useState, useCallback, useEffect } from 'react';
import { API_URL } from '../config/environment';
import {
  IonPage,
  IonContent,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonGrid,
  IonRow,
  IonCol,
  IonImg,
  IonText,
  IonToast,
  IonSelect,
  IonSelectOption,
  IonLabel,
  IonItem,
  IonIcon,
  IonButton,
  IonTextarea,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonInput,
  IonModal,
  IonButtons,
  IonSpinner,
} from '@ionic/react';
import { 
  imageOutline, 
  cameraOutline, 
  sparklesOutline, 
  saveOutline,
  personOutline,
  logOutOutline,
  warningOutline,
  logInOutline,
  personAddOutline
} from 'ionicons/icons';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { useAuth } from '../contexts/AuthContext';
import { useHistory, useLocation } from 'react-router-dom';
import axios from 'axios';
import './CameraPage.css';

const CameraPage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastColor, setToastColor] = useState<'success' | 'danger'>('success');
  
  
  
  const [usageInfo, setUsageInfo] = useState<any>(null);
  const [usageLoading, setUsageLoading] = useState(false);
  const [usageError, setUsageError] = useState<string | null>(null);
  
  const { isAuthenticated, user, logout, token, isPremium } = useAuth();
  const history = useHistory();
  const location = useLocation();



  useEffect(() => {
    if (isAuthenticated && token) {
      // Fetch usage info for authenticated users
      fetchUsageInfo();
    }
  }, [isAuthenticated, token, user]); // Added user to dependencies


  const takePicture = async () => {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Camera,
      });

      if (image.base64String) {
        setSelectedImage(`data:image/jpeg;base64,${image.base64String}`);
        setProcessedImage(null);
      }
    } catch (error) {
      console.error('Error taking picture:', error);
      showToastMessage('Failed to take picture', 'danger');
    }
  };

  const selectFromGallery = async () => {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Photos,
      });

      if (image.base64String) {
        setSelectedImage(`data:image/jpeg;base64,${image.base64String}`);
        setProcessedImage(null);
      }
    } catch (error) {
      console.error('Error selecting from gallery:', error);
      showToastMessage('Failed to select image from gallery', 'danger');
    }
  };

  const uploadImage = async () => {
    if (!selectedImage) {
      showToastMessage('Please select an image first', 'danger');
      return;
    }

    setLoading(true);
    try {
      const payload: any = {
        image: selectedImage,
      };

      const response = await axios.post(`${API_URL}/upload`, payload);
      
      if (response.data.url) {
        const processedImageUrl = `${API_URL}${response.data.url}`;
        setProcessedImage(processedImageUrl);
        showToastMessage('Image enhanced successfully!', 'success');
        
        // Refresh usage info after successful upload
        fetchUsageInfo();
        
        console.log('Image processed successfully');
      }
    } catch (error: any) {
      console.error('Error uploading image:', error);
      
      // Handle premium restriction error
      if (error.response?.status === 403 && error.response?.data?.premium_required) {
        showToastMessage('Custom prompts are a premium feature. Please upgrade to use custom enhancement prompts.', 'danger');
      } else {
        showToastMessage('Failed to enhance image', 'danger');
      }
    } finally {
      setLoading(false);
    }
  };

  const showToastMessage = (message: string, color: 'success' | 'danger') => {
    setToastMessage(message);
    setToastColor(color);
    setShowToast(true);
  };

  const fetchUsageInfo = async () => {
    setUsageLoading(true);
    setUsageError(null);
    try {
      console.log('Fetching usage info...');
      const response = await fetch(`${API_URL}/auth/usage-info`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Usage info response:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Usage info data:', data);
        setUsageInfo(data);
      } else {
        console.error('Failed to fetch usage info:', response.status);
        const errorData = await response.json();
        console.error('Error details:', errorData);
        setUsageError('Failed to load usage info');
      }
    } catch (error) {
      console.error('Error fetching usage info:', error);
      setUsageError('Network error loading usage info');
    } finally {
      setUsageLoading(false);
    }
  };




  const clearImage = () => {
    setSelectedImage(null);
    setProcessedImage(null);
  };


  const handleLogout = () => {
    logout();
    showToastMessage('Logged out successfully', 'success');
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };

  return (
    <IonPage>
      <IonHeader className="modern-header">
        <IonToolbar>
          <IonTitle>
            Style AI
          </IonTitle>
          <IonButtons slot="end">
            {isAuthenticated ? (
              <>
                {/* Credits & Purchase Button */}
                <div className="credits-purchase-container">
                  {usageLoading ? (
                    <div className="credits-loading">
                      <IonSpinner name="crescent" />
                    </div>
                  ) : usageError ? (
                    <button className="credits-error-btn" onClick={fetchUsageInfo}>
                      Retry
                    </button>
                  ) : usageInfo ? (
                    <button 
                      className={`credits-purchase-btn ${usageInfo.image_credits <= 2 ? 'low-credits' : ''}`}
                      onClick={() => history.push('/payment')}
                      title="Purchase more image credits"
                    >
                      <IonIcon icon={sparklesOutline} />
                      <div className="credits-info">
                        <span className="credits-count">{usageInfo.image_credits || usageInfo.remaining}</span>
                        <span className="credits-label">left</span>
                      </div>
                      <span className="buy-text">Buy More</span>
                    </button>
                  ) : null}
                </div>
                
                <IonButton onClick={() => history.push('/saved-prompts')}>
                  <IonIcon icon={personOutline} />
                </IonButton>
                <IonButton onClick={handleLogout}>
                  <IonIcon icon={logOutOutline} />
                </IonButton>
              </>
            ) : (
              <>
                <IonButton onClick={() => history.push('/login')}>
                  <IonIcon icon={logInOutline} />
                </IonButton>
                <IonButton onClick={() => history.push('/register')}>
                  <IonIcon icon={personAddOutline} />
                </IonButton>
              </>
            )}
          </IonButtons>
        </IonToolbar>
      </IonHeader>

      <IonContent className="camera-content">
        <div className="camera-container">
          {/* Header */}
          <div className="camera-header">
            <h1 className="camera-title">AI Photo Enhancement</h1>
            <p className="camera-subtitle">
              Transform your photos with AI-powered style enhancement
            </p>
          </div>

          {/* Upload Section */}
          <div className="upload-section">
            <div className="upload-card">
              <div className="upload-area" onClick={selectFromGallery}>
                <div className="upload-icon">📷</div>
                <div className="upload-text">Upload or Take a Photo</div>
                <div className="upload-hint">Click to select from gallery or use camera</div>
              </div>
            </div>
          </div>

          {/* Image Display */}
          {selectedImage && (
            <div className="image-section">
              <div className="image-grid">
                <div className="image-container">
                  <label className="image-label">Original Image</label>
                  <img 
                    src={selectedImage} 
                    alt="Selected" 
                    className="image-preview"
                  />
                </div>
                
                <div className="image-container place-holder-card">
                  <label className="image-label">Enhanced Image</label>
                  {processedImage ? (
                    <img 
                      src={processedImage} 
                      alt="Enhanced" 
                      className="image-preview"
                    />
                  ) : (
                    <div className="image-placeholder">
                      {loading ? 'Processing...' : 'Enhanced image will appear here'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}




          {/* Action Buttons */}
          {selectedImage && (
            <div className="actions-section">
              <button
                className="modern-button action-button"
                onClick={uploadImage}
                disabled={loading}
              >
                <IonIcon icon={sparklesOutline} />
                {loading ? 'Enhancing...' : 'Enhance Image'}
              </button>
              
              <button
                className="modern-button action-button secondary"
                onClick={clearImage}
              >
                Clear Image
              </button>
            </div>
          )}
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

export default CameraPage; 