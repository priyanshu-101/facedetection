# Face Detection Backend

A Python Flask backend for face detection and recognition using OpenCV and MongoDB.

## Features

- User registration with photo upload
- Face detection and encoding
- Face recognition from uploaded images
- MongoDB storage for user data and face encodings
- RESTful API endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=facedetection
UPLOAD_FOLDER=uploads
```

3. Start MongoDB service

4. Run the application:
```bash
python app.py
```

## API Endpoints

- `POST /register` - Register a new user with photo
- `POST /detect` - Detect and recognize faces in uploaded image
- `GET /users` - Get all registered users
- `GET /user/<user_id>` - Get specific user details

## Directory Structure

```
backend/
├── app.py              # Main Flask application
├── models/
│   ├── user.py         # User model
│   └── database.py     # Database connection
├── services/
│   ├── face_service.py # Face detection and recognition
│   └── file_service.py # File upload handling
├── routes/
│   └── api_routes.py   # API route definitions
├── uploads/            # Uploaded images storage
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```
