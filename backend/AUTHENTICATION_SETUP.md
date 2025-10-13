# Authentication Setup Guide

## Overview
The Style AI app now includes user authentication and prompt saving functionality. Users can create accounts, sign in, and save their enhancement prompts for future use.

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
# JWT Secret Key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# AI API Keys (Optional - for enhanced AI features)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
REPLICATE_API_KEY=your_replicate_api_key_here
STABILITY_API_KEY=your_stability_api_key_here
```

### 3. Start the Backend
```bash
python app.py
```

The database will be created automatically on first run.

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend/style-ai
npm install
```

### 2. Start the Frontend
```bash
npm run dev
```

## Features

### Authentication
- **User Registration**: Users can create accounts with username, email, and password
- **User Login**: Secure login with JWT tokens
- **Session Management**: Automatic token refresh and persistent sessions
- **Logout**: Secure logout with token cleanup

### Prompt Management
- **Save Prompts**: Users can save their custom enhancement prompts with titles
- **View Saved Prompts**: Browse all saved prompts in a dedicated gallery
- **Use Saved Prompts**: Load saved prompts back into the camera page
- **Favorites**: Mark prompts as favorites for quick access
- **Delete Prompts**: Remove prompts that are no longer needed

### User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Consistent dark theme throughout the app
- **Toast Notifications**: User feedback for all actions
- **Loading States**: Visual feedback during API calls

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Prompt Management
- `POST /prompts` - Save a new prompt
- `GET /prompts` - Get user's saved prompts
- `PUT /prompts/<id>` - Update a prompt
- `DELETE /prompts/<id>` - Delete a prompt

### Image Processing
- `POST /upload` - Upload and enhance image (now requires authentication)
- `GET /styles` - Get available enhancement styles
- `GET /uploads/<filename>` - Download enhanced images

## Database Schema

### Users Table
- `id` (String, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `password_hash` (String)
- `created_at` (DateTime)
- `is_active` (Boolean)

### Saved Prompts Table
- `id` (String, Primary Key)
- `user_id` (String, Foreign Key)
- `title` (String)
- `prompt_text` (Text)
- `style_type` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_favorite` (Boolean)

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with 7-day expiration
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configured for frontend-backend communication
- **SQL Injection Protection**: Uses SQLAlchemy ORM

## Usage

1. **First Time Users**:
   - Open the app and click the user icon in the top-right
   - Register a new account
   - Start creating and saving prompts

2. **Returning Users**:
   - Sign in with your credentials
   - Access your saved prompts from the "Saved" tab
   - Continue enhancing photos with your custom prompts

3. **Saving Prompts**:
   - Create a custom prompt in the camera page
   - Click the save icon (only visible when logged in)
   - Give your prompt a descriptive title
   - Access it later from the saved prompts page

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure the backend is running
   - Check that the database file has proper permissions

2. **Authentication Errors**:
   - Verify JWT_SECRET_KEY is set in .env
   - Check that tokens haven't expired

3. **CORS Errors**:
   - Ensure frontend is running on the correct port
   - Check backend CORS configuration

### Development Tips

- Use browser developer tools to inspect network requests
- Check backend logs for detailed error messages
- Test authentication flow step by step
- Verify database entries using a SQLite browser

## Production Considerations

- Change JWT_SECRET_KEY to a secure random string
- Use environment variables for all sensitive data
- Consider using PostgreSQL or MySQL for production
- Implement rate limiting for API endpoints
- Add input sanitization and validation
- Set up proper logging and monitoring
