from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
from PIL import Image
import io
import os
import uuid
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Created uploads directory at {UPLOAD_FOLDER}")

def save_image(image_data):
    # Generate unique filename
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Convert base64 to image and save
    image_bytes = base64.b64decode(image_data.split(',')[1])
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    logger.info(f"Saved image to {filepath}")
    return filename

def process_image(image_data):
    # Convert base64 to image
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert PIL Image to OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Apply a simple filter (grayscale)
    processed_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    
    # Convert back to PIL Image
    processed_pil = Image.fromarray(processed_image)
    
    # Convert to base64
    buffered = io.BytesIO()
    processed_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        logger.info("Received upload request")
        data = request.json
        if not data or 'image' not in data:
            logger.error("No image data in request")
            return jsonify({'error': 'No image data provided'}), 400
        
        # Save the original image
        filename = save_image(data['image'])
        logger.info(f"Saved original image as {filename}")
        
        # Process the image
        processed_image = process_image(data['image'])
        
        # Save the processed image
        processed_filename = f"processed_{filename}"
        processed_filepath = os.path.join(UPLOAD_FOLDER, processed_filename)
        processed_bytes = base64.b64decode(processed_image.split(',')[1])
        with open(processed_filepath, 'wb') as f:
            f.write(processed_bytes)
        logger.info(f"Saved processed image as {processed_filename}")
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded and processed successfully',
            'original_image': f"/uploads/{filename}",
            'processed_image': f"/uploads/{processed_filename}"
        })
    
    except Exception as e:
        logger.error(f"Error in upload_image: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def get_image(filename):
    logger.info(f"Serving image: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/images', methods=['GET'])
def get_images():
    try:
        logger.info("Received request for images list")
        images = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith('processed_'):
                # Get the original image filename
                original_filename = filename[10:]  # Remove 'processed_' prefix
                if os.path.exists(os.path.join(UPLOAD_FOLDER, original_filename)):
                    # Get file creation time
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    timestamp = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    images.append({
                        'id': filename,
                        'url': f"/uploads/{filename}",
                        'timestamp': timestamp.isoformat()
                    })
        
        # Sort images by timestamp, newest first
        images.sort(key=lambda x: x['timestamp'], reverse=True)
        logger.info(f"Found {len(images)} images")
        
        return jsonify({'images': images})
    
    except Exception as e:
        logger.error(f"Error in get_images: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 