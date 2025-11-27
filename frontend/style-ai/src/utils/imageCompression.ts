/**
 * Image compression utility to reduce upload size and server memory usage
 */

interface CompressionOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  maxSizeKB?: number;
}

/**
 * Compresses an image by resizing and reducing quality
 * @param base64Image - Base64 encoded image string (with or without data URL prefix)
 * @param options - Compression options
 * @returns Compressed base64 image string
 */
export const compressImage = async (
  base64Image: string,
  options: CompressionOptions = {}
): Promise<string> => {
  const {
    maxWidth = 1920, // Max width for images (reduces memory usage)
    maxHeight = 1920, // Max height for images
    quality = 0.75, // JPEG quality (0.75 = 75%, good balance)
    maxSizeKB = 500, // Target max size in KB
  } = options;

  return new Promise((resolve, reject) => {
    try {
      // Remove data URL prefix if present
      const base64Data = base64Image.includes(',') 
        ? base64Image.split(',')[1] 
        : base64Image;

      // Create image element
      const img = new Image();
      
      img.onload = () => {
        try {
          // Calculate new dimensions while maintaining aspect ratio
          let width = img.width;
          let height = img.height;

          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width = Math.floor(width * ratio);
            height = Math.floor(height * ratio);
          }

          // Create canvas
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;

          // Draw and compress
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            reject(new Error('Could not get canvas context'));
            return;
          }

          ctx.drawImage(img, 0, 0, width, height);

          // Convert to base64 with compression
          let compressedBase64 = canvas.toDataURL('image/jpeg', quality);

          // If still too large, reduce quality further
          let currentQuality = quality;
          let iterations = 0;
          const maxIterations = 5;

          while (iterations < maxIterations) {
            const sizeKB = (compressedBase64.length * 3) / 4 / 1024;
            
            if (sizeKB <= maxSizeKB || currentQuality <= 0.5) {
              break;
            }

            // Reduce quality and try again
            currentQuality = Math.max(0.5, currentQuality - 0.1);
            compressedBase64 = canvas.toDataURL('image/jpeg', currentQuality);
            iterations++;
          }

          resolve(compressedBase64);
        } catch (error) {
          reject(error);
        }
      };

      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };

      // Load the image
      img.src = `data:image/jpeg;base64,${base64Data}`;
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Gets the approximate size of a base64 image in KB
 */
export const getImageSizeKB = (base64Image: string): number => {
  const base64Data = base64Image.includes(',') 
    ? base64Image.split(',')[1] 
    : base64Image;
  return (base64Data.length * 3) / 4 / 1024;
};

