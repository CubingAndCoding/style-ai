# Gallery Per-User Migration Guide

## Overview
This update changes the gallery system from a shared gallery to individual user galleries. Each user now only sees their own processed images.

## Changes Made

### 1. Database Model (models.py)
- Added `ProcessedImage` model with `user_id` foreign key
- Each image is now associated with a specific user
- Images are automatically deleted when a user is deleted (cascade)

### 2. Backend API Changes (app.py)
- **Modified `/upload` endpoint**: Now saves image metadata to database with `user_id`
- **Modified `/images` endpoint**: 
  - Now requires JWT authentication (@jwt_required())
  - Filters images by current user's ID
  - Returns only the authenticated user's images

### 3. Frontend Changes
- No changes needed! The frontend already uses axios interceptors to send auth tokens
- GalleryPage already checks for authentication before making requests

## Deployment Steps

### Step 1: Run Database Migration

```bash
cd backend
python migrate_add_processed_images_table.py
```

This will create the new `processed_image` table in your database.

### Step 2: Test the Changes

1. **Start the backend server**:
```bash
cd backend
python app.py
```

2. **Test the gallery**:
   - Create/Login to multiple user accounts
   - Upload images from different accounts
   - Verify each account only sees their own images

### Step 3: Migration from Old System (Optional)

If you have existing images from before this update, they won't show up in any user's gallery. You can:

1. **Option A**: Keep existing images as public/shared (not recommended)
2. **Option B**: Create a migration script to associate old images with users (if you have that data)
3. **Option C**: Leave old images orphaned (they won't appear in galleries)

### Step 4: Verify Database Schema

Check that the new table exists:
```sql
-- PostgreSQL
\d processed_image

-- Or SQLite
.schema processed_image
```

## Database Schema

### ProcessedImage Table
```sql
CREATE TABLE processed_image (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    style VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
```

## Testing Checklist

- [ ] Run migration script successfully
- [ ] Test creating a new account and uploading an image
- [ ] Verify the image appears in the uploader's gallery
- [ ] Create a second account and verify it has an empty gallery
- [ ] Upload an image from the second account
- [ ] Verify both accounts only see their own images
- [ ] Test logout/login to ensure gallery persists
- [ ] Test that old images (from before migration) don't appear

## Important Notes

1. **Old Images**: Images uploaded before this update will not appear in any user's gallery since they aren't in the database. They still exist in the `uploads/` folder but aren't associated with any user.

2. **File Cleanup**: The files in `uploads/` are not automatically deleted. Consider implementing a cleanup job if disk space becomes an issue.

3. **Authentication Required**: The `/images` endpoint now requires authentication. Unauthenticated requests will fail with a 401 Unauthorized error.

## Rollback (If Needed)

If you need to rollback these changes:

1. Remove `@jwt_required()` from the `/images` endpoint
2. Restore the old file-system-based gallery logic
3. The database table can remain as it won't break anything

However, note that any new images uploaded after migration will be in the database and won't appear with the old system.

## Future Enhancements

Consider adding:
- Delete image functionality
- Image metadata editing
- Bulk operations
- Image sharing between users (optional)
- Analytics on processed images
















