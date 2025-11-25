# Gallery Changes: Per-User Galleries

## Problem
Previously, all users shared the same gallery - every account could see every uploaded image. This was a privacy and user experience issue.

## Solution
Now each account has its own personal gallery. Users only see images they've uploaded themselves.

## Changes Made

### 1. Database Model (`backend/models.py`)
**Added `ProcessedImage` model**:
```python
class ProcessedImage(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    style = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Updated `User` model** to include relationship:
```python
processed_images = db.relationship('ProcessedImage', backref='user', lazy=True, cascade='all, delete-orphan')
```

### 2. Backend API (`backend/app.py`)

#### `/upload` endpoint (lines 1399-1519)
- Now saves image metadata to database with `user_id`
- Creates a `ProcessedImage` record for each uploaded image
- Returns database ID instead of random UUID

#### `/images` endpoint (lines 2238-2257)
- Added `@jwt_required()` decorator - requires authentication
- Filters images by `user_id` from JWT token
- Returns only the authenticated user's images
- Uses database query instead of file system scanning

### 3. Frontend
- **No changes needed!** Already configured correctly
- Uses axios interceptors to send auth token
- GalleryPage checks authentication before loading

## Files Modified

1. `backend/models.py` - Added ProcessedImage model
2. `backend/app.py` - Updated upload and images endpoints
3. `backend/migrate_add_processed_images_table.py` - NEW: Migration script
4. `backend/GALLERY_PER_USER_MIGRATION.md` - NEW: Deployment guide

## How It Works

1. **User uploads image**:
   - Frontend sends image with JWT token
   - Backend extracts `user_id` from JWT
   - Image is processed and saved to `uploads/` folder
   - Metadata is saved to `processed_image` table with `user_id`

2. **User views gallery**:
   - Frontend requests `/images` with JWT token
   - Backend extracts `user_id` from JWT
   - Queries `processed_image` table filtering by `user_id`
   - Returns only that user's images

## Security
- JWT authentication required for both upload and viewing
- Users cannot access other users' images
- Database foreign key ensures data integrity
- Cascade delete removes images when user is deleted

## Migration Steps

1. Run the migration script:
```bash
cd backend
python migrate_add_processed_images_table.py
```

2. Restart the backend server

3. Test with multiple accounts to verify isolation

## Testing
- Create two different accounts
- Upload images from each account
- Verify each account only sees their own images
- Verify logout/login maintains correct gallery
















