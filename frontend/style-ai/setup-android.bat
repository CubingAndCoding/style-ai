@echo off
REM Style AI - Android Deployment Setup Script for Windows
REM This script helps set up your app for Google Play Store deployment

echo 🚀 Style AI - Android Deployment Setup
echo ======================================

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ Error: Please run this script from the frontend/style-ai directory
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ Node.js and npm are installed

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
) else (
    echo ✅ Dependencies already installed
)

REM Check if Android platform is already added
if exist "android" (
    echo ✅ Android platform already exists
) else (
    echo 📱 Adding Android platform...
    npm run cap:add:android
)

REM Build the web app
echo 🔨 Building web app...
npm run build

REM Sync with Capacitor
echo 🔄 Syncing with Capacitor...
npx cap sync android

echo.
echo 🎉 Setup complete! Next steps:
echo.
echo 1. Install Android Studio if you haven't already
echo 2. Open Android Studio and import the android folder
echo 3. Create app icons and splash screens
echo 4. Configure signing for release builds
echo 5. Build release bundle: cd android ^&^& gradlew bundleRelease
echo 6. Set up Google Play Console account
echo 7. Upload your app bundle to Play Console
echo.
echo 📖 For detailed instructions, see GOOGLE_PLAY_DEPLOYMENT.md
echo.
echo 🔧 To open Android Studio: npm run cap:open:android
echo 📱 To run on device: npm run cap:run:android
echo.
pause

