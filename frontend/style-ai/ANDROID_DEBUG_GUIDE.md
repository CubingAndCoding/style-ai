# Android API Debugging Guide

## Issue: API calls not working on Android

### Problem Analysis
The app opens fine on Android but API calls fail, specifically:
- Registration always returns "username or email already exists" 
- This suggests the API calls might not be reaching the backend properly

### Debugging Steps

#### 1. Use the Debug Page
I've created an API debug page at `/api-debug` that you can access by navigating to:
```
http://localhost:8100/api-debug
```

This page will:
- Test environment configuration
- Test API connectivity
- Test registration and login endpoints
- Show detailed error information

#### 2. Check Environment Configuration
The app is currently using the default API URL: `https://style-ai-production.up.railway.app`

To verify this is correct:
1. Open the debug page
2. Click "Test Environment" to see all environment variables
3. Verify the API_URL is pointing to your correct backend

#### 3. Create Environment File
Create a `.env.local` file in the frontend/style-ai directory with:

```env
# App Configuration
VITE_APP_NAME=Style AI
VITE_APP_VERSION=0.0.1

# API Configuration - Replace with your actual Railway backend URL
VITE_API_URL=https://style-ai-production.up.railway.app

# Development flags (set to true for debugging)
VITE_DEBUG_MODE=true
VITE_ENABLE_CONSOLE_LOGS=true

# API Timeout (in milliseconds)
VITE_API_TIMEOUT=15000
```

#### 4. Android Network Configuration
I've added network security configuration to allow HTTPS traffic. The Android manifest now includes:
- `android:usesCleartextTraffic="true"`
- `android:networkSecurityConfig="@xml/network_security_config"`

#### 5. Test API Endpoints Directly
You can test the backend directly using curl:

```bash
# Test registration
curl -X POST https://style-ai-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","email":"test@example.com","password":"testpass123"}'

# Test login
curl -X POST https://style-ai-production.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","password":"testpass123"}'
```

#### 6. Check Browser Console
When testing on Android:
1. Open Chrome DevTools
2. Connect to your Android device
3. Check the console for any network errors
4. Look for CORS errors or connection timeouts

#### 7. Common Issues and Solutions

**Issue: CORS Errors**
- The backend is configured to allow all origins (`CORS(app)`)
- This should not be the issue

**Issue: Network Timeout**
- Increase `VITE_API_TIMEOUT` in your environment file
- Check if your Railway backend is running

**Issue: Wrong API URL**
- Verify the Railway URL is correct
- Check if the backend is deployed and accessible

**Issue: Android Network Security**
- The network security config should allow HTTPS traffic
- If testing with HTTP, make sure cleartext traffic is permitted

#### 8. Rebuild and Test
After making changes:
1. Stop the development server
2. Run `npm run build`
3. Run `npx cap sync android`
4. Run `npx cap open android`
5. Test the debug page first

### Next Steps
1. Use the debug page to identify the exact issue
2. Check the browser console for error details
3. Verify the backend is accessible from your network
4. Test with different usernames/emails to rule out database issues

The debug page will provide detailed information about what's failing and help pinpoint the exact issue.

