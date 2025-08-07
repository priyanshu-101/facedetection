@echo off
echo ========================================
echo Face Detection Backend Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Choose installation method:
echo 1. Basic installation (OpenCV only - recommended for Windows)
echo 2. Advanced installation (with face_recognition - requires Visual Studio)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Installing basic dependencies...
    pip install -r requirements_basic.txt
    if errorlevel 1 (
        echo ERROR: Failed to install basic dependencies
        echo Trying individual installation...
        pip install Flask==2.3.3
        pip install Flask-CORS==4.0.0
        pip install pymongo==4.5.0
        pip install opencv-python==4.8.1.78
        pip install numpy==1.24.3
        pip install Pillow==10.0.1
        pip install python-dotenv==1.0.0
        pip install werkzeug==2.3.7
        pip install bson==0.5.10
    )
    echo.
    echo Basic installation completed!
    echo The app will use OpenCV-only face recognition.
    
) else if "%choice%"=="2" (
    echo.
    echo Installing advanced dependencies...
    echo This may take several minutes and requires Visual Studio Build Tools...
    pip install cmake
    pip install dlib==19.24.1
    if errorlevel 1 (
        echo ERROR: Failed to install dlib
        echo Please install Visual Studio Build Tools first:
        echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo.
        echo Falling back to basic installation...
        pip install -r requirements_basic.txt
    ) else (
        pip install face-recognition==1.3.0
        pip install -r requirements_basic.txt
        echo.
        echo Advanced installation completed!
        echo The app will use advanced face recognition.
    )
    
) else (
    echo Invalid choice. Installing basic version...
    pip install -r requirements_basic.txt
)

REM Create uploads directory
echo.
echo Creating uploads directory...
if not exist "uploads" mkdir uploads

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Ensure MongoDB is running
echo 2. Run: python app.py
echo.
echo The API will be available at:
echo http://localhost:5000
echo.
pause
