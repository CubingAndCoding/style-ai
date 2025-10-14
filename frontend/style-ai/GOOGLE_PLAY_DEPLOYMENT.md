# Google Play Store Deployment Guide for Style AI

## Prerequisites

1. **Android Studio** - Download and install from https://developer.android.com/studio
2. **Java Development Kit (JDK)** - Version 11 or higher
3. **Google Play Console Account** - $25 one-time registration fee
4. **Android SDK** - Installed via Android Studio

## Step 1: Initialize Capacitor and Add Android Platform

```bash
# Navigate to your frontend directory
cd frontend/style-ai

# Install dependencies (if not already done)
npm install

# Add Android platform
npm run cap:add:android

# Build and sync
npm run cap:build:android
```

## Step 2: Configure App Metadata

### App Icons
You need to create app icons in multiple sizes:
- **48x48dp** (mdpi) - 48x48px
- **72x72dp** (hdpi) - 72x72px  
- **96x96dp** (xhdpi) - 96x96px
- **144x144dp** (xxhdpi) - 144x144px
- **192x192dp** (xxxhdpi) - 192x192px

Place these in: `android/app/src/main/res/drawable-[density]/`

### Splash Screen
Create splash screen images:
- **320x480dp** (mdpi) - 320x480px
- **480x800dp** (hdpi) - 480x800px
- **720x1280dp** (xhdpi) - 720x1280px
- **1080x1920dp** (xxhdpi) - 1080x1920px
- **1440x2560dp** (xxxhdpi) - 1440x2560px

## Step 3: Configure Android Permissions

The following permissions will be automatically added by Capacitor plugins:

### Camera Permissions
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```

### Network Permissions
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## Step 4: Build Production App

### Create Release Keystore
```bash
# Generate a keystore for signing your app
keytool -genkey -v -keystore style-ai-release-key.keystore -alias style-ai-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

### Configure Gradle for Release
Add to `android/app/build.gradle`:

```gradle
android {
    ...
    signingConfigs {
        release {
            if (project.hasProperty('MYAPP_RELEASE_STORE_FILE')) {
                storeFile file(MYAPP_RELEASE_STORE_FILE)
                storePassword MYAPP_RELEASE_STORE_PASSWORD
                keyAlias MYAPP_RELEASE_KEY_ALIAS
                keyPassword MYAPP_RELEASE_KEY_PASSWORD
            }
        }
    }
    buildTypes {
        release {
            ...
            signingConfig signingConfigs.release
        }
    }
}
```

### Create gradle.properties
Create `android/gradle.properties`:
```properties
MYAPP_RELEASE_STORE_FILE=style-ai-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=style-ai-key-alias
MYAPP_RELEASE_STORE_PASSWORD=your_store_password
MYAPP_RELEASE_KEY_PASSWORD=your_key_password
```

### Build Release Bundle
```bash
# Build the app bundle (recommended for Play Store)
cd android
./gradlew bundleRelease
```

## Step 5: Google Play Console Setup

### 1. Create Google Play Console Account
- Go to https://play.google.com/console
- Pay $25 registration fee
- Complete developer profile

### 2. Create New App
- Click "Create app"
- Fill in app details:
  - **App name**: Style AI
  - **Default language**: English (United States)
  - **App or game**: App
  - **Free or paid**: Free (or Paid if you want to charge)

### 3. App Content Rating
Complete the content rating questionnaire:
- Age range: 13+ (due to camera access)
- Content: No objectionable content

## Step 6: Store Listing Assets

### Required Assets:
1. **App Icon**: 512x512px PNG
2. **Feature Graphic**: 1024x500px PNG
3. **Screenshots**: 
   - Phone: 320-3840px wide, 2:1 to 1:2 aspect ratio
   - Tablet: 1080-7680px wide, 2:1 to 1:2 aspect ratio
4. **Short Description**: 80 characters max
5. **Full Description**: 4000 characters max

### Example Store Listing:

**Short Description:**
"AI-powered image processing and style transfer app with camera integration"

**Full Description:**
```
Transform your photos with Style AI - the ultimate image processing app powered by artificial intelligence.

🎨 KEY FEATURES:
• Advanced AI image processing
• Real-time camera integration
• Style transfer technology
• Secure cloud processing
• Professional-grade filters
• Easy-to-use interface

📸 CAMERA FEATURES:
• High-quality photo capture
• Instant AI processing
• Multiple style options
• Gallery management
• Share your creations

🔒 SECURITY & PRIVACY:
• Secure authentication
• Encrypted data transmission
• Privacy-focused design
• No data retention

Perfect for photographers, designers, and anyone who loves creative photo editing. Download Style AI today and discover the power of AI-driven image processing!

#StyleAI #PhotoEditing #AI #Camera #ImageProcessing
```

## Step 7: Upload and Publish

### 1. Upload App Bundle
- Go to "Release" → "Production"
- Click "Create new release"
- Upload your `.aab` file from `android/app/build/outputs/bundle/release/`

### 2. Release Notes
Add release notes for version 1.0:
```
Initial release of Style AI
- AI-powered image processing
- Camera integration
- Style transfer features
- Secure authentication
- Gallery management
```

### 3. Review and Publish
- Review all information
- Submit for review
- Wait for Google's approval (usually 1-3 days)

## Post-Launch Considerations

### 1. App Updates
- Use semantic versioning (1.0.0, 1.0.1, etc.)
- Test thoroughly before each release
- Update release notes for each version

### 2. Analytics
Consider adding:
- Google Analytics for Firebase
- Crash reporting
- User engagement metrics

### 3. Monetization (Optional)
- In-app purchases for premium features
- Subscription model
- Ad integration

## Troubleshooting

### Common Issues:
1. **Build Errors**: Ensure Android SDK is properly installed
2. **Permission Denied**: Check AndroidManifest.xml permissions
3. **App Rejected**: Review Google Play policies
4. **Signing Issues**: Verify keystore configuration

### Support Resources:
- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer/)
- [Android Developer Guide](https://developer.android.com/distribute)

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Backend Security**: Ensure your backend is properly secured
3. **Data Privacy**: Comply with GDPR/CCPA if applicable
4. **App Signing**: Keep your keystore secure and backed up

Remember to test your app thoroughly on different Android devices before publishing!
