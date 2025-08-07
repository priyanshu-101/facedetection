import os
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

class FileService:
    def __init__(self):
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file, custom_filename=None):
        """Save uploaded file and return the file path"""
        try:
            if file and self.allowed_file(file.filename):
                # Generate unique filename
                if custom_filename:
                    filename = secure_filename(custom_filename)
                else:
                    # Use original filename with UUID prefix
                    original_filename = secure_filename(file.filename)
                    file_extension = original_filename.rsplit('.', 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                file_path = os.path.join(self.upload_folder, filename)
                file.save(file_path)
                return file_path
            else:
                return None
                
        except Exception as e:
            print(f"Error saving uploaded file: {e}")
            return None
    
    def delete_file(self, file_path):
        """Delete a file from the filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, file_path):
        """Get the URL for accessing the file"""
        try:
            # Return relative path for serving via Flask
            return file_path.replace('\\', '/')
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None
    
    def validate_file_size(self, file, max_size_mb=16):
        """Validate file size (default 16MB limit)"""
        try:
            # Seek to end of file to get size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            max_size_bytes = max_size_mb * 1024 * 1024
            return file_size <= max_size_bytes
            
        except Exception as e:
            print(f"Error validating file size: {e}")
            return False
    
    def create_user_folder(self, user_name):
        """Create a folder for a specific user"""
        try:
            user_folder = os.path.join(self.upload_folder, secure_filename(user_name))
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            return user_folder
        except Exception as e:
            print(f"Error creating user folder: {e}")
            return None
    
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'exists': True
                }
            else:
                return {'exists': False}
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {'exists': False}
