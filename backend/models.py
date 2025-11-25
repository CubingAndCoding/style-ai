from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'  # Use 'users' instead of 'user' (which is a SQLite reserved word)
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_premium = db.Column(db.Boolean, default=False)
    
    # Usage tracking - image credits system
    image_credits = db.Column(db.Integer, default=0)  # Number of image processing credits
    free_trial_used = db.Column(db.Boolean, default=False)
    
    # Relationship to saved prompts
    saved_prompts = db.relationship('SavedPrompt', backref='user', lazy=True, cascade='all, delete-orphan')
    # Relationship to processed images
    processed_images = db.relationship('ProcessedImage', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'image_credits': self.image_credits,
            'free_trial_used': self.free_trial_used
        }

class SavedPrompt(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    style_type = db.Column(db.String(50), nullable=True)  # The style used (cinematic, sketch, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert saved prompt to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'prompt_text': self.prompt_text,
            'style_type': self.style_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_favorite': self.is_favorite
        }

class ProcessedImage(db.Model):
    __tablename__ = 'processed_image'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # The processed filename
    original_filename = db.Column(db.String(255), nullable=False)  # The original filename before processing
    style = db.Column(db.String(50), nullable=True)  # The style used (cinematic, sketch, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert processed image to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'url': f'/uploads/{self.filename}',
            'timestamp': self.created_at.isoformat(),
            'style': self.style
        }