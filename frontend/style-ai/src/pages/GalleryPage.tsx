import React, { useEffect, useState, useCallback } from 'react';
import {
  IonContent,
  IonHeader,
  IonPage,
  IonTitle,
  IonToolbar,
  IonGrid,
  IonRow,
  IonCol,
  IonImg,
  IonText,
  IonToast,
  IonRefresher,
  IonRefresherContent,
  RefresherEventDetail,
  IonSpinner,
  IonSelect,
  IonSelectOption,
  IonLabel,
  IonItem,
  IonChip,
  IonModal,
  IonButton,
  IonIcon,
  IonButtons
} from '@ionic/react';
import { downloadOutline, closeOutline, shareOutline, personOutline, logOutOutline } from 'ionicons/icons';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useHistory } from 'react-router-dom';
import './GalleryPage.css';

import { API_URL } from '../config/environment';

interface Image {
  id: string;
  url: string;
  timestamp: string;
  style?: string;
}


const GalleryPage: React.FC = () => {
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<Image | null>(null);
  const [showModal, setShowModal] = useState(false);
  
  const { isAuthenticated, logout } = useAuth();
  const history = useHistory();

  const handleLogout = () => {
    logout();
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };

  const fetchImages = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/images`);
      
      if (response.data.images) {
        const processedImages = response.data.images.map((img: Image) => ({
          ...img,
          url: `${API_URL}${img.url}`,
          // Extract style from filename (e.g., "processed_sketch_123.jpg" -> "sketch")
          style: img.id.includes('_') ? img.id.split('_')[1] : 'unknown'
        }));
        setImages(processedImages);
      } else {
        setImages([]);
      }
    } catch (err) {
      console.error('Error fetching images:', err);
      setError('Failed to load images. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    if (isAuthenticated) {
      fetchImages();
    }
  }, [fetchImages, isAuthenticated]);

  // Set up periodic refresh
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const refreshInterval = setInterval(() => {
      if (!loading && !error) { // Only refresh if not loading and no error
        fetchImages();
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(refreshInterval);
  }, [fetchImages, loading, error, isAuthenticated]);

  const handleRefresh = async (event: CustomEvent<RefresherEventDetail>) => {
    setLoading(true);
    setError(null); // Clear any previous errors when manually refreshing
    await fetchImages();
    event.detail.complete();
  };

  const openModal = (image: Image) => {
    setSelectedImage(image);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedImage(null);
  };

  const handleDownload = async (image: Image, event?: React.MouseEvent) => {
    // Prevent modal from opening when download button is clicked
    if (event) {
      event.stopPropagation();
    }
    
    try {
      const response = await axios.get(image.url, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'image/jpeg' }); // Assuming JPEG for now
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `image_${image.id}.jpg`; // Default to JPEG
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setError('Image downloaded successfully!');
    } catch (err) {
      console.error('Error downloading image:', err);
      setError('Failed to download image.');
    }
  };

  const handleShare = async () => {
    if (!selectedImage) return;
    try {
      await navigator.share({
        title: `Image from ${new Date(selectedImage.timestamp).toLocaleString()}`,
        text: `Check out this cool image!`,
        url: selectedImage.url,
      });
      setError('Image shared successfully!');
    } catch (err) {
      console.error('Error sharing image:', err);
      setError('Failed to share image.');
    }
  };

  // All images are shown (no filtering needed)
  const filteredImages = images;

  // Early return for unauthenticated users
  if (!isAuthenticated) {
    return (
      <IonPage>
        <IonHeader className="modern-header">
          <IonToolbar>
            <IonTitle>Gallery</IonTitle>
            <IonButtons slot="end">
              <IonButton onClick={() => history.push('/login')}>
                <IonIcon icon={personOutline} />
              </IonButton>
            </IonButtons>
          </IonToolbar>
        </IonHeader>
        <IonContent className="saved-prompts-content">
          <div className="saved-prompts-container">
            <div className="saved-prompts-header">
              <h1 className="saved-prompts-title">My Gallery</h1>
              <p className="saved-prompts-subtitle">
                Sign in to view your enhanced images
              </p>
            </div>
            
            <div className="empty-state">
              <div className="empty-state-icon">🖼️</div>
              <h2 className="empty-state-title">Authentication Required</h2>
              <p className="empty-state-text">
                Please sign in to view your enhanced images. Create an account to start building your personal gallery of AI-enhanced photos.
              </p>
              <button 
                className="modern-button"
                onClick={() => history.push('/login')}
              >
                Sign In
              </button>
            </div>
          </div>
        </IonContent>
      </IonPage>
    );
  }

  return (
    <IonPage>
      <IonHeader className="modern-header">
        <IonToolbar>
          <IonTitle>Gallery</IonTitle>
          <IonButtons slot="end">
            {isAuthenticated ? (
              <>
                <IonButton onClick={() => history.push('/saved-prompts')}>
                  <IonIcon icon={personOutline} />
                </IonButton>
                <IonButton onClick={handleLogout}>
                  <IonIcon icon={logOutOutline} />
                </IonButton>
              </>
            ) : (
              <IonButton onClick={() => history.push('/login')}>
                <IonIcon icon={personOutline} />
              </IonButton>
            )}
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent className="gallery-content">
        <IonRefresher slot="fixed" onIonRefresh={handleRefresh}>
          <IonRefresherContent></IonRefresherContent>
        </IonRefresher>

        <div className="gallery-container">

          {loading ? (
            <div className="gallery-loading">
              <IonSpinner name="circular" />
              <p>Loading images...</p>
            </div>
          ) : filteredImages.length === 0 ? (
            <div className="gallery-empty">
              <div className="gallery-empty-icon">📷</div>
              <h2>No images found</h2>
              <p>Take a picture and upload it to see it here!</p>
            </div>
          ) : (
            <div className="gallery-grid">
              {filteredImages.map((image) => (
                <div 
                  key={image.id}
                  className="image-card"
                  onClick={() => openModal(image)}
                >
                  <div className="image-container">
                    <img
                      src={image.url}
                      alt={`Image from ${new Date(image.timestamp).toLocaleString()}`}
                      onError={(e) => {
                        console.error('Error loading image:', image.url);
                        setError(`Failed to load image: ${image.url}`);
                      }}
                    />
                  </div>
                  <div className="image-overlay">
                    <p className="image-date">
                      {new Date(image.timestamp).toLocaleDateString()}
                    </p>
                    <button 
                      className="download-btn"
                      onClick={(e) => handleDownload(image, e)}
                      title="Download image"
                    >
                      <IonIcon icon={downloadOutline} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <IonToast
          isOpen={!!error}
          onDidDismiss={() => setError(null)}
          message={error || ''}
          duration={2000}
          color="danger"
          position="top"
          cssClass="custom-toast"
          buttons={[
            {
              text: 'Dismiss',
              role: 'cancel'
            }
          ]}
        />

        <IonModal isOpen={showModal} onDidDismiss={closeModal}>
          {selectedImage && (
            <div className="modal-wrapper">
              <IonHeader>
                <IonToolbar>
                  <IonTitle>{`Image from ${new Date(selectedImage.timestamp).toLocaleString()}`}</IonTitle>
                  <IonButtons slot="end">
                    <IonButton onClick={closeModal}>
                      <IonIcon icon={closeOutline} />
                    </IonButton>
                  </IonButtons>
                </IonToolbar>
              </IonHeader>
              <div className="modal-content">
                <div className="modal-image-container">
                  <img 
                    src={selectedImage.url} 
                    alt={`Full size: ${selectedImage.id}`}
                    className="modal-image"
                  />
                </div>
                <div className="modal-actions">
                  <button className="modern-button" onClick={() => handleDownload(selectedImage)}>
                    <IonIcon icon={downloadOutline} /> Download
                  </button>
                  <button className="modern-button secondary" onClick={handleShare}>
                    <IonIcon icon={shareOutline} /> Share
                  </button>
                </div>
              </div>
            </div>
          )}
        </IonModal>
      </IonContent>
    </IonPage>
  );
};

export default GalleryPage; 