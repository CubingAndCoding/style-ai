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
  logOutOutline,
  warningOutline,
  logInOutline,
  personAddOutline
} from 'ionicons/icons';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Filesystem, Directory } from '@capacitor/filesystem';
import { Share } from '@capacitor/share';
import { Capacitor } from '@capacitor/core';
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
      // Check if camera is available
      const hasPermission = await Camera.checkPermissions();
      if (hasPermission.camera === 'denied' || hasPermission.camera === 'prompt') {
        const requestResult = await Camera.requestPermissions();
        if (requestResult.camera !== 'granted') {
          showToastMessage('Camera permission is required to take photos', 'danger');
          return;
        }
      }

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
    } catch (error: any) {
      // Don't show error if user cancelled
      if (error?.message?.includes('cancel') || error?.message?.includes('Cancel')) {
        return;
      }
      console.error('Error taking picture:', error);
      const errorMessage = error?.message || 'Unknown error';
      showToastMessage(`Failed to take picture: ${errorMessage}`, 'danger');
    }
  };

  const selectFromGallery = async () => {
    try {
      // Check if photo library permission is available
      const hasPermission = await Camera.checkPermissions();
      if (hasPermission.photos === 'denied' || hasPermission.photos === 'prompt') {
        const requestResult = await Camera.requestPermissions();
        if (requestResult.photos !== 'granted') {
          showToastMessage('Photo library permission is required to select images', 'danger');
          return;
        }
      }

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
    } catch (error: any) {
      // Don't show error if user cancelled
      if (error?.message?.includes('cancel') || error?.message?.includes('Cancel') || error?.code === 'USER_CANCELED') {
        return;
      }
      console.error('Error selecting from gallery:', error);
      const errorMessage = error?.message || error?.toString() || 'Unknown error';
      console.error('Full error details:', error);
      showToastMessage(`Failed to select image: ${errorMessage}`, 'danger');
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
      const response = await fetch(`${API_URL}/auth/usage-info`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsageInfo(data);
      } else {
        const errorData = await response.json();
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

  const saveImageToDevice = async () => {
    if (!processedImage) {
      showToastMessage('No processed image to save', 'danger');
      return;
    }

    try {
      // Check if we're on a native platform (Android/iOS)
      const isNative = Capacitor.isNativePlatform();
      
      if (isNative) {
        // Fetch the image
        const response = await axios.get(processedImage, { responseType: 'blob' });
        const blob = await response.data;
        
        // Convert blob to base64
        const reader = new FileReader();
        const base64Data = await new Promise<string>((resolve, reject) => {
          reader.onloadend = () => {
            const base64String = reader.result as string;
            // Remove data URL prefix if present
            const base64 = base64String.includes(',') 
              ? base64String.split(',')[1] 
              : base64String;
            resolve(base64);
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });

        // Generate filename
        const filename = `StyleAI_${Date.now()}.jpg`;
        
        try {
          // Try to save to Pictures directory (Android) or Photos (iOS)
          // This should work with the permissions we've added
          await Filesystem.writeFile({
            path: filename,
            data: base64Data,
            directory: Directory.Pictures,
          });
          
          showToastMessage('Image saved to your gallery!', 'success');
        } catch (filesystemError: any) {
          // If saving to Pictures fails, try using Share API as fallback
          console.log('Direct save failed, using Share API:', filesystemError);
          
          // Save to cache first
          const cacheFile = await Filesystem.writeFile({
            path: filename,
            data: base64Data,
            directory: Directory.Cache,
          });
          
          // Share the file - user can choose to save to gallery
          await Share.share({
            title: 'Save Enhanced Image',
            text: 'Save this enhanced image to your gallery',
            url: cacheFile.uri,
            dialogTitle: 'Save to Gallery',
          });
          
          showToastMessage('Use the share menu to save to gallery', 'success');
        }
      } else {
        // For web platforms, use the download approach
        const response = await axios.get(processedImage, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: 'image/jpeg' });
        const url = window.URL.createObjectURL(blob);
        
        // Create a download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `enhanced-image-${Date.now()}.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToastMessage('Image saved to your device!', 'success');
      }
    } catch (error: any) {
      console.error('Error saving image:', error);
      const errorMessage = error?.message || 'Failed to save image';
      if (errorMessage.includes('permission') || errorMessage.includes('Permission')) {
        showToastMessage('Permission denied. Please grant storage permission in app settings.', 'danger');
      } else {
        showToastMessage('Failed to save image. Please try again.', 'danger');
      }
    }
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
          <IonButtons slot="start">
            {/* Empty start slot to prevent title from centering on iOS */}
          </IonButtons>
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
              {!processedImage ? (
                <button
                  className="modern-button action-button"
                  onClick={uploadImage}
                  disabled={loading}
                >
                  <IonIcon icon={sparklesOutline} />
                  {loading ? 'Enhancing...' : 'Enhance Image'}
                </button>
              ) : (
                <button
                  className="modern-button action-button"
                  onClick={saveImageToDevice}
                >
                  <IonIcon icon={saveOutline} />
                  Save to Device
                </button>
              )}
              
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