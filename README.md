# Style AI

A mobile application built with Ionic React and Python Flask that allows users to capture photos, process them with AI, and view them in a gallery.

## Features

- Photo capture using device camera
- Image upload to backend server
- AI-powered image processing
- Gallery view with automatic refresh
- Pull-to-refresh functionality
- Error handling and loading states

## Tech Stack

### Frontend
- Ionic React
- TypeScript
- Capacitor for native device features
- Axios for API calls

### Backend
- Python Flask
- RESTful API endpoints
- Image processing capabilities

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend/style-ai
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. For mobile development, add platforms:
   ```bash
   ionic capacitor add android
   ionic capacitor add ios
   ```

## Project Structure

```
style-ai/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── uploads/
├── frontend/
│   └── style-ai/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── CameraPage.tsx
│       │   │   └── GalleryPage.tsx
│       │   └── App.tsx
│       └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 