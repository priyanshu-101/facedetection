# Face Detection App

A full-stack face detection application with a FastAPI backend and React Native (Expo) frontend.

## Features

- Upload images from mobile device
- Detect faces in uploaded images using OpenCV
- Store detection results locally
- View detection history
- Clean, user-friendly interface

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the backend server:
   
   **Windows:**
   ```bash
   start.bat
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   Or manually:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. The backend will be available at: `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Remove Supabase dependency:
   ```bash
   npm uninstall @supabase/supabase-js
   ```

4. Start the Expo development server:
   ```bash
   npm start
   ```

5. Use the Expo Go app on your phone to scan the QR code and run the app

## API Endpoints

### Backend Endpoints

- `GET /` - Test form for browser-based uploads
- `POST /process-face` - Upload image and detect faces
- `GET /health` - Health check
- `GET /detections` - Get all face detection results

### Example Usage

```bash
# Health check
curl http://localhost:8000/health

# Upload image for face detection
curl -X POST "http://localhost:8000/process-face" \
  -F "name=John Doe" \
  -F "image=@photo.jpg"

# Get all detections
curl http://localhost:8000/detections
```

## Architecture

### Backend (FastAPI)
- **Framework:** FastAPI with uvicorn
- **Face Detection:** OpenCV with Haar Cascades
- **Storage:** Local JSON file (`data/face_detections.json`)
- **CORS:** Enabled for frontend communication

### Frontend (React Native + Expo)
- **Framework:** Expo with React Native
- **Navigation:** Expo Router
- **Image Picker:** expo-image-picker
- **API Client:** Custom fetch-based client

## File Structure

```
facedetection/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app and routes
│   │   ├── face_utils.py     # Face detection logic
│   │   └── face_utils_new.py # Alternative face detection
│   ├── data/                 # Local storage for results
│   ├── requirements.txt      # Python dependencies
│   ├── start.bat            # Windows startup script
│   └── start.sh             # Linux/macOS startup script
└── frontend/
    ├── app/                 # Expo Router pages
    ├── components/
    │   └── uploadForm.js    # Main upload component
    ├── services/
    │   └── apiClient.js     # Backend API client
    └── package.json         # Node.js dependencies
```

## Troubleshooting

### Backend Issues

1. **Port already in use:**
   ```bash
   # Change port in start script or kill existing process
   lsof -ti:8000 | xargs kill -9  # macOS/Linux
   netstat -ano | findstr :8000   # Windows
   ```

2. **OpenCV installation issues:**
   ```bash
   pip install opencv-python-headless
   ```

### Frontend Issues

1. **Cannot connect to backend:**
   - Ensure backend is running on `http://localhost:8000`
   - Check firewall settings
   - For Android emulator, the backend URL is automatically set to `http://10.0.2.2:8000`

2. **Image picker not working:**
   ```bash
   expo install expo-image-picker
   ```

3. **Metro bundler issues:**
   ```bash
   npx expo start --clear
   ```

## Development

### Adding New Features

1. **Backend:** Add new routes in `app/main.py`
2. **Frontend:** Add new API calls in `services/apiClient.js`
3. **Face Detection:** Modify algorithms in `app/face_utils.py`

### Production Deployment

1. **Backend:** Deploy to services like Railway, Heroku, or AWS
2. **Frontend:** Build with `expo build` for app stores
3. **Update API URLs:** Change `API_BASE_URL` in `apiClient.js`

## Dependencies

### Backend
- FastAPI - Web framework
- OpenCV - Computer vision
- uvicorn - ASGI server
- python-multipart - File upload handling

### Frontend
- Expo - React Native framework
- expo-image-picker - Image selection
- expo-router - Navigation

## License

MIT License - Feel free to use and modify as needed.
