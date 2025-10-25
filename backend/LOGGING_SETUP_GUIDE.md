# Backend Logging Setup Guide

## Overview
I've set up comprehensive logging for your Flask backend to help debug API call issues. The logging system will now show you exactly what's happening with every request and response.

## What's Been Added

### 1. **Comprehensive Request/Response Logging**
- **Before Request**: Logs all incoming requests with:
  - Method, URL, path
  - Remote address and user agent
  - Headers (excluding sensitive ones)
  - Request data (JSON, form data, files)
  
- **After Request**: Logs all outgoing responses with:
  - Status code and content type
  - Response headers
  - Response data (truncated for large responses)

### 2. **Enhanced Authentication Endpoints**
- **Registration Endpoint**: Detailed step-by-step logging
- **Login Endpoint**: Comprehensive authentication flow logging
- **Error Handling**: Full traceback logging for all exceptions

### 3. **Server Startup Logging**
- Configuration details when server starts
- Database connection info
- Upload folder and limits

## How to Use

### 1. **Start the Backend Server**
```bash
cd backend
python app.py
```

You'll see detailed startup logs like:
```
🚀 STARTING STYLE AI BACKEND SERVER
================================================================================
🔧 Server Configuration:
   Host: 0.0.0.0
   Port: 5000
   Debug Mode: True
   Database: sqlite:///style_ai.db
   Upload Folder: uploads
   Max Content Length: 16777216
================================================================================
📡 Server is ready to receive requests!
================================================================================
```

### 2. **Test API Calls**
When you make API calls from your Android app, you'll see logs like:

**For Registration:**
```
================================================================================
🔵 INCOMING REQUEST
   Method: POST
   URL: http://localhost:5000/auth/register
   Path: /auth/register
   Remote Address: 127.0.0.1
   User Agent: Mozilla/5.0...
   Content Type: application/json
   Content Length: 89
   Headers: {'Content-Type': 'application/json', 'Accept': '*/*'}
   JSON Data: {'username': 'testuser', 'email': 'test@example.com', 'password': 'testpass123'}
================================================================================

🚀 REGISTRATION ENDPOINT CALLED
📝 Registration data received: {'username': 'testuser', 'email': 'test@example.com', 'password': 'testpass123'}
📋 Extracted fields - Username: testuser, Email: test@example.com, Password: ***
🔍 Checking if username 'testuser' already exists...
🔍 Checking if email 'test@example.com' already exists...
👤 Creating new user...
💾 Adding user to database...
🔑 Creating access token...
✅ New user registered successfully: testuser (ID: abc123)
📤 Sending response: {'message': 'User registered successfully', 'access_token': '...', 'user': {...}}
================================================================================
🟢 OUTGOING RESPONSE
   Status Code: 201
   Content Type: application/json
   Content Length: 245
   Headers: {'Content-Type': 'application/json'}
   JSON Response: {'message': 'User registered successfully', 'access_token': '...', 'user': {...}}
================================================================================
```

### 3. **Test the Logging**
I've created a test script to verify the logging works:

```bash
cd backend
python test_logging.py
```

This will:
- Test registration endpoint
- Test login endpoint  
- Test duplicate registration (should fail)
- Test invalid login (should fail)
- Show you exactly what the backend logs

### 4. **Debug Your Android App**
1. **Start the backend server** (with logging enabled)
2. **Run your Android app** (`npx cap open android`)
3. **Try to register** with a new username/email
4. **Check the backend console** - you'll see exactly what's happening

## What to Look For

### ✅ **If API calls are reaching the backend:**
- You'll see the "🔵 INCOMING REQUEST" logs
- You'll see the "🚀 REGISTRATION ENDPOINT CALLED" logs
- You'll see step-by-step processing logs

### ❌ **If API calls are NOT reaching the backend:**
- You won't see any logs when you try to register
- This means the issue is with network connectivity or Android configuration

### 🔍 **Common Issues to Check:**

1. **Network Connectivity**
   - Check if the API URL is correct
   - Verify the backend is running
   - Check Android network security config

2. **CORS Issues**
   - Backend allows all origins, so this shouldn't be the issue

3. **Request Format**
   - Check if the request data is being sent correctly
   - Verify Content-Type headers

4. **Database Issues**
   - Check if the database is accessible
   - Look for database connection errors in logs

## Environment Variables

Make sure your backend has these environment variables set:
```env
LOG_LEVEL=DEBUG
FLASK_ENV=development
DEBUG=true
```

## Next Steps

1. **Start the backend** with the new logging
2. **Test with the test script** to verify logging works
3. **Try your Android app** and watch the backend logs
4. **Use the debug page** (`/api-debug`) in your frontend to test API calls
5. **Compare the logs** to see exactly where the issue occurs

The detailed logging will show you exactly what's happening with every API call, making it much easier to debug the Android connectivity issues!
