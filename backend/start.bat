@echo off
echo ========================================
echo Starting Face Detection Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if MongoDB is running
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); client.admin.command('ping'); print('MongoDB connected successfully')" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: MongoDB connection failed
    echo Please ensure MongoDB is installed and running
    echo.
    echo To start MongoDB:
    echo net start MongoDB
    echo.
    echo Or manually:
    echo mongod --dbpath "C:\data\db"
    echo.
    pause
)

REM Start the application
echo.
echo Starting Face Detection API...
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
