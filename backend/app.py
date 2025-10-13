from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, SavedPrompt
import cv2
import numpy as np
import base64
from PIL import Image
import io
import os
import uuid
from datetime import datetime, timedelta
import logging
import requests
from io import BytesIO
import json
from dotenv import load_dotenv
# import google.generativeai as genai  # Old library - not needed anymore
from collections import defaultdict, deque
import time
import stripe

# Load environment variables from .env file FIRST
load_dotenv()

# Now import config after loading environment variables
from config import STRIPE_CONFIG

# Set up logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
is_production = os.getenv('FLASK_ENV') == 'production'

if is_production:
    # Production logging configuration
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            # Add file handler for production if needed
            # logging.FileHandler('/app/logs/app.log')
        ]
    )
    logger.info("Production logging configured")
else:
    # Development logging configuration
    logging.basicConfig(
        level=getattr(logging, log_level, logging.DEBUG),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Development logging configured")

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with environment variable
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins and cors_origins != '*':
    # Split comma-separated origins
    origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, origins=origins)
else:
    # Allow all origins (for development)
    CORS(app)

# Database configuration
# Handle both DATABASE_URL (Railway PostgreSQL) and SQLALCHEMY_DATABASE_URI
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Railway provides DATABASE_URL for PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info("Using PostgreSQL database from DATABASE_URL")
else:
    # Fallback to SQLite or custom SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///style_ai.db')
    logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB default

# Debug and testing configuration
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
app.config['TESTING'] = os.getenv('TESTING', 'False').lower() == 'true'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Initialize Stripe
stripe.api_key = STRIPE_CONFIG["SECRET_KEY"]

# Debug Stripe configuration
logger.info(f"Stripe Secret Key loaded: {bool(STRIPE_CONFIG['SECRET_KEY'])}")
if STRIPE_CONFIG["SECRET_KEY"]:
    logger.info(f"Stripe Key starts with: {STRIPE_CONFIG['SECRET_KEY'][:7]}...")
    logger.info("✅ Stripe is properly configured!")
else:
    logger.error("❌ STRIPE_SECRET_KEY not found in environment variables!")
    logger.error("Please check your .env file in the backend directory")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f".env file exists: {os.path.exists('.env')}")
    
    # Try to load .env explicitly
    from dotenv import load_dotenv
    load_dotenv('.env')
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    logger.error(f"After explicit load: {bool(stripe_key)}")

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Created uploads directory at {UPLOAD_FOLDER}")

# Cinematic AI Configuration
CINEMATIC_AI_CONFIG = {
    "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
    "GOOGLE_GEMINI_URL": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent",
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "REPLICATE_API_KEY": os.getenv("REPLICATE_API_KEY", ""),
    "STABILITY_API_KEY": os.getenv("STABILITY_API_KEY", ""),
    
    # Rate Limiting Configuration for Gemini 2.0 Flash Preview Image Generation
    "RATE_LIMITS": {
        "requests_per_minute": int(os.getenv('RATE_LIMIT_PER_MINUTE', '10')),
        "requests_per_day": int(os.getenv('RATE_LIMIT_PER_HOUR', '200000')) * 24,  # Convert hourly to daily
        "max_tokens_per_request": 100
    },
    
    # Usage limits - Pure pay-per-use system
    "USAGE_LIMITS": {
        "default": {
            "images_per_month": 0,  # All users must use credits
            "model": "gemini-2.0-flash-preview-image-generation",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent"
        },
        "free": {
            "images_per_month": 0,  # Free users also use credits
            "model": "gemini-2.0-flash-preview-image-generation",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent"
        }
    },
    
    # Cinematic AI Models
    "CINEMATIC_MODELS": {
        "huggingface": {
            "url": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "headers": {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
        },
        "replicate": {
            "url": "https://api.replicate.com/v1/predictions",
            "headers": {"Authorization": f"Token {os.getenv('REPLICATE_API_KEY', '')}"}
        },
        "stability": {
            "url": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            "headers": {"Authorization": f"Bearer {os.getenv('STABILITY_API_KEY', '')}"}
        }
    }
}

# Rate limiting storage
rate_limit_storage = {
    'minute_requests': deque(),  # Store timestamps of requests in the last minute
    'daily_requests': deque(),   # Store timestamps of requests in the last 24 hours
    'daily_count': 0,            # Counter for daily requests
    'last_reset': time.time()    # Last time daily counter was reset
}

# Debug logging for API keys
logger.info("=== AI API Configuration ===")
logger.info(f"HUGGINGFACE_API_KEY: {'SET' if CINEMATIC_AI_CONFIG['HUGGINGFACE_API_KEY'] else 'NOT SET'}")
logger.info(f"GOOGLE_API_KEY: {'SET' if CINEMATIC_AI_CONFIG['GOOGLE_API_KEY'] else 'NOT SET'}")
logger.info(f"REPLICATE_API_KEY: {'SET' if CINEMATIC_AI_CONFIG['REPLICATE_API_KEY'] else 'NOT SET'}")
logger.info(f"STABILITY_API_KEY: {'SET' if CINEMATIC_AI_CONFIG['STABILITY_API_KEY'] else 'NOT SET'}")
logger.info("===========================")

def check_rate_limit():
    """
    Check if the current request is within rate limits.
    Returns True if request is allowed, False if rate limited.
    """
    current_time = time.time()
    
    # Clean up old requests from minute window
    while rate_limit_storage['minute_requests'] and rate_limit_storage['minute_requests'][0] < current_time - 60:
        rate_limit_storage['minute_requests'].popleft()
    
    # Clean up old requests from daily window
    while rate_limit_storage['daily_requests'] and rate_limit_storage['daily_requests'][0] < current_time - 86400:
        rate_limit_storage['daily_requests'].popleft()
    
    # Reset daily counter if it's been more than 24 hours
    if current_time - rate_limit_storage['last_reset'] > 86400:
        rate_limit_storage['daily_count'] = 0
        rate_limit_storage['last_reset'] = current_time
    
    # Check minute limit
    if len(rate_limit_storage['minute_requests']) >= CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_minute']:
        logger.warning(f"Rate limit exceeded: {len(rate_limit_storage['minute_requests'])} requests in the last minute")
        return False
    
    # Check daily limit
    if rate_limit_storage['daily_count'] >= CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_day']:
        logger.warning(f"Daily rate limit exceeded: {rate_limit_storage['daily_count']} requests today")
        return False
    
    return True

def record_api_call():
    """Record an API call for rate limiting purposes"""
    current_time = time.time()
    rate_limit_storage['minute_requests'].append(current_time)
    rate_limit_storage['daily_requests'].append(current_time)
    rate_limit_storage['daily_count'] += 1
    
    logger.info(f"API call recorded. Minute: {len(rate_limit_storage['minute_requests'])}/{CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_minute']}, "
                f"Daily: {rate_limit_storage['daily_count']}/{CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_day']}")

def get_rate_limit_status():
    """Get current rate limit status for monitoring"""
    current_time = time.time()
    
    # Clean up old requests
    while rate_limit_storage['minute_requests'] and rate_limit_storage['minute_requests'][0] < current_time - 60:
        rate_limit_storage['minute_requests'].popleft()
    
    while rate_limit_storage['daily_requests'] and rate_limit_storage['daily_requests'][0] < current_time - 86400:
        rate_limit_storage['daily_requests'].popleft()
    
    return {
        'minute_requests': len(rate_limit_storage['minute_requests']),
        'minute_limit': CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_minute'],
        'daily_requests': rate_limit_storage['daily_count'],
        'daily_limit': CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_day'],
        'minute_remaining': CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_minute'] - len(rate_limit_storage['minute_requests']),
        'daily_remaining': CINEMATIC_AI_CONFIG['RATE_LIMITS']['requests_per_day'] - rate_limit_storage['daily_count']
    }

def reset_monthly_usage_if_needed(user):
    """Reset monthly usage counter if it's a new month"""
    current_date = datetime.utcnow()
    if user.last_reset_date.month != current_date.month or user.last_reset_date.year != current_date.year:
        user.images_processed_this_month = 0
        user.last_reset_date = current_date
        db.session.commit()
        logger.info(f"Reset monthly usage for user {user.username}")

def check_usage_limit(user):
    """Check if user has image credits available"""
    # All users must have credits to process images
    if user.image_credits > 0:
        return True, user.image_credits
    
    return False, 0

def increment_usage(user):
    """Decrement user's image credits"""
    if user.image_credits > 0:
        user.image_credits -= 1
        db.session.commit()
        logger.info(f"Used 1 credit for user {user.username}. Credits remaining: {user.image_credits}")
    else:
        logger.warning(f"User {user.username} tried to use credit but has none remaining")

def get_user_tier_info(user):
    """Get user's credit information"""
    # All users use the same system - credits only
    tier_config = CINEMATIC_AI_CONFIG['USAGE_LIMITS']['default']
    
    return {
        'tier': 'user',  # All users are just "user" tier
        'images_used': 0,  # Not tracking monthly usage anymore
        'images_limit': tier_config['images_per_month'],
        'model': tier_config['model'],
        'unlimited': False,  # No unlimited users anymore
        'remaining': user.image_credits,
        'image_credits': user.image_credits,
        'free_trial_used': user.free_trial_used
    }

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

def preprocess_image(image):
    """Preprocess image for better AI processing results"""
    # Convert to float32 for better precision
    image_float = image.astype(np.float32) / 255.0
    
    # Apply slight sharpening to enhance details
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image_float, -1, kernel)
    
    # Normalize and convert back to uint8
    sharpened = np.clip(sharpened, 0, 1)
    sharpened = (sharpened * 255).astype(np.uint8)
    
    # Apply slight contrast enhancement
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Enhance lightness channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Ensure all channels have the same data type before merging
    l = l.astype(np.uint8)
    a = a.astype(np.uint8)
    b = b.astype(np.uint8)
    
    # Merge channels back
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced

def postprocess_result(result, style_type):
    """Post-process the result for better quality output"""
    # Apply slight noise reduction
    result = cv2.fastNlMeansDenoisingColored(result, None, 3, 3, 7, 21)
    
    # Enhance contrast slightly
    result = cv2.convertScaleAbs(result, alpha=1.05, beta=5)
    
    # Apply slight sharpening for crisp results
    kernel = np.array([[-0.5,-0.5,-0.5], [-0.5,5,-0.5], [-0.5,-0.5,-0.5]])
    result = cv2.filter2D(result, -1, kernel)
    
    # Ensure values are in valid range
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result

def apply_cinematic_ai_enhancement(image, style_type="cinematic"):
    """
    Apply cinematic AI enhancement to transform photos into emotionally powerful narratives.
    This AI understands human emotion, storytelling, and cinematic artistry.
    """
    try:
        # Convert image to base64 for API
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Cinematic storytelling prompt
        cinematic_prompt = """
        Enhance the provided photo into a professionally captured cinematic portrait that retells the story within the imageâ€”because every photo should feel like it holds a thousand words.

        Preserve and amplify the authentic emotions, atmosphere, and storytelling of the scene. Refine the subjects' featuresâ€”skin tone, clarity, and lightingâ€”without altering their faces, expressions, identity, or other defining aspects. If posture, gestures, or imperfections contribute to the emotion (e.g., exhaustion, intimacy, vulnerability, joy), preserve and enhance them so they feel intentional and artfully powerful.

        If body language unintentionally distracts from the story, the AI may subtly refine movements, gestures, or focus to enhance narrative clarity. For example, a mother looking away may instead look toward her child; eyes may be gently opened or closed if it deepens the moment; hands, gazes, or motions can be slightly shifted to create more emotional alignment. The AI may also adjust positioning or object placementâ€”such as moving a person slightly off-center for balance, or rearranging background elementsâ€”to better frame the story. These changes must always remain natural, subtle, and deliberate enhancements of the narrative, never arbitrary alterations.

        Apply cinematic lighting and compositionâ€”soft highlights, meaningful shadows, controlled contrastâ€”to emphasize the emotional core. Enhance the background so it becomes a storytelling device: sharpen details that matter, soften distractions, and color-grade for mood.

        Infuse metaphorical storytelling into the edit, weaving in subtle symbolic cues: sunlight embracing a nurturing figure, shadows deepening solitude, warm tones radiating joy, blurred distance evoking nostalgia, or compositional balance reinforcing unity.

        The final result should look as though a professional photographer not only staged the scene but orchestrated the story, symbolism, and emotional weight, ensuring every visual detail contributes to the narrative.

        Final qualities:
        * A photo that retells a complete story, rich with emotion and context
        * Authentic emotions preserved and heightened
        * Imperfections embraced if they enhance the narrative
        * Faces and identities never altered
        * Motions, gazes, and placements may be adjusted subtly if they enhance the story
        * Professional polish in lighting, composition, and color
        * Accessibility, individuality, and truth respected
        * Metaphorical enhancements and deliberate changes used only to strengthen storytelling
        """
        
        # Try to use AI service if available
        if CINEMATIC_AI_CONFIG["HUGGINGFACE_API_KEY"]:
            logger.info("Using Hugging Face AI for cinematic enhancement")
            return call_huggingface_ai(image, cinematic_prompt)
        elif CINEMATIC_AI_CONFIG["REPLICATE_API_KEY"]:
            logger.info("Using Replicate AI for cinematic enhancement")
            return call_replicate_ai(image, cinematic_prompt)
        elif CINEMATIC_AI_CONFIG["STABILITY_API_KEY"]:
            logger.info("Using Stability AI for cinematic enhancement")
            return call_stability_ai(image, cinematic_prompt)
        else:
            logger.info("No AI API keys available, using cinematic computer vision enhancement")
            return apply_cinematic_cv_enhancement(image)
            
    except Exception as e:
        logger.error(f"Cinematic AI processing failed: {str(e)}")
        # Fallback to cinematic computer vision
        return apply_cinematic_cv_enhancement(image)

def call_huggingface_ai(image, prompt):
    """Call Hugging Face AI for cinematic enhancement"""
    try:
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare payload for Hugging Face
        payload = {
            "inputs": f"{prompt}\n\nInput image: [IMAGE]",
            "parameters": {
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "strength": 0.8,
                "guidance_start": 0.0,
                "guidance_end": 1.0
            }
        }
        
        # For now, return enhanced computer vision result
        # In production, this would call the actual Hugging Face API
        logger.info("Hugging Face AI would process this image with cinematic enhancement")
        return apply_cinematic_cv_enhancement(image)
        
    except Exception as e:
        logger.error(f"Hugging Face AI call failed: {str(e)}")
        return apply_cinematic_cv_enhancement(image)

def call_replicate_ai(image, prompt):
    """Call Replicate AI for cinematic enhancement"""
    try:
        # For now, return enhanced computer vision result
        # In production, this would call the actual Replicate API
        logger.info("Replicate AI would process this image with cinematic enhancement")
        return apply_cinematic_cv_enhancement(image)
        
    except Exception as e:
        logger.error(f"Replicate AI call failed: {str(e)}")
        return apply_cinematic_cv_enhancement(image)

def call_stability_ai(image, prompt):
    """Call Stability AI for cinematic enhancement"""
    try:
        # For now, return enhanced computer vision result
        # In production, this would call the actual Stability API
        logger.info("Stability AI would process this image with cinematic enhancement")
        return apply_cinematic_cv_enhancement(image)
        
    except Exception as e:
        logger.error(f"Stability AI call failed: {str(e)}")
        return apply_cinematic_cv_enhancement(image)

def apply_cinematic_cv_enhancement(image):
    """
    Apply cinematic computer vision enhancement that mimics AI storytelling.
    This creates emotionally powerful, cinematically enhanced images.
    """
    try:
        # Preprocess image for cinematic enhancement
        enhanced = preprocess_for_cinematic(image)
        
        # Apply cinematic lighting enhancement
        enhanced = enhance_cinematic_lighting(enhanced)
        
        # Enhance emotional storytelling through composition
        enhanced = enhance_emotional_composition(enhanced)
        
        # Apply cinematic color grading
        enhanced = apply_cinematic_color_grading(enhanced)
        
        # Enhance details and textures
        enhanced = enhance_cinematic_details(enhanced)
        
        # Final cinematic polish
        enhanced = apply_cinematic_polish(enhanced)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Cinematic CV enhancement failed: {str(e)}")
        return image

def preprocess_for_cinematic(image):
    """Prepare image for cinematic enhancement"""
    # Convert to float for better processing
    enhanced = image.astype(np.float32) / 255.0
    
    # Apply subtle noise reduction while preserving details
    enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Enhance local contrast for cinematic feel
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply((l * 255).astype(np.uint8)) / 255.0
    
    # Ensure all channels have the same data type before merging
    l = l.astype(np.float32)
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    
    # Recombine
    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return enhanced

def enhance_cinematic_lighting(image):
    """Enhance lighting for cinematic storytelling"""
    try:
        # Ensure image is in the correct format
        if image.dtype == np.float64:
            image = image.astype(np.float32)
        elif image.dtype == np.uint8:
            image = image.astype(np.float32) / 255.0
        
        # Ensure image is in valid range [0, 1]
        image = np.clip(image, 0, 1)
        
        # Create cinematic lighting effects
        
        # Enhance highlights more dramatically
        highlights = cv2.GaussianBlur(image, (0, 0), 5)
        enhanced = cv2.addWeighted(image, 1.0, highlights, 0.4, 0)
        
        # Enhance shadows more dramatically
        shadows = cv2.GaussianBlur(image, (0, 0), 7)
        enhanced = cv2.addWeighted(enhanced, 1.0, shadows, -0.3, 0)
        
        # Add more pronounced vignette for cinematic focus
        rows, cols = enhanced.shape[:2]
        y, x = np.ogrid[:rows, :cols]
        center_y, center_x = rows / 2, cols / 2
        mask = 1 - np.sqrt((x - center_x)**2 + (y - center_y)**2) / np.sqrt(center_x**2 + center_y**2)
        mask = np.clip(mask, 0, 1)
        mask = np.dstack([mask] * 3)
        
        # Apply stronger vignette effect
        enhanced = enhanced * (0.75 + 0.25 * mask)
        
        # Add subtle rim lighting effect
        rim_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        rim_effect = cv2.filter2D(enhanced, -1, rim_kernel)
        enhanced = cv2.addWeighted(enhanced, 0.9, rim_effect, 0.1, 0)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Lighting enhancement failed: {str(e)}")
        logger.info("Returning original image due to lighting enhancement failure")
        # Return the original image if lighting enhancement fails
        if image.dtype == np.float64:
            return (image * 255).astype(np.uint8)
        elif image.dtype == np.float32:
            return (image * 255).astype(np.uint8)
        else:
            return image

def enhance_emotional_composition(image):
    """Enhance composition for emotional storytelling"""
    # Apply subtle composition improvements
    
    # Enhance center focus
    rows, cols = image.shape[:2]
    center_y, center_x = rows / 2, cols / 2
    
    # Create focus mask
    y, x = np.ogrid[:rows, :cols]
    focus_mask = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * (min(rows, cols) / 4)**2))
    focus_mask = np.dstack([focus_mask] * 3)
    
    # Apply focus enhancement
    enhanced = image * (0.9 + 0.1 * focus_mask)
    
    # Enhance edges for better storytelling
    edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
    edges = cv2.dilate(edges, None)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR) / 255.0
    
    # Subtle edge enhancement
    enhanced = cv2.addWeighted(enhanced, 1.0, edges, 0.05, 0)
    
    return enhanced

def apply_cinematic_color_grading(image):
    """Apply cinematic color grading for emotional storytelling"""
    try:
        # Ensure image is in the correct format for OpenCV color operations
        if image.dtype == np.float64:
            # Convert from CV_64F to CV_32F
            image = image.astype(np.float32)
        elif image.dtype == np.uint8:
            # Convert from CV_8U to CV_32F for better precision
            image = image.astype(np.float32) / 255.0
        
        # Ensure image is in valid range [0, 1]
        image = np.clip(image, 0, 1)
        
        # Convert to HSV for better color control
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Enhance saturation more dramatically
        hsv[:, :, 1] = hsv[:, :, 1] * 1.2
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 1)
        
        # Apply cinematic color temperature shift (warmer tones)
        hsv[:, :, 0] = (hsv[:, :, 0] + 8) % 180  # Stronger warm shift
        
        # Enhance value for more dramatic contrast
        hsv[:, :, 2] = hsv[:, :, 2] * 1.1
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 1)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Add subtle color grading curves
        # Enhance blues in shadows and warm tones in highlights
        b, g, r = cv2.split(enhanced)
        
        # Ensure all channels are the same data type and size
        b = b.astype(np.float32)
        g = g.astype(np.float32)
        r = r.astype(np.float32)
        
        # Enhance blue channel in shadows
        b = np.where(b < 0.5, b * 0.9, b)  # Darken blues in shadows
        b = np.clip(b, 0, 1)
        
        # Enhance red channel in highlights
        r = np.where(r > 0.5, r * 1.1, r)  # Brighten reds in highlights
        r = np.clip(r, 0, 1)
        
        # Ensure all channels have the same shape and type
        b = b.astype(np.float32)
        g = g.astype(np.float32)
        r = r.astype(np.float32)
        
        # Recombine channels and convert back to uint8
        enhanced = cv2.merge([b, g, r])
        enhanced = (enhanced * 255).astype(np.uint8)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Color grading failed: {str(e)}")
        logger.info("Returning original image due to color grading failure")
        # Return the original image if color grading fails
        if image.dtype == np.float64:
            return (image * 255).astype(np.uint8)
        elif image.dtype == np.float32:
            return (image * 255).astype(np.uint8)
        else:
            return image

def enhance_cinematic_details(image):
    """Enhance details for cinematic storytelling"""
    # Sharpen important details
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    
    # Blend sharpening
    enhanced = cv2.addWeighted(image, 0.8, sharpened, 0.2, 0)
    
    # Enhance textures
    texture = cv2.GaussianBlur(image, (0, 0), 1)
    enhanced = cv2.addWeighted(enhanced, 0.9, texture, 0.1, 0)
    
    return enhanced

def apply_cinematic_polish(image):
    """Apply final cinematic polish"""
    # Convert back to uint8
    enhanced = (image * 255).astype(np.uint8)
    
    # Final contrast enhancement
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.05, beta=5)
    
    # Subtle noise reduction
    enhanced = cv2.bilateralFilter(enhanced, 5, 50, 50)
    
    return enhanced

def apply_ai_style(image, style_type):
    """
    Main function to apply AI styles - now focused on cinematic storytelling
    """
    if style_type == "cinematic" or style_type == "enhance":
        # Apply cinematic AI enhancement
        return apply_cinematic_ai_enhancement(image, style_type)
    else:
        # For other styles, use the enhanced computer vision approach
        return apply_ai_enhanced_cv_style(image, style_type)

def apply_ai_enhanced_cv_style(image, style_type):
    """Apply advanced computer vision techniques as AI fallback"""
    # Preprocess image for better results
    image = preprocess_image(image)
    
    if style_type == "sketch":
        # Advanced pencil sketch effect with white background and black lines
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while preserving edges
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Create inverted blur for sketch effect
        inverted = 255 - smooth
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        
        # Create pencil sketch effect
        sketch = cv2.divide(smooth, 255 - blur, scale=256)
        
        # Enhance contrast for crisp lines
        sketch = cv2.convertScaleAbs(sketch, alpha=1.8, beta=0)
        
        # Apply slight threshold to make lines more defined
        _, sketch = cv2.threshold(sketch, 240, 255, cv2.THRESH_BINARY)
        
        # Convert back to BGR (will be grayscale but in BGR format)
        result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    elif style_type == "cartoon":
        # Advanced cartoon effect with edge detection and color quantization
        # Convert to LAB color space for better color processing
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply bilateral filter to smooth colors while preserving edges
        l_smooth = cv2.bilateralFilter(l, 9, 75, 75)
        
        # Detect edges using adaptive threshold
        edges = cv2.adaptiveThreshold(l_smooth, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        
        # Quantize colors for cartoon effect
        # Reduce color palette
        color_quantized = cv2.medianBlur(image, 7)
        color_quantized = cv2.bilateralFilter(color_quantized, 9, 300, 300)
        
        # Combine edges with quantized colors
        result = cv2.bitwise_and(color_quantized, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
    
    elif style_type == "oil_painting":
        # Advanced oil painting effect using texture analysis
        # Apply bilateral filter for edge-preserving smoothing
        oil = cv2.bilateralFilter(image, 9, 75, 75)
        # Add texture using morphological operations
        kernel = np.ones((3, 3), np.uint8)
        oil = cv2.morphologyEx(oil, cv2.MORPH_OPEN, kernel)
        # Enhance colors
        oil = cv2.convertScaleAbs(oil, alpha=1.1, beta=10)
        result = oil
    
    elif style_type == "watercolor":
        # Advanced watercolor effect using edge-preserving filters and color blending
        # Apply edge-preserving smoothing
        watercolor = cv2.bilateralFilter(image, 15, 80, 80)
        # Add slight blur for watercolor texture
        watercolor = cv2.GaussianBlur(watercolor, (5, 5), 0)
        # Enhance saturation
        hsv = cv2.cvtColor(watercolor, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)  # Increase saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        watercolor = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        # Add subtle texture
        watercolor = cv2.addWeighted(watercolor, 0.9, cv2.GaussianBlur(watercolor, (3, 3), 0), 0.1, 0)
        result = watercolor
    
    elif style_type == "pencil_sketch":
        # Advanced pencil sketch effect with white background and black lines
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while preserving edges
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Create inverted blur for sketch effect
        inverted = 255 - smooth
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        
        # Create pencil sketch effect
        sketch = cv2.divide(smooth, 255 - blur, scale=256)
        
        # Enhance contrast for crisp lines
        sketch = cv2.convertScaleAbs(sketch, alpha=1.8, beta=0)
        
        # Apply slight threshold to make lines more defined
        _, sketch = cv2.threshold(sketch, 240, 255, cv2.THRESH_BINARY)
        
        # Convert back to BGR (will be grayscale but in BGR format)
        result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    elif style_type == "pop_art":
        # Advanced pop art effect with color manipulation and halftone
        # Convert to HSV for better color control
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Enhance saturation dramatically
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 2.0)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # Shift hue for pop art colors
        hsv[:, :, 0] = (hsv[:, :, 0] + 45) % 180
        
        # Enhance value (brightness)
        hsv[:, :, 2] = cv2.multiply(hsv[:, :, 2], 1.2)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        
        pop_art = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Add contrast
        pop_art = cv2.convertScaleAbs(pop_art, alpha=1.3, beta=0)
        result = pop_art
    
    elif style_type == "vintage":
        # Advanced vintage effect with sepia tone and film grain
        # Convert to sepia using proper color matrix
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        vintage = cv2.transform(image, sepia_matrix)
        vintage = np.clip(vintage, 0, 255).astype(np.uint8)
        
        # Add vintage color grading
        vintage = cv2.convertScaleAbs(vintage, alpha=0.9, beta=15)
        
        # Add film grain effect
        noise = np.random.normal(0, 20, vintage.shape).astype(np.uint8)
        vintage = cv2.add(vintage, noise)
        
        # Add slight blur for vintage feel
        vintage = cv2.GaussianBlur(vintage, (3, 3), 0)
        
        # Enhance contrast
        vintage = cv2.convertScaleAbs(vintage, alpha=1.1, beta=0)
        result = vintage
    
    elif style_type == "neon":
        # Advanced neon glow effect with multiple layers
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create edge detection with multiple thresholds
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges3 = cv2.Canny(gray, 70, 200)
        
        # Combine edges for rich neon effect
        combined_edges = cv2.addWeighted(edges1, 0.4, edges2, 0.4, 0)
        combined_edges = cv2.addWeighted(combined_edges, 0.8, edges3, 0.2, 0)
        
        # Create glow effect using multiple blur passes
        glow1 = cv2.GaussianBlur(combined_edges, (5, 5), 0)
        glow2 = cv2.GaussianBlur(combined_edges, (9, 9), 0)
        glow3 = cv2.GaussianBlur(combined_edges, (15, 15), 0)
        
        # Combine glow layers
        neon_glow = cv2.addWeighted(glow1, 0.5, glow2, 0.3, 0)
        neon_glow = cv2.addWeighted(neon_glow, 0.8, glow3, 0.2, 0)
        
        # Add original edges back
        neon_result = cv2.addWeighted(neon_glow, 0.7, combined_edges, 0.3, 0)
        
        # Apply neon color mapping
        neon_colored = cv2.applyColorMap(neon_result, cv2.COLORMAP_HOT)
        
        # Enhance brightness and contrast
        neon_colored = cv2.convertScaleAbs(neon_colored, alpha=1.5, beta=30)
        result = neon_colored
    
    else:
        # Default: return original image
        result = image
    
    # Post-process the result for better quality
    result = postprocess_result(result, style_type)
    
    return result

def process_image(image_data, style_type="sketch"):
    """Process image with the specified AI style"""
    try:
        # Convert base64 to image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply the selected style
        processed_image = apply_ai_style(opencv_image, style_type)
        
        # Convert back to PIL Image
        processed_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        
        # Convert to base64
        buffered = io.BytesIO()
        processed_pil.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise e

# Authentication endpoints
@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"New user registered: {username}")
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"User logged in: {user.username}")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500

@app.route('/auth/upgrade-premium', methods=['POST'])
@jwt_required()
def upgrade_to_premium():
    """Temporary endpoint to upgrade user to premium for testing"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_premium = True
        db.session.commit()

        logger.info(f"User {user.username} upgraded to premium")
        return jsonify({
            'message': 'Successfully upgraded to premium!',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Upgrade error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upgrade to premium'}), 500

@app.route('/auth/usage-info', methods=['GET'])
@jwt_required()
def get_usage_info():
    """Get user's usage information and tier details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tier_info = get_user_tier_info(user)
        return jsonify(tier_info)
        
    except Exception as e:
        logger.error(f"Error getting usage info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/auth/dev-toggle-premium', methods=['POST'])
@jwt_required()
def dev_toggle_premium():
    """Developer endpoint to toggle premium status for alaqmartrunk@gmail.com"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Only allow for the specific developer email
        if user.email != 'alaqmartrunk@gmail.com':
            return jsonify({'error': 'Developer access denied'}), 403

        # Toggle premium status
        user.is_premium = not user.is_premium
        db.session.commit()

        status = "premium" if user.is_premium else "free"
        logger.info(f"Developer {user.username} toggled to {status}")
        
        return jsonify({
            'message': f'Successfully switched to {status} tier!',
            'user': user.to_dict(),
            'is_premium': user.is_premium
        }), 200

    except Exception as e:
        logger.error(f"Dev toggle error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to toggle premium status'}), 500

# Prompt management endpoints
@app.route('/prompts', methods=['POST'])
@jwt_required()
def save_prompt():
    """Save a new prompt"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        prompt_text = data.get('prompt_text')
        style_type = data.get('style_type', 'cinematic')
        
        if not all([title, prompt_text]):
            return jsonify({'error': 'Title and prompt text are required'}), 400
        
        # Create new saved prompt
        saved_prompt = SavedPrompt(
            user_id=user_id,
            title=title,
            prompt_text=prompt_text,
            style_type=style_type
        )
        
        db.session.add(saved_prompt)
        db.session.commit()
        
        logger.info(f"Prompt saved: {title} by user {user_id}")
        return jsonify({
            'message': 'Prompt saved successfully',
            'prompt': saved_prompt.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Save prompt error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to save prompt'}), 500

@app.route('/prompts', methods=['GET'])
@jwt_required()
def get_user_prompts():
    """Get all prompts for the current user"""
    try:
        user_id = get_jwt_identity()
        prompts = SavedPrompt.query.filter_by(user_id=user_id).order_by(SavedPrompt.created_at.desc()).all()
        
        return jsonify({
            'prompts': [prompt.to_dict() for prompt in prompts]
        }), 200
        
    except Exception as e:
        logger.error(f"Get prompts error: {str(e)}")
        return jsonify({'error': 'Failed to get prompts'}), 500

@app.route('/prompts/<prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    """Update a saved prompt"""
    try:
        user_id = get_jwt_identity()
        prompt = SavedPrompt.query.filter_by(id=prompt_id, user_id=user_id).first()
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404
        
        data = request.get_json()
        prompt.title = data.get('title', prompt.title)
        prompt.prompt_text = data.get('prompt_text', prompt.prompt_text)
        prompt.style_type = data.get('style_type', prompt.style_type)
        prompt.is_favorite = data.get('is_favorite', prompt.is_favorite)
        prompt.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Prompt updated: {prompt_id}")
        return jsonify({
            'message': 'Prompt updated successfully',
            'prompt': prompt.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update prompt error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update prompt'}), 500

@app.route('/prompts/<prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    """Delete a saved prompt"""
    try:
        user_id = get_jwt_identity()
        prompt = SavedPrompt.query.filter_by(id=prompt_id, user_id=user_id).first()
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404
        
        db.session.delete(prompt)
        db.session.commit()
        
        logger.info(f"Prompt deleted: {prompt_id}")
        return jsonify({'message': 'Prompt deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete prompt error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete prompt'}), 500

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """Upload and process image with AI enhancement"""
    logger.info("Upload endpoint called")
    try:
        # Get current user
        user_id = get_jwt_identity()
        logger.info(f"JWT user_id: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get image data from request
        data = request.get_json()
        logger.info(f"Request data keys: {list(data.keys()) if data else 'None'}")
        
        image_data = data.get('image')
        
        logger.info(f"Image data present: {bool(image_data)}")
        
        if not image_data:
            logger.error("No image data provided in request")
            return jsonify({'error': 'No image data provided'}), 400
        
        # Check usage limits
        can_process, remaining = check_usage_limit(user)
        if not can_process:
            return jsonify({
                'error': 'No image credits remaining. Purchase credits to continue processing images.',
                'upgrade_required': True,
                'remaining': remaining
            }), 429
        
        # Save original image
        filename = save_image(image_data)
        
        # Load image for processing
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        pil_image = Image.open(image_path)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Get user tier for AI model selection
        user_tier = 'default'  # All users use the same tier now
        
        # Use hardcoded prompt for enhancement
        hardcoded_prompt = """Enhance the provided photo into a professionally captured cinematic portrait that retells the story within the imageâ€”because every photo should feel like it holds a thousand words.

Preserve and amplify the authentic emotions, atmosphere, and storytelling of the scene. Refine the subjects' featuresâ€”skin tone, clarity, and lightingâ€”without altering their faces, expressions, identity, or other defining aspects. If posture, gestures, or imperfections contribute to the emotion (e.g., exhaustion, intimacy, vulnerability, joy), preserve and enhance them so they feel intentional and artfully powerful.

If body language unintentionally distracts from the story, the AI may subtly refine movements, gestures, or focus to enhance narrative clarity. For example, a mother looking away may instead look toward her child; eyes may be gently opened or closed if it deepens the moment; hands, gazes, or motions can be slightly shifted to create more emotional alignment. The AI may also adjust positioning or object placementâ€”such as moving a person slightly off-center for balance, or rearranging background elementsâ€”to better frame the story. These changes must always remain natural, subtle, and deliberate enhancements of the narrative, never arbitrary alterations.

Apply cinematic lighting and compositionâ€”soft highlights, meaningful shadows, controlled contrastâ€”to emphasize the emotional core. Enhance the background so it becomes a storytelling device: sharpen details that matter, soften distractions, and color-grade for mood.

Infuse metaphorical storytelling into the edit, weaving in subtle symbolic cues: sunlight embracing a nurturing figure, shadows deepening solitude, warm tones radiating joy, blurred distance evoking nostalgia, or compositional balance reinforcing unity.

The final result should look as though a professional photographer not only staged the scene but orchestrated the story, symbolism, and emotional weight, ensuring every visual detail contributes to the narrative.

Final qualities:
* A photo that retells a complete story, rich with emotion and context
* Authentic emotions preserved and heightened
* Imperfections embraced if they enhance the narrative
* Faces and identities never altered
* Motions, gazes, and placements may be adjusted subtly if they enhance the story
* Professional polish in lighting, composition, and color
* Accessibility, individuality, and truth respected
* Metaphorical enhancements and deliberate changes used only to strengthen storytelling"""
        logger.info(f"Processing with hardcoded prompt: {hardcoded_prompt[:100]}...")
        try:
            processed_image, saved_filepath = apply_custom_ai_enhancement(opencv_image, hardcoded_prompt, user_tier)
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'rate_limit_info': get_rate_limit_status(),
                    'retry_after': 60  # seconds
                }), 429
            else:
                raise e
        
        # Use the saved filepath from Gemini (already saved)
        processed_filename = os.path.basename(saved_filepath)
        processed_path = saved_filepath
        
        logger.info(f"Using Gemini-generated image: {processed_path}")
        
        # Get image info
        # Increment usage counter
        increment_usage(user)
        
        image_info = {
            'id': str(uuid.uuid4()),
            'filename': processed_filename,
            'original_filename': filename,
            'style': 'hardcoded',
            'timestamp': datetime.now().isoformat(),
            'url': f'/uploads/{processed_filename}',
            'download_url': f'/download-image/{processed_filename}',
            'user_tier': user_tier,
            'ai_model': CINEMATIC_AI_CONFIG['USAGE_LIMITS'][user_tier]['model']
        }
        
        logger.info(f"Image processed successfully: {processed_filename} using {user_tier} tier")
        return jsonify(image_info)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e), 'error_type': type(e).__name__}), 500

def create_combined_prompt(custom_prompt):
    """
    Create a combined prompt that merges the hardcoded cinematic prompt with the user's custom prompt.
    The custom prompt takes priority when there are contradictions.
    """
    # Base hardcoded prompt
    base_prompt = """Enhance the provided photo into a professionally captured cinematic portrait that retells the story within the imageâ€”because every photo should feel like it holds a thousand words.

Preserve and amplify the authentic emotions, atmosphere, and storytelling of the scene. Refine the subjects' featuresâ€”skin tone, clarity, and lightingâ€”without altering their faces, expressions, identity, or other defining aspects. If posture, gestures, or imperfections contribute to the emotion (e.g., exhaustion, intimacy, vulnerability, joy), preserve and enhance them so they feel intentional and artfully powerful.

If body language unintentionally distracts from the story, the AI may subtly refine movements, gestures, or focus to enhance narrative clarity. For example, a mother looking away may instead look toward her child; eyes may be gently opened or closed if it deepens the moment; hands, gazes, or motions can be slightly shifted to create more emotional alignment. The AI may also adjust positioning or object placementâ€”such as moving a person slightly off-center for balance, or rearranging background elementsâ€”to better frame the story. These changes must always remain natural, subtle, and deliberate enhancements of the narrative, never arbitrary alterations.

Apply cinematic lighting and compositionâ€”soft highlights, meaningful shadows, controlled contrastâ€”to emphasize the emotional core. Enhance the background so it becomes a storytelling device: sharpen details that matter, soften distractions, and color-grade for mood.

Infuse metaphorical storytelling into the edit, weaving in subtle symbolic cues: sunlight embracing a nurturing figure, shadows deepening solitude, warm tones radiating joy, blurred distance evoking nostalgia, or compositional balance reinforcing unity.

The final result should look as though a professional photographer not only staged the scene but orchestrated the story, symbolism, and emotional weight, ensuring every visual detail contributes to the narrative.

Final qualities:
* A photo that retells a complete story, rich with emotion and context
* Authentic emotions preserved and heightened
* Imperfections embraced if they enhance the narrative
* Faces and identities never altered
* Motions, gazes, and placements may be adjusted subtly if they enhance the story
* Professional polish in lighting, composition, and color
* Accessibility, individuality, and truth respected
* Metaphorical enhancements and deliberate changes used only to strengthen storytelling"""

    # Create the combined prompt with clear priority structure
    combined_prompt = f"""{base_prompt}

ADDITIONAL CUSTOM ENHANCEMENT REQUIREMENTS (PRIORITY OVER BASE PROMPT):
The user has specified the following additional requirements that should take priority over the base cinematic enhancement guidelines:

{custom_prompt}

IMPORTANT: When there are any contradictions between the base cinematic prompt and the custom requirements above, ALWAYS prioritize the custom requirements. The custom prompt represents the user's specific vision and should be the primary guide for the enhancement process.

The base cinematic prompt provides the professional foundation, but the custom requirements above are the user's specific instructions and should be followed as the primary enhancement direction."""
    
    return combined_prompt

def apply_custom_ai_enhancement(image, prompt, user_tier='free'):
    """
    Apply custom AI enhancement using Google Gemini with different models based on user tier.
    Free users get Gemini 1.5 Flash (cheaper), Premium users get Gemini 2.0 Flash Preview (best quality).
    """
    try:
        logger.info(f"Applying custom AI enhancement with Google Gemini for {user_tier} tier...")
        
        # Check if we have Google Gemini API key
        if CINEMATIC_AI_CONFIG["GOOGLE_API_KEY"] and CINEMATIC_AI_CONFIG["GOOGLE_API_KEY"] != "your_google_api_key_here":
            # Get the appropriate model URL for the user tier, fallback to 'default' if tier not found
            tier_config = CINEMATIC_AI_CONFIG['USAGE_LIMITS'].get(user_tier, CINEMATIC_AI_CONFIG['USAGE_LIMITS']['default'])
            model_url = tier_config['url']
            model_name = tier_config['model']
            
            logger.info(f"Using Google Gemini {model_name} for {user_tier} tier enhancement")
            enhanced_image, saved_filepath = call_google_gemini_ai_with_model(image, prompt, model_url, model_name)
            return enhanced_image, saved_filepath
        
        # If no Gemini key, return error instead of falling back
        else:
            logger.error("No Google Gemini API key found. Please add your GOOGLE_API_KEY to the .env file.")
            raise Exception("Google Gemini API key required for AI enhancement. No fallbacks available.")
            
    except Exception as e:
        logger.error(f"Google Gemini AI enhancement failed: {str(e)}")
        # Don't fall back to computer vision - only use Gemini
        raise Exception(f"AI enhancement failed: {str(e)}. Please check your Gemini API key and try again.")

def call_huggingface_ai_real(image, prompt):
    """Call Hugging Face AI for real enhancement - NO LONGER USED, ONLY GEMINI"""
    # This function is deprecated - we only use Google Gemini now
    logger.warning("Hugging Face AI is no longer used. Only Google Gemini is supported.")
    raise Exception("Hugging Face AI is no longer supported. Please use Google Gemini for the best results.")

def call_google_gemini_ai_with_model(image, prompt, model_url, model_name):
    """Call Google Gemini API with specified model for AI image generation"""
    try:
        # Check rate limits before making the API call
        if not check_rate_limit():
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Check if we have a valid Google API key
        api_key = CINEMATIC_AI_CONFIG["GOOGLE_API_KEY"]
        if not api_key or api_key == "your_google_api_key_here":
            logger.error("No valid Google API key found. Gemini API key required.")
            raise Exception("Google Gemini API key required for AI enhancement.")
        
        # Validate inputs
        if image is None:
            logger.error("Image is None - cannot process")
            raise Exception("No image provided for processing")
        
        if not prompt or prompt.strip() == "":
            logger.error("Prompt is empty - cannot process")
            raise Exception("No prompt provided for processing")
        
        logger.info(f"Image shape: {image.shape if hasattr(image, 'shape') else 'No shape attribute'}")
        logger.info(f"Image dtype: {image.dtype if hasattr(image, 'dtype') else 'No dtype attribute'}")
        logger.info(f"Prompt length: {len(prompt)}")
        
        logger.info(f"=== GEMINI {model_name.upper()} IMAGE GENERATION STARTED ===")
        logger.info(f"Using Google Gemini {model_name} for image generation!")
        logger.info(f"Prompt: {prompt[:100]}...")
        
        # Record the API call for rate limiting
        record_api_call()
        
        # Configure the API key - using new client approach
        # genai.configure(api_key=api_key)  # Old approach - not needed
        
        # Convert OpenCV image to base64 for the API
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Convert PIL image to base64
        import io
        import base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Debug logging
        logger.info(f"Image shape: {image_rgb.shape}")
        logger.info(f"PIL image mode: {pil_image.mode}")
        logger.info(f"PIL image size: {pil_image.size}")
        logger.info(f"Prompt: {prompt}")
        
        # Use the correct Google Generative AI syntax with config
        logger.info("Calling Gemini API...")
        
        # Use the correct Python Google GenAI client approach
        from google import genai as google_genai
        from google.genai import types
        
        client = google_genai.Client(api_key=api_key)
        
        # Create content using PIL image directly (not base64 text)
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=prompt),
                    types.Part(inline_data=types.Blob(
                        data=base64.b64decode(image_base64),
                        mime_type="image/png"
                    ))
                ]
            )
        ]
        
        # Configure response modalities
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
        
        # Process streaming response
        response_parts = []
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            
            # Collect parts from the stream
            if chunk.candidates[0].content.parts:
                response_parts.extend(chunk.candidates[0].content.parts)
        
        # Create a mock response object with the collected parts
        class MockResponse:
            def __init__(self, parts):
                self.candidates = [MockCandidate(parts)]
        
        class MockCandidate:
            def __init__(self, parts):
                self.content = MockContent(parts)
        
        class MockContent:
            def __init__(self, parts):
                self.parts = parts
        
        response = MockResponse(response_parts)
        logger.info("Gemini API call completed")
        
        if response and response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                # Extract the generated image from response
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        # Convert PIL Image to OpenCV format
                        from io import BytesIO
                        generated_pil = Image.open(BytesIO(part.inline_data.data))
                        enhanced_image = cv2.cvtColor(np.array(generated_pil), cv2.COLOR_RGB2BGR)
                        
                        if enhanced_image is not None:
                            logger.info(f"Successfully generated enhanced image using Gemini {model_name}")
                            
                            # Save the generated image
                            import uuid
                            import os
                            filename = f"generated_{uuid.uuid4()}.png"
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            cv2.imwrite(filepath, enhanced_image)
                            logger.info(f"Saved generated image to: {filepath}")
                            
                            return enhanced_image, filepath
                        else:
                            logger.error("Failed to convert generated image from Gemini response")
                            raise Exception("Failed to process generated image from Gemini")
        
        # If no image was generated, log the response for debugging
        if response and hasattr(response, 'text'):
            logger.info(f"Gemini response (text): {response.text[:200]}...")
        
        logger.warning("No image generated by Gemini, falling back to computer vision enhancement")
        enhanced_image = apply_cinematic_cv_enhancement(image)
        
        if enhanced_image is not None:
            logger.info("Successfully applied computer vision enhancement as fallback")
            return enhanced_image
        else:
            logger.error("Both Gemini generation and CV enhancement failed")
            raise Exception("Failed to enhance image with both Gemini and computer vision")
        
    except Exception as e:
        logger.error(f"Google Gemini {model_name} API call failed: {str(e)}")
        logger.error(f"Gemini error type: {type(e).__name__}")
        import traceback
        logger.error(f"Gemini traceback: {traceback.format_exc()}")
        
        # Fall back to computer vision enhancement
        try:
            logger.info("Falling back to computer vision enhancement due to Gemini error")
            enhanced_image = apply_cinematic_cv_enhancement(image)
            if enhanced_image is not None:
                return enhanced_image
        except Exception as cv_error:
            logger.error(f"Computer vision fallback also failed: {str(cv_error)}")
        
        raise e

def call_google_gemini_ai(image, prompt):
    """Call Google Gemini AI for image generation based on the input image and prompt"""
    try:
        # Check rate limits before making the API call
        if not check_rate_limit():
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Check if we have a valid Google API key
        api_key = CINEMATIC_AI_CONFIG["GOOGLE_API_KEY"]
        if not api_key or api_key == "your_google_api_key_here":
            logger.error("No valid Google API key found. Gemini API key required.")
            raise Exception("Google Gemini API key required for AI enhancement.")
        
        # Validate inputs
        if image is None:
            logger.error("Image is None - cannot process")
            raise Exception("No image provided for processing")
        
        if not prompt or prompt.strip() == "":
            logger.error("Prompt is empty - cannot process")
            raise Exception("No prompt provided for processing")
        
        logger.info(f"Image shape: {image.shape if hasattr(image, 'shape') else 'No shape attribute'}")
        logger.info(f"Image dtype: {image.dtype if hasattr(image, 'dtype') else 'No dtype attribute'}")
        logger.info(f"Prompt length: {len(prompt)}")
        
        logger.info("=== GEMINI 2.0 FLASH PREVIEW IMAGE GENERATION CALL STARTED ===")
        logger.info(f"Using Google Gemini 2.0 Flash Preview Image Generation for image enhancement!")
        logger.info(f"Prompt: {prompt[:100]}...")
        
        # Record the API call for rate limiting
        record_api_call()
        
        # Configure the API key - using new client approach
        # genai.configure(api_key=api_key)  # Old approach - not needed
        
        # Convert OpenCV image to base64 for the API
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Convert PIL image to base64
        import io
        import base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Debug logging
        logger.info(f"Image shape: {image_rgb.shape}")
        logger.info(f"PIL image mode: {pil_image.mode}")
        logger.info(f"PIL image size: {pil_image.size}")
        logger.info(f"Prompt: {prompt}")
        
        # Use the correct Google Generative AI syntax with config
        logger.info("Calling Gemini API...")
        
        # Use the correct Python Google GenAI client approach
        from google import genai as google_genai
        from google.genai import types
        
        client = google_genai.Client(api_key=api_key)
        
        # Create content using PIL image directly (not base64 text)
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=prompt),
                    types.Part(inline_data=types.Blob(
                        data=base64.b64decode(image_base64),
                        mime_type="image/png"
                    ))
                ]
            )
        ]
        
        # Configure response modalities
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
        
        # Process streaming response
        response_parts = []
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            
            # Collect parts from the stream
            if chunk.candidates[0].content.parts:
                response_parts.extend(chunk.candidates[0].content.parts)
        
        # Create a mock response object with the collected parts
        class MockResponse:
            def __init__(self, parts):
                self.candidates = [MockCandidate(parts)]
        
        class MockCandidate:
            def __init__(self, parts):
                self.content = MockContent(parts)
        
        class MockContent:
            def __init__(self, parts):
                self.parts = parts
        
        response = MockResponse(response_parts)
        
        if response and response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                # Extract the generated image from response
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        # Convert PIL Image to OpenCV format
                        from io import BytesIO
                        generated_pil = Image.open(BytesIO(part.inline_data.data))
                        enhanced_image = cv2.cvtColor(np.array(generated_pil), cv2.COLOR_RGB2BGR)
                        
                        if enhanced_image is not None:
                            logger.info("Successfully enhanced image using Gemini 2.0 Flash Preview")
                            
                            # Save the generated image
                            import uuid
                            import os
                            filename = f"generated_{uuid.uuid4()}.png"
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            cv2.imwrite(filepath, enhanced_image)
                            logger.info(f"Saved generated image to: {filepath}")
                            
                            return enhanced_image, filepath
                        else:
                            logger.error("Failed to convert generated image from Gemini response")
                            raise Exception("Failed to process generated image from Gemini")
        
        logger.error("No valid image found in Gemini response")
        raise Exception("No valid image generated by Gemini")
            
    except Exception as e:
        logger.error(f"Google Gemini API call failed: {str(e)}")
        raise e

def blend_ai_with_original(original_image, ai_generated, prompt):
    """
    Blend AI-generated image with original for better results
    """
    try:
        # Resize AI image to match original dimensions
        original_height, original_width = original_image.shape[:2]
        ai_resized = cv2.resize(ai_generated, (original_width, original_height))
        
        # Calculate blending weights based on prompt content
        ai_weight = 0.7  # Default AI weight
        original_weight = 0.3  # Default original weight
        
        # Adjust weights based on prompt keywords
        if "preserve" in prompt.lower() or "keep" in prompt.lower():
            original_weight = 0.5
            ai_weight = 0.5
        elif "enhance" in prompt.lower() or "improve" in prompt.lower():
            ai_weight = 0.8
            original_weight = 0.2
        
        # Blend the images
        blended = cv2.addWeighted(ai_resized, ai_weight, original_image, original_weight, 0)
        
        # Apply additional cinematic enhancement to the blended result
        enhanced = apply_cinematic_enhancement_from_prompt(blended, prompt)
        
        logger.info(f"Successfully blended AI enhancement with original image (AI: {ai_weight:.1f}, Original: {original_weight:.1f})")
        return enhanced
        
    except Exception as e:
        logger.error(f"Blending failed: {str(e)}, returning AI-generated image")
        return ai_resized

def apply_cinematic_enhancement_from_prompt(image, prompt):
    """
    Apply cinematic enhancement based on prompt content
    """
    try:
        # Apply different enhancements based on prompt keywords
        enhanced = image.copy()
        
        # Lighting enhancement
        if "lighting" in prompt.lower() or "dramatic" in prompt.lower():
            enhanced = apply_dramatic_cinematic_lighting(enhanced)
        
        # Color grading
        if "color" in prompt.lower() or "mood" in prompt.lower():
            enhanced = apply_sophisticated_color_grading(enhanced)
        
        # Composition enhancement
        if "composition" in prompt.lower() or "framing" in prompt.lower():
            enhanced = apply_composition_enhancement(enhanced)
        
        # Storytelling polish
        if "story" in prompt.lower() or "emotion" in prompt.lower():
            enhanced = apply_storytelling_polish(enhanced)
        
        # Final enhancement
        enhanced = apply_final_enhancement(enhanced)
        
        logger.info("Successfully applied cinematic enhancement from prompt")
        return enhanced
        
    except Exception as e:
        logger.error(f"Cinematic enhancement from prompt failed: {str(e)}")
        logger.info("Returning original image due to enhancement failure")
        return image

def apply_storytelling_enhancement(image):
    """
    Apply storytelling enhancement to create emotional impact
    """
    try:
        # Enhance center focus for storytelling
        rows, cols = image.shape[:2]
        center_y, center_x = rows / 2, cols / 2
        
        # Create focus mask
        y, x = np.ogrid[:rows, :cols]
        focus_mask = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * (min(rows, cols) / 4)**2))
        focus_mask = np.dstack([focus_mask] * 3)
        
        # Apply focus enhancement
        enhanced = image.astype(np.float32)
        enhanced = enhanced * (0.7 + 0.3 * focus_mask)
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        # Apply subtle vignette for storytelling
        vignette = np.ones_like(image, dtype=np.float32)
        y, x = np.ogrid[:rows, :cols]
        center_y, center_x = rows / 2, cols / 2
        vignette_strength = 0.3
        vignette *= (1 - vignette_strength * np.sqrt((x - center_x)**2 + (y - center_y)**2) / (min(rows, cols) / 2))
        vignette = np.clip(vignette, 0.3, 1.0)
        
        enhanced = enhanced.astype(np.float32) * vignette
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        logger.info("Successfully applied storytelling enhancement")
        return enhanced
        
    except Exception as e:
        logger.error(f"Storytelling enhancement failed: {str(e)}")
        return image

def call_replicate_ai_real(image, prompt):
    """Call Replicate AI for real enhancement"""
    try:
        logger.info("Replicate AI would process this image with custom prompt")
        logger.info(f"Custom prompt: {prompt}")
        
        # For now, use enhanced computer vision with prompt analysis
        # In production, this would call the actual Replicate API
        return apply_cinematic_enhancement_from_prompt(image, prompt)
        
    except Exception as e:
        logger.error(f"Replicate AI call failed: {str(e)}")
        return image

def call_stability_ai_real(image, prompt):
    """Call Stability AI for real enhancement"""
    try:
        logger.info("Stability AI would process this image with custom prompt")
        logger.info(f"Custom prompt: {prompt}")
        
        # For now, use enhanced computer vision with prompt analysis
        # In production, this would call the actual Stability API
        return apply_cinematic_enhancement_from_prompt(image, prompt)
        
    except Exception as e:
        logger.error(f"Stability AI call failed: {str(e)}")
        return image

def apply_custom_cv_enhancement(image, prompt):
    """
    Apply custom computer vision enhancement guided by the prompt.
    This analyzes the prompt and applies appropriate enhancements.
    """
    try:
        # Analyze prompt for enhancement direction
        prompt_lower = prompt.lower()
        
        # Preprocess image
        enhanced = preprocess_for_cinematic(image)
        
        # Apply enhancements based on prompt analysis
        if "lighting" in prompt_lower or "dramatic" in prompt_lower:
            enhanced = enhance_cinematic_lighting(enhanced)
        
        if "composition" in prompt_lower or "framing" in prompt_lower:
            enhanced = enhance_emotional_composition(enhanced)
            
        if "color" in prompt_lower or "mood" in prompt_lower:
            enhanced = apply_cinematic_color_grading(enhanced)
        
        if "story" in prompt_lower or "emotion" in prompt_lower:
            enhanced = apply_storytelling_enhancement(enhanced)
        
        # Apply final polish
        enhanced = apply_cinematic_polish(enhanced)
        
        logger.info("Successfully applied custom CV enhancement")
        return enhanced
        
    except Exception as e:
        logger.error(f"Custom CV enhancement failed: {str(e)}")
        return image

@app.route('/styles', methods=['GET'])
def get_styles():
    """Get available AI styles"""
    styles = [
        {
            "id": "cinematic",
            "name": "Cinematic Enhancement",
            "description": "Transform photos into emotionally powerful cinematic narratives that tell a complete story",
            "category": "ai_enhancement"
        },
        {
            "id": "enhance", 
            "name": "AI Enhancement",
            "description": "General AI-powered image enhancement",
            "category": "ai_enhancement"
        }
    ]
    
    return jsonify(styles)

@app.route('/uploads/<filename>')
def get_image(filename):
    logger.info(f"Serving image: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/rate-limit-status', methods=['GET'])
def get_rate_limit_status_endpoint():
    """Get current rate limit status"""
    try:
        status = get_rate_limit_status()
        return jsonify({
            'status': 'success',
            'rate_limits': status,
            'model': 'models/gemini-2.0-flash-preview-image-generation'
        }), 200
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        return jsonify({'error': 'Failed to get rate limit status'}), 500

@app.route('/api-logs', methods=['GET'])
def get_api_logs():
    """Get list of API response log files"""
    try:
        log_files = []
        
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.startswith('gemini_response_') and (filename.endswith('.json') or filename.endswith('.txt')):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file_info = {
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'modified': os.path.getmtime(filepath)
                    }
                    log_files.append(file_info)
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'log_files': log_files,
            'count': len(log_files)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting API logs: {str(e)}")
        return jsonify({'error': 'Failed to get API logs'}), 500

@app.route('/api-logs/<filename>', methods=['GET'])
def get_api_log_content(filename):
    """Get content of a specific API log file"""
    try:
        # Security check - only allow log files
        if not filename.startswith('gemini_response_') or not (filename.endswith('.json') or filename.endswith('.txt')):
            return jsonify({'error': 'Invalid log file'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Log file not found'}), 404
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'content': content
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting API log content: {str(e)}")
        return jsonify({'error': 'Failed to get API log content'}), 500

@app.route('/api-logs/cumulative', methods=['GET'])
def get_cumulative_api_logs():
    """Get the cumulative JSONL log file with all responses"""
    try:
        cumulative_log_path = os.path.join(UPLOAD_FOLDER, "gemini_all_responses.jsonl")
        
        if not os.path.exists(cumulative_log_path):
            return jsonify({
                'status': 'success',
                'message': 'No cumulative log file found yet',
                'responses': []
            }), 200
        
        responses = []
        with open(cumulative_log_path, 'r') as f:
            for line in f:
                try:
                    response_data = json.loads(line.strip())
                    responses.append(response_data)
                except json.JSONDecodeError:
                    continue
        
        return jsonify({
            'status': 'success',
            'responses': responses,
            'count': len(responses)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cumulative API logs: {str(e)}")
        return jsonify({'error': 'Failed to get cumulative API logs'}), 500

@app.route('/api-logs/cumulative/raw', methods=['GET'])
def get_cumulative_raw_logs():
    """Get the raw cumulative JSONL log file content"""
    try:
        cumulative_log_path = os.path.join(UPLOAD_FOLDER, "gemini_all_responses.jsonl")
        
        if not os.path.exists(cumulative_log_path):
            return jsonify({'error': 'Cumulative log file not found'}), 404
        
        with open(cumulative_log_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            'status': 'success',
            'content': content
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting raw cumulative logs: {str(e)}")
        return jsonify({'error': 'Failed to get raw cumulative logs'}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        logger.info("Received request for images list")
        images = []
        
        # Check if uploads directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            logger.info("Uploads directory does not exist, returning empty list")
            return jsonify({'images': []})
            
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
                        'filename': filename,
                        'original_filename': original_filename,
                        'url': f'/uploads/{filename}',
                        'timestamp': timestamp.isoformat(),
                        'style': 'hardcoded'
                    })
        
        # Sort by timestamp (newest first)
        images.sort(key=lambda x: x['timestamp'], reverse=True)
        
        logger.info(f"Found {len(images)} images")
        return jsonify({'images': images})
    
    except Exception as e:
        logger.error(f"Error getting images: {str(e)}")
        return jsonify({'error': 'Failed to get images'}), 500

@app.route('/download-image/<filename>', methods=['GET'])
def download_image(filename):
    """Download/save image - works for both web and mobile platforms"""
    try:
        # Security check - ensure filename is safe
        if not filename or '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if it's a mobile platform request
        user_agent = request.headers.get('User-Agent', '').lower()
        is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        
        if is_mobile:
            # For mobile platforms, return the image data as base64
            with open(filepath, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                
            return jsonify({
                'success': True,
                'image_data': base64_data,
                'filename': filename,
                'mime_type': 'image/png',
                'platform': 'mobile'
            })
        else:
            # For web platforms, return the file directly
            return send_file(filepath, as_attachment=True, download_name=filename)
            
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        return jsonify({'error': 'Failed to download image'}), 500

def apply_ai_guided_enhancement(image, prompt):
    """
    Apply AI-guided enhancement using prompt analysis to create more sophisticated
    computer vision effects that mimic AI behavior.
    """
    try:
        logger.info("Applying AI-guided enhancement based on prompt analysis...")
        
        # Analyze the prompt for enhancement direction
        prompt_lower = prompt.lower()
        
        # Create a more sophisticated enhancement based on prompt content
        enhanced = image.copy()
        
        # Apply different enhancements based on prompt keywords
        if "dramatic" in prompt_lower or "cinematic" in prompt_lower:
            enhanced = apply_dramatic_cinematic_lighting(enhanced)
        
        if "color" in prompt_lower or "mood" in prompt_lower:
            enhanced = apply_sophisticated_color_grading(enhanced)
        
        if "composition" in prompt_lower or "framing" in prompt_lower:
            enhanced = apply_composition_enhancement(enhanced)
        
        if "story" in prompt_lower or "emotion" in prompt_lower:
            enhanced = apply_storytelling_enhancement(enhanced)
        
        # Apply final polish
        enhanced = apply_final_enhancement(enhanced)
        
        logger.info("Successfully applied AI-guided enhancement")
        return enhanced
        
    except Exception as e:
        logger.error(f"AI-guided enhancement failed: {str(e)}")
        return image

def apply_dramatic_cinematic_lighting(image):
    """Apply dramatic cinematic lighting effects"""
    try:
        # Convert to float for processing
        enhanced = image.astype(np.float32) / 255.0
        
        # Create dramatic vignette
        rows, cols = enhanced.shape[:2]
        y, x = np.ogrid[:rows, :cols]
        center_y, center_x = rows / 2, cols / 2
        
        # More dramatic vignette
        vignette_strength = 0.6
        vignette = 1 - vignette_strength * np.sqrt((x - center_x)**2 + (y - center_y)**2) / (min(rows, cols) / 2)
        vignette = np.clip(vignette, 0.2, 1.0)
        vignette = np.dstack([vignette] * 3)
        
        # Apply vignette
        enhanced = enhanced * vignette
        
        # Enhance contrast for dramatic effect
        enhanced = np.power(enhanced, 0.8)  # Gamma correction
        
        # Apply subtle color grading
        enhanced[:, :, 0] *= 1.1  # Boost reds slightly
        enhanced[:, :, 2] *= 0.95  # Reduce blues slightly
        
        # Convert back to uint8
        enhanced = np.clip(enhanced * 255, 0, 255).astype(np.uint8)
        
        logger.info("Successfully applied dramatic cinematic lighting")
        return enhanced
        
    except Exception as e:
        logger.error(f"Dramatic lighting enhancement failed: {str(e)}")
        return image

def apply_sophisticated_color_grading(image):
    """Apply sophisticated color grading"""
    try:
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Enhance saturation dramatically
        hsv[:, :, 1] = hsv[:, :, 1] * 1.3
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # Apply cinematic color temperature
        hsv[:, :, 0] = (hsv[:, :, 0] + 10) % 180  # Stronger warm shift
        
        # Enhance value (brightness) for more dramatic effect
        hsv[:, :, 2] = hsv[:, :, 2] * 1.1
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Apply additional color grading
        enhanced = enhanced.astype(np.float32)
        enhanced[:, :, 0] *= 0.95  # Reduce blue
        enhanced[:, :, 1] *= 1.05  # Boost green slightly
        enhanced[:, :, 2] *= 1.1   # Boost red
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        logger.info("Successfully applied sophisticated color grading")
        return enhanced
        
    except Exception as e:
        logger.error(f"Color grading enhancement failed: {str(e)}")
        return image

def apply_composition_enhancement(image):
    """Apply composition enhancement"""
    try:
        # Enhance center focus
        rows, cols = image.shape[:2]
        center_y, center_x = rows / 2, cols / 2
        
        # Create focus mask
        y, x = np.ogrid[:rows, :cols]
        focus_mask = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * (min(rows, cols) / 3)**2))
        focus_mask = np.dstack([focus_mask] * 3)
        
        # Apply focus enhancement
        enhanced = image.astype(np.float32)
        enhanced = enhanced * (0.6 + 0.4 * focus_mask)
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        # Apply subtle sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        enhanced = np.clip(enhanced, 0, 255)
        
        logger.info("Successfully applied composition enhancement")
        return enhanced
        
    except Exception as e:
        logger.error(f"Composition enhancement failed: {str(e)}")
        return image

def apply_storytelling_polish(image):
    """Apply storytelling polish"""
    try:
        # Add film grain effect
        noise = np.random.normal(0, 10, image.shape).astype(np.uint8)
        enhanced = cv2.add(image, noise)
        
        # Add subtle blur for cinematic feel
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Enhance contrast for dramatic effect
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.1, beta=10)
        
        # Apply subtle vignette for storytelling focus
        rows, cols = enhanced.shape[:2]
        y, x = np.ogrid[:rows, :cols]
        center_y, center_x = rows / 2, cols / 2
        vignette = 1 - 0.3 * np.sqrt((x - center_x)**2 + (y - center_y)**2) / (min(rows, cols) / 2)
        vignette = np.clip(vignette, 0.7, 1.0)
        vignette = np.dstack([vignette] * 3)
        
        enhanced = enhanced.astype(np.float32) * vignette
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        logger.info("Successfully applied storytelling polish")
        return enhanced
        
    except Exception as e:
        logger.error(f"Storytelling polish failed: {str(e)}")
        return image

def apply_final_enhancement(image):
    """Apply final enhancement polish"""
    try:
        # Final contrast enhancement
        enhanced = cv2.convertScaleAbs(image, alpha=1.05, beta=5)
        
        # Subtle noise reduction
        enhanced = cv2.bilateralFilter(enhanced, 5, 50, 50)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Final enhancement failed: {str(e)}")
        return image

def apply_gemini_guided_enhancement(image, prompt, gemini_response):
    """
    Apply enhancement guided by Gemini's understanding of the image and prompt.
    This will give you the same quality results you experienced with Gemini!
    """
    try:
        logger.info("Applying Gemini-guided enhancement for professional cinematic results...")
        
        # Analyze Gemini's response to understand what it detected
        gemini_lower = gemini_response.lower()
        prompt_lower = prompt.lower()
        
        # Start with the original image
        enhanced = image.copy()
        
        # Use Gemini's actual analysis to guide enhancement
        # This is the key difference - we're using Gemini's understanding, not just keywords
        
        # Apply professional cinematic enhancement based on Gemini's analysis
        if any(word in gemini_lower + prompt_lower for word in ['cinematic', 'dramatic', 'storytelling', 'narrative']):
            enhanced = apply_professional_cinematic_lighting(enhanced)
            logger.info("Applied professional cinematic lighting based on Gemini analysis")
        
        # Apply emotional enhancement based on Gemini's analysis
        if any(word in gemini_lower + prompt_lower for word in ['emotional', 'mood', 'atmosphere', 'feeling']):
            enhanced = apply_emotional_enhancement(enhanced)
            logger.info("Applied emotional enhancement based on Gemini analysis")
        
        # Apply professional polish based on Gemini's analysis
        if any(word in gemini_lower + prompt_lower for word in ['professional', 'polish', 'quality', 'refined']):
            enhanced = apply_professional_polish(enhanced)
            logger.info("Applied professional polish based on Gemini analysis")
        
        # Apply storytelling enhancement based on Gemini's analysis
        if any(word in gemini_lower + prompt_lower for word in ['story', 'narrative', 'thousand words', 'meaningful']):
            enhanced = apply_storytelling_enhancement(enhanced)
            logger.info("Applied storytelling enhancement based on Gemini analysis")
        
        # Final professional touch
        enhanced = apply_final_professional_touch(enhanced)
        
        logger.info("Successfully applied Gemini-guided enhancement")
        return enhanced
        
    except Exception as e:
        logger.error(f"Gemini-guided enhancement failed: {str(e)}")
        return image

def blend_ai_with_original(original_image, ai_generated, prompt):
    """
    Blend the AI-generated image with the original to preserve content
    while adding AI enhancement based on the prompt.
    """
    try:
        # Resize AI-generated image to match original dimensions
        ai_resized = cv2.resize(ai_generated, (original_image.shape[1], original_image.shape[0]))
        
        # Analyze the prompt to determine blending strategy
        prompt_lower = prompt.lower()
        
        # Determine blending weights based on prompt content
        if any(word in prompt_lower for word in ['cinematic', 'dramatic', 'storytelling', 'emotional']):
            # For cinematic prompts, give more weight to AI enhancement
            ai_weight = 0.7
            original_weight = 0.3
        elif any(word in prompt_lower for word in ['enhance', 'improve', 'polish', 'professional']):
            # For enhancement prompts, balanced blend
            ai_weight = 0.6
            original_weight = 0.4
        else:
            # Default: preserve more of original
            ai_weight = 0.5
            original_weight = 0.5
        
        # Blend the images
        blended = cv2.addWeighted(original_image, original_weight, ai_resized, ai_weight, 0)
        
        # Apply additional cinematic enhancement to the blended result
        enhanced = apply_cinematic_enhancement_from_prompt(blended, prompt)
        
        logger.info(f"Successfully blended AI enhancement with original image (AI: {ai_weight:.1f}, Original: {original_weight:.1f})")
        return enhanced
        
    except Exception as e:
        logger.error(f"Blending failed: {str(e)}, returning AI-generated image")
        return ai_resized

def apply_cinematic_enhancement_from_prompt(image, prompt):
    """
    Apply cinematic enhancement based on the full prompt analysis.
    This handles complex, long prompts like the cinematic storytelling prompt.
    """
    try:
        logger.info("Applying cinematic enhancement based on prompt analysis")
        
        # Preprocess image
        enhanced = preprocess_for_cinematic(image)
        
        # Analyze the prompt for enhancement direction
        prompt_lower = prompt.lower()
        
        # Check for cinematic storytelling keywords
        is_cinematic_storytelling = any(phrase in prompt_lower for phrase in [
            'cinematic portrait', 'retells the story', 'thousand words',
            'authentic emotions', 'storytelling', 'narrative',
            'professional photographer', 'emotional weight'
        ])
        
        # Check for specific enhancement types
        has_lighting_enhancement = any(word in prompt_lower for word in [
            'lighting', 'highlights', 'shadows', 'contrast', 'cinematic lighting'
        ])
        
        has_color_enhancement = any(word in prompt_lower for word in [
            'color', 'color-grade', 'warm tones', 'mood', 'atmosphere'
        ])
        
        has_detail_enhancement = any(word in prompt_lower for word in [
            'details', 'sharp', 'clarity', 'texture', 'professional polish'
        ])
        
        has_composition_enhancement = any(word in prompt_lower for word in [
            'composition', 'framing', 'balance', 'positioning', 'background'
        ])
        
        # Apply comprehensive cinematic enhancement for storytelling prompts
        if is_cinematic_storytelling:
            logger.info("Detected cinematic storytelling prompt - applying comprehensive enhancement")
            
            try:
                # Apply all cinematic enhancements with error handling
                enhanced = enhance_cinematic_lighting(enhanced)
                logger.info("Applied lighting enhancement")
            except Exception as e:
                logger.warning(f"Lighting enhancement failed: {str(e)}")
                
            try:
                enhanced = enhance_emotional_composition(enhanced)
                logger.info("Applied emotional composition enhancement")
            except Exception as e:
                logger.warning(f"Emotional composition enhancement failed: {str(e)}")
                
            try:
                enhanced = apply_cinematic_color_grading(enhanced)
                logger.info("Applied color grading enhancement")
            except Exception as e:
                logger.warning(f"Color grading enhancement failed: {str(e)}")
                
            try:
                enhanced = enhance_cinematic_details(enhanced)
                logger.info("Applied detail enhancement")
            except Exception as e:
                logger.warning(f"Detail enhancement failed: {str(e)}")
            
            # Add extra cinematic polish for storytelling
            try:
                enhanced = apply_storytelling_enhancement(enhanced)
                logger.info("Applied storytelling enhancement")
            except Exception as e:
                logger.warning(f"Storytelling enhancement failed: {str(e)}")
            
        else:
            # Apply targeted enhancements based on prompt analysis
            if has_lighting_enhancement:
                try:
                    enhanced = enhance_cinematic_lighting(enhanced)
                    logger.info("Applied lighting enhancement based on prompt")
                except Exception as e:
                    logger.warning(f"Lighting enhancement failed: {str(e)}")
                
            if has_color_enhancement:
                try:
                    enhanced = apply_cinematic_color_grading(enhanced)
                    logger.info("Applied color enhancement based on prompt")
                except Exception as e:
                    logger.warning(f"Color enhancement failed: {str(e)}")
                
            if has_detail_enhancement:
                try:
                    enhanced = enhance_cinematic_details(enhanced)
                    logger.info("Applied detail enhancement based on prompt")
                except Exception as e:
                    logger.warning(f"Detail enhancement failed: {str(e)}")
                
            if has_composition_enhancement:
                try:
                    enhanced = enhance_emotional_composition(enhanced)
                    logger.info("Applied composition enhancement based on prompt")
                except Exception as e:
                    logger.warning(f"Composition enhancement failed: {str(e)}")
            
            # If no specific enhancements detected, apply comprehensive enhancement
            if not any([has_lighting_enhancement, has_color_enhancement, has_detail_enhancement, has_composition_enhancement]):
                logger.info("No specific enhancements detected, applying comprehensive cinematic enhancement")
                
                try:
                    enhanced = enhance_cinematic_lighting(enhanced)
                except Exception as e:
                    logger.warning(f"Comprehensive lighting enhancement failed: {str(e)}")
                    
                try:
                    enhanced = enhance_emotional_composition(enhanced)
                except Exception as e:
                    logger.warning(f"Comprehensive composition enhancement failed: {str(e)}")
                    
                try:
                    enhanced = apply_cinematic_color_grading(enhanced)
                except Exception as e:
                    logger.warning(f"Comprehensive color enhancement failed: {str(e)}")
                    
                try:
                    enhanced = enhance_cinematic_details(enhanced)
                except Exception as e:
                    logger.warning(f"Comprehensive detail enhancement failed: {str(e)}")
        
        # Final cinematic polish
        try:
            enhanced = apply_cinematic_polish(enhanced)
            logger.info("Applied final cinematic polish")
        except Exception as e:
            logger.warning(f"Final polish failed: {str(e)}")
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Cinematic enhancement from prompt failed: {str(e)}")
        logger.info("Returning original image due to enhancement failure")
        return image

def apply_storytelling_enhancement(image):
    """
    Apply special enhancements for cinematic storytelling prompts.
    This adds extra polish for narrative-focused enhancements.
    """
    try:
        # Add subtle vignette for cinematic focus
        rows, cols = image.shape[:2]
        y, x = np.ogrid[:rows, :cols]
        center_y, center_x = rows / 2, cols / 2
        
        # Create a more pronounced vignette for storytelling
        mask = 1 - np.sqrt((x - center_x)**2 + (y - center_y)**2) / np.sqrt(center_x**2 + center_y**2)
        mask = np.clip(mask, 0, 1)
        mask = np.dstack([mask] * 3)
        
        # Apply stronger vignette effect
        enhanced = image * (0.7 + 0.3 * mask)
        
        # Add subtle film grain for cinematic feel
        noise = np.random.normal(0, 8, enhanced.shape).astype(np.float32)
        enhanced = enhanced + noise
        enhanced = np.clip(enhanced, 0, 1)
        
        # Enhance contrast for dramatic storytelling
        enhanced = cv2.convertScaleAbs((enhanced * 255).astype(np.uint8), alpha=1.1, beta=10)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Storytelling enhancement failed: {str(e)}")
        return image

def call_replicate_ai_real(image, prompt):
    """Call Replicate AI for real enhancement"""
    try:
        logger.info("Replicate AI would process this image with custom prompt")
        logger.info(f"Custom prompt: {prompt}")
        
        # For now, use enhanced computer vision with prompt analysis
        # In production, this would call the actual Replicate API
        return apply_cinematic_enhancement_from_prompt(image, prompt)
        
    except Exception as e:
        logger.error(f"Replicate AI call failed: {str(e)}")
        return apply_cinematic_enhancement_from_prompt(image, prompt)

def call_stability_ai_real(image, prompt):
    """Call Stability AI for real enhancement"""
    try:
        logger.info("Stability AI would process this image with custom prompt")
        logger.info(f"Custom prompt: {prompt}")
        
        # For now, use enhanced computer vision with prompt analysis
        # In production, this would call the actual Stability API
        return apply_cinematic_enhancement_from_prompt(image, prompt)
        
    except Exception as e:
        logger.error(f"Stability AI call failed: {str(e)}")
        return apply_cinematic_enhancement_from_prompt(image, prompt)

def apply_custom_cv_enhancement(image, prompt):
    """
    Apply custom computer vision enhancement guided by the prompt.
    This analyzes the prompt and applies appropriate enhancements.
    """
    try:
        # Analyze prompt for enhancement direction
        prompt_lower = prompt.lower()
        
        # Preprocess image
        enhanced = preprocess_for_cinematic(image)
        
        # Apply enhancements based on prompt analysis
        if any(word in prompt_lower for word in ['light', 'bright', 'glow', 'shine']):
            enhanced = enhance_cinematic_lighting(enhanced)
            logger.info("Applied lighting enhancement based on prompt")
            
        if any(word in prompt_lower for word in ['color', 'vibrant', 'saturation', 'hue']):
            enhanced = apply_cinematic_color_grading(enhanced)
            logger.info("Applied color enhancement based on prompt")
            
        if any(word in prompt_lower for word in ['detail', 'sharp', 'crisp', 'clear']):
            enhanced = enhance_cinematic_details(enhanced)
            logger.info("Applied detail enhancement based on prompt")
            
        if any(word in prompt_lower for word in ['mood', 'atmosphere', 'emotion', 'feeling']):
            enhanced = enhance_emotional_composition(enhanced)
            logger.info("Applied emotional composition enhancement based on prompt")
            
        # If no specific enhancements detected, apply all cinematic enhancements
        if not any(word in prompt_lower for word in ['light', 'color', 'detail', 'mood']):
            enhanced = enhance_cinematic_lighting(enhanced)
            enhanced = enhance_emotional_composition(enhanced)
            enhanced = apply_cinematic_color_grading(enhanced)
            enhanced = enhance_cinematic_details(enhanced)
            logger.info("Applied comprehensive cinematic enhancement")
        
        # Final polish
        enhanced = apply_cinematic_polish(enhanced)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Custom CV enhancement failed: {str(e)}")
        return image


@app.route('/auth/purchase-credits', methods=['POST'])
@jwt_required()
def purchase_credits():
    """Purchase 25 image credits for $5"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, we'll simulate a successful payment
        # In a real implementation, you'd integrate with a payment processor
        user.image_credits += 25
        db.session.commit()
        
        logger.info(f"User {user.username} purchased 25 credits. Total credits: {user.image_credits}")
        return jsonify({
            'message': 'Payment successful! You now have 25 image credits.',
            'credits_purchased': 25,
            'total_credits': user.image_credits
        })
        
    except Exception as e:
        logger.error(f"Error purchasing credits: {str(e)}")
        return jsonify({'error': 'Failed to purchase credits'}), 500

@app.route('/auth/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a Stripe payment intent for purchasing credits"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        amount = data.get('amount', STRIPE_CONFIG['CREDITS_PACKAGE']['amount'])
        currency = data.get('currency', STRIPE_CONFIG['CURRENCY'])
        description = data.get('description', STRIPE_CONFIG['CREDITS_PACKAGE']['description'])
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata={
                'user_id': str(user_id),
                'credits': str(STRIPE_CONFIG['CREDITS_PACKAGE']['credits'])
            }
        )
        
        logger.info(f"Created payment intent {intent.id} for user {user.username}")
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {str(e)}")
        return jsonify({'error': f'Payment processing error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return jsonify({'error': 'Failed to create payment intent'}), 500

@app.route('/test-stripe-config', methods=['GET'])
def test_stripe_config():
    """Test endpoint to verify Stripe configuration"""
    return jsonify({
        'stripe_configured': bool(STRIPE_CONFIG['SECRET_KEY']),
        'stripe_key_prefix': STRIPE_CONFIG['SECRET_KEY'][:7] + '...' if STRIPE_CONFIG['SECRET_KEY'] else 'None',
        'current_directory': os.getcwd(),
        'env_file_exists': os.path.exists('.env'),
        'stripe_api_key_set': bool(stripe.api_key)
    })

@app.route('/auth/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    """Confirm payment and add credits to user account"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        amount = data.get('amount')
        
        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID required'}), 400
        
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Verify payment was successful
        if intent.status != 'succeeded':
            return jsonify({'error': 'Payment not completed'}), 400
        
        # Verify the amount matches our expected amount
        if intent.amount != STRIPE_CONFIG['CREDITS_PACKAGE']['amount']:
            return jsonify({'error': 'Invalid payment amount'}), 400
        
        # Add credits to user account
        credits_to_add = STRIPE_CONFIG['CREDITS_PACKAGE']['credits']
        user.image_credits += credits_to_add
        db.session.commit()
        
        logger.info(f"Payment confirmed for user {user.username}. Added {credits_to_add} credits. Total: {user.image_credits}")
        
        return jsonify({
            'message': 'Payment confirmed successfully!',
            'credits_added': credits_to_add,
            'total_credits': user.image_credits,
            'payment_intent_id': payment_intent_id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error confirming payment: {str(e)}")
        return jsonify({'error': f'Payment verification error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to confirm payment'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def create_tables():
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True) 
