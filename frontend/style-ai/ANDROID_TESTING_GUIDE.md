# Android Testing Guide

This guide will help you test your Style AI frontend on Android devices or emulators.

## Prerequisites

1. **Android Studio** - Download from [developer.android.com/studio](https://developer.android.com/studio)
2. **Java Development Kit (JDK)** - Android Studio includes this, or install JDK 11+ separately
3. **Android SDK** - Installed via Android Studio
4. **Physical Android Device** (optional but recommended) OR **Android Emulator**

## Quick Start - Testing on Android

### Option 1: Using Android Studio (Recommended)

1. **Build and sync your app:**
   ```bash
   cd frontend/style-ai
   npm run cap:build:android
   ```

2. **Open Android Studio:**
   ```bash
   npm run cap:open:android
   ```
   Or manually: Open Android Studio → File → Open → Select `frontend/style-ai/android` folder

3. **Wait for Gradle sync** (first time may take a few minutes)

4. **Run on Device/Emulator:**
   - Connect your Android device via USB (enable USB debugging)
   - OR create/start an Android emulator (Tools → Device Manager)
   - Click the green "Run" button (▶️) or press `Shift+F10`

### Option 2: Using Command Line (Advanced)

1. **Build and sync:**
   ```bash
   cd frontend/style-ai
   npm run build
   npx cap sync android
   ```

2. **Run on connected device:**
   ```bash
   cd android
   ./gradlew installDebug
   ```
   (On Windows: `gradlew.bat installDebug`)

## Setting Up Android Device for Testing

### Enable Developer Options:
1. Go to Settings → About Phone
2. Tap "Build Number" 7 times
3. Go back to Settings → Developer Options
4. Enable "USB Debugging"

### Connect Device:
1. Connect via USB
2. Accept the "Allow USB Debugging" prompt on your phone
3. Verify connection: `adb devices` (should show your device)

## Setting Up Android Emulator

1. Open Android Studio
2. Go to Tools → Device Manager
3. Click "Create Device"
4. Choose a device (e.g., Pixel 5)
5. Download a system image (e.g., Android 13)
6. Click "Finish"
7. Start the emulator by clicking the play button

## Testing Workflow

### After Making Frontend Changes:

1. **Rebuild the web app:**
   ```bash
   cd frontend/style-ai
   npm run build
   ```

2. **Sync with Capacitor:**
   ```bash
   npx cap sync android
   ```

3. **In Android Studio:**
   - Click the "Run" button again (or press `Shift+F10`)
   - The app will reload with your changes

### Live Reload (Development Mode):

For faster development, you can use Capacitor's live reload:

1. **Start your dev server:**
   ```bash
   cd frontend/style-ai
   npm run dev
   ```

2. **Update capacitor.config.ts** to point to your dev server:
   ```typescript
   server: {
     url: 'http://YOUR_LOCAL_IP:5173',
     cleartext: true
   }
   ```

3. **Sync:**
   ```bash
   npx cap sync android
   ```

4. **Run the app** - Changes will reload automatically!

## Troubleshooting

### Issue: "Gradle sync failed"
- **Solution:** Open Android Studio → File → Invalidate Caches → Invalidate and Restart

### Issue: "SDK not found"
- **Solution:** Open Android Studio → Tools → SDK Manager → Install required SDKs

### Issue: "Device not detected"
- **Solution:** 
  - Check USB debugging is enabled
  - Try different USB cable/port
  - Run `adb kill-server && adb start-server`

### Issue: "Build failed"
- **Solution:** 
  - Check Android Studio's Build output for errors
  - Ensure all dependencies are installed: `npm install`
  - Try: `cd android && ./gradlew clean`

### Issue: "App crashes on launch"
- **Solution:**
  - Check Logcat in Android Studio for error messages
  - Verify API URL is correct in environment config
  - Check network permissions in AndroidManifest.xml

## Useful Commands

```bash
# Build and sync
npm run cap:build:android

# Open Android Studio
npm run cap:open:android

# Check connected devices
adb devices

# View logs
adb logcat

# Install APK directly
adb install -r android/app/build/outputs/apk/debug/app-debug.apk

# Uninstall app
adb uninstall com.styleai.app
```

## Testing Checklist

- [ ] App launches without crashes
- [ ] Login/Register functionality works
- [ ] API calls connect to backend
- [ ] Camera functionality works (if applicable)
- [ ] UI displays correctly on different screen sizes
- [ ] Navigation works smoothly
- [ ] Payment integration works (if applicable)
- [ ] Network requests work on mobile data and WiFi

## Next Steps

Once testing is complete:
- See `GOOGLE_PLAY_DEPLOYMENT.md` for production deployment
- See `ANDROID_DEBUG_GUIDE.md` for debugging API issues

