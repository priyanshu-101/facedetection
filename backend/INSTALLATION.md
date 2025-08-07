# Face Detection Backend - Installation Guide

## Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Make sure to add Python to PATH during installation

2. **MongoDB**
   - Download from: https://www.mongodb.com/try/download/community
   - Install and start the MongoDB service
   - Default connection: `mongodb://localhost:27017/`

3. **Visual C++ Build Tools** (for Windows)
   - Required for some Python packages (dlib, face-recognition)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

## Installation Steps

### 1. Install Python Dependencies

**IMPORTANT for Windows Users:** The `face_recognition` library requires Visual C++ build tools. Choose one of these methods:

#### Method A: Install Visual Studio Build Tools (Recommended)
1. Download and install Visual Studio Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. During installation, select "C++ build tools" workload
3. Restart your computer after installation

#### Method B: Use Pre-compiled Wheels (Easier)
Open PowerShell in the backend directory and run:

```powershell
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install specific versions with pre-compiled wheels
pip install cmake
pip install dlib==19.24.1
pip install face-recognition==1.3.0

# Install other dependencies
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install pymongo==4.5.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install Pillow==10.0.1
pip install python-dotenv==1.0.0
pip install werkzeug==2.3.7
pip install bson==0.5.10
```

#### Method C: Alternative Face Recognition (If above fails)
If you still have issues, use this alternative approach:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies without face_recognition
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install pymongo==4.5.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install Pillow==10.0.1
pip install python-dotenv==1.0.0
pip install werkzeug==2.3.7
pip install bson==0.5.10

# Use OpenCV-only implementation (see note below)
```

**Note:** If using Method C, the face recognition will be less accurate but will work with basic face detection.

### 2. Set up MongoDB

```powershell
# Start MongoDB service (if not running)
net start MongoDB

# Or if installed manually:
mongod --dbpath "C:\data\db"
```

### 3. Configure Environment

Update the `.env` file with your settings:

```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=facedetection
UPLOAD_FOLDER=uploads
SECRET_KEY=your-secret-key-here
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif
FACE_RECOGNITION_TOLERANCE=0.6
HOST=0.0.0.0
PORT=5000
FLASK_ENV=development
```

### 4. Run Setup Script

```powershell
python setup.py
```

## Running the Application

```powershell
# Start the Flask server
python app.py
```

The API will be available at: `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "message": "Face Detection API is running"
}
```

#### 2. Register User
```
POST /register
```
**Request:**
- Form data: `name` (string)
- File: `photo` (image file)

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "60d5ec49f1b2c8b1f8e4e1a1",
  "name": "John Doe",
  "image_url": "uploads/john_doe_photo.jpg"
}
```

#### 3. Detect Face
```
POST /detect
```
**Request:**
- File: `photo` (image file)

**Response:**
```json
{
  "faces_detected": 1,
  "face_locations": [[120, 200, 300, 80]],
  "recognition": {
    "recognized": true,
    "user_name": "John Doe",
    "confidence": 0.85,
    "distance": 0.15
  }
}
```

#### 4. Get All Users
```
GET /users
```
**Response:**
```json
{
  "users": [
    {
      "_id": "60d5ec49f1b2c8b1f8e4e1a1",
      "name": "John Doe",
      "image_url": "uploads/john_doe_photo.jpg",
      "created_at": "2023-06-25T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

#### 5. Get User by ID
```
GET /user/<user_id>
```
**Response:**
```json
{
  "user": {
    "_id": "60d5ec49f1b2c8b1f8e4e1a1",
    "name": "John Doe",
    "image_url": "uploads/john_doe_photo.jpg",
    "created_at": "2023-06-25T10:30:00Z"
  }
}
```

#### 6. Delete User
```
DELETE /user/<user_id>
```
**Response:**
```json
{
  "message": "User deleted successfully"
}
```

## Testing

Run the test script to verify API functionality:

```powershell
python test_api.py
```

## Troubleshooting

### Common Issues

1. **dlib/face_recognition installation fails on Windows**
   ```
   ERROR: Building wheel for dlib failed
   ```
   **Solutions:**
   - **Option A:** Install Visual Studio Build Tools
     - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
     - Select "C++ build tools" workload during installation
     - Restart computer and try again
   
   - **Option B:** Use basic installation (recommended)
     ```powershell
     pip install -r requirements_basic.txt
     ```
     This will use OpenCV-only face recognition which works well for most cases.

2. **ImportError: No module named 'cv2'**
   ```powershell
   pip install opencv-python
   ```

3. **ImportError: No module named 'face_recognition'**
   This is expected if you're using the basic installation. The app will automatically use OpenCV-only recognition.

4. **MongoDB Connection Error**
   - Ensure MongoDB service is running:
     ```powershell
     net start MongoDB
     ```
   - Or start manually:
     ```powershell
     mongod --dbpath "C:\data\db"
     ```
   - Check connection string in `.env` file
   - Verify MongoDB is accessible on port 27017

5. **File Upload Issues**
   - Check upload folder permissions
   - Verify file size limits (16MB default)
   - Ensure allowed file extensions (png, jpg, jpeg, gif)

6. **Virtual Environment Issues**
   - Make sure you're in the correct directory
   - Try deleting the `venv` folder and recreating it:
     ```powershell
     rmdir /s venv
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

### Face Recognition Method Comparison

| Method | Accuracy | Setup Difficulty | Requirements |
|--------|----------|------------------|--------------|
| Advanced (face_recognition) | High | Hard (Windows) | Visual Studio Build Tools |
| Basic (OpenCV) | Medium | Easy | OpenCV only |

The basic method works well for most use cases and is much easier to set up on Windows.

### Performance Tips

1. **Image Preprocessing**
   - Resize large images before upload
   - Use good lighting for better face detection
   - Ensure faces are clearly visible

2. **Database Optimization**
   - Create indexes for frequently queried fields
   - Regular database maintenance

3. **Memory Management**
   - Process images in batches for bulk operations
   - Clear temporary files regularly

## Security Considerations

1. **Input Validation**
   - File type validation
   - File size limits
   - Sanitize user inputs

2. **Authentication**
   - Add JWT authentication for production
   - Implement rate limiting

3. **Data Protection**
   - Encrypt sensitive data
   - Secure file storage
   - Regular backups

## Production Deployment

1. **Environment Setup**
   ```env
   FLASK_ENV=production
   SECRET_KEY=strong-random-secret-key
   DEBUG=False
   ```

2. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)
   - Enable HTTPS

3. **Database**
   - Use MongoDB Atlas or managed MongoDB
   - Enable authentication
   - Configure backups

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Verify all dependencies are installed correctly
