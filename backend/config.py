import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Configuration
AI_CONFIG = {
    # Hugging Face API (for real AI models)
    "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
    "HUGGINGFACE_API_URL": "https://api-inference.huggingface.co",
    
    # Google Gemini API (for amazing cinematic enhancement)
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
    "GOOGLE_GEMINI_URL": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent",
    
    # OpenAI API (alternative AI service)
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_API_URL": "https://api.openai.com/v1",
    
    # Local AI models (if you want to run models locally)
    "USE_LOCAL_MODELS": os.getenv("USE_LOCAL_MODELS", "false").lower() == "true",
    "LOCAL_MODEL_PATH": os.getenv("LOCAL_MODEL_PATH", "./models"),
    
    # Model configurations
    "MODELS": {
        "sketch": {
            "provider": "huggingface",
            "model": "runwayml/stable-diffusion-v1-5",
            "prompt_template": "Convert this photo to a beautiful pencil sketch, artistic, detailed, high quality, black and white"
        },
        "cartoon": {
            "provider": "huggingface", 
            "model": "CompVis/stable-diffusion-v1-4",
            "prompt_template": "Transform this photo into a vibrant cartoon style, colorful, animated, professional, anime-inspired"
        },
        "oil_painting": {
            "provider": "huggingface",
            "model": "runwayml/stable-diffusion-v1-5", 
            "prompt_template": "Convert this photo to an oil painting masterpiece, artistic, textured, museum quality, Van Gogh style"
        },
        "watercolor": {
            "provider": "huggingface",
            "model": "CompVis/stable-diffusion-v1-4",
            "prompt_template": "Transform this photo into a beautiful watercolor painting, soft, artistic, flowing colors, impressionist"
        },
        "pencil_sketch": {
            "provider": "huggingface",
            "model": "runwayml/stable-diffusion-v1-5",
            "prompt_template": "Convert this photo to a detailed pencil sketch, black and white, artistic, clean lines, realistic"
        },
        "pop_art": {
            "provider": "huggingface",
            "model": "CompVis/stable-diffusion-v1-4",
            "prompt_template": "Transform this photo into pop art style, bold colors, Andy Warhol inspired, vibrant, comic book style"
        },
        "vintage": {
            "provider": "huggingface", 
            "model": "runwayml/stable-diffusion-v1-5",
            "prompt_template": "Convert this photo to vintage style, sepia tone, classic, nostalgic, film grain, 1950s aesthetic"
        },
        "neon": {
            "provider": "huggingface",
            "model": "CompVis/stable-diffusion-v1-4", 
            "prompt_template": "Transform this photo with neon glow effects, cyberpunk, glowing edges, futuristic, synthwave aesthetic"
        }
    }
}

# Fallback to advanced computer vision if no AI keys
def has_ai_access():
    """Check if we have access to AI services"""
    return bool(AI_CONFIG["HUGGINGFACE_API_KEY"] or AI_CONFIG["GOOGLE_API_KEY"] or AI_CONFIG["OPENAI_API_KEY"])

# Stripe Configuration
STRIPE_CONFIG = {
    "SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
    "WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
    "CURRENCY": "usd",
    "CREDITS_PACKAGE": {
        "amount": 500,  # $5.00 in cents
        "credits": 25,
        "description": "25 Image Credits - Style AI"
    }
}

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
