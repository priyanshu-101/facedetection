from flask import Blueprint, request, jsonify, send_from_directory
from models.user import User
from services.face_service import FaceService
from services.file_service import FileService
import os

api = Blueprint('api', __name__)

# Initialize services
user_model = User()
face_service = FaceService()
file_service = FileService()

@api.route('/register', methods=['POST'])
def register_user():
    """Register a new user with photo upload"""
    try:
        # Check if required data is provided
        if 'name' not in request.form:
            return jsonify({'error': 'Name is required'}), 400
        
        if 'photo' not in request.files:
            return jsonify({'error': 'Photo is required'}), 400
        
        name = request.form['name'].strip()
        photo = request.files['photo']
        
        # Validate inputs
        if not name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        
        if photo.filename == '':
            return jsonify({'error': 'No photo selected'}), 400
        
        # Check if user already exists
        if user_model.user_exists(name):
            return jsonify({'error': 'User with this name already exists'}), 409
        
        # Validate file size
        if not file_service.validate_file_size(photo):
            return jsonify({'error': 'File size too large (max 16MB)'}), 400
        
        # Save the uploaded photo
        file_path = file_service.save_uploaded_file(photo, f"{name}_{photo.filename}")
        if not file_path:
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Validate image and detect faces
        is_valid, validation_message = face_service.validate_image(file_path)
        if not is_valid:
            file_service.delete_file(file_path)
            return jsonify({'error': validation_message}), 400
        
        # Extract face encoding
        face_encoding = face_service.extract_face_encoding(file_path)
        if face_encoding is None:
            file_service.delete_file(file_path)
            return jsonify({'error': 'Could not extract face encoding from image'}), 400
        
        # Create user in database
        user_id = user_model.create_user(name, file_path, face_encoding)
        if not user_id:
            file_service.delete_file(file_path)
            return jsonify({'error': 'Failed to create user'}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'name': name,
            'image_url': file_service.get_file_url(file_path)
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@api.route('/detect', methods=['POST'])
def detect_face():
    """Detect and recognize faces in uploaded image"""
    try:
        if 'photo' not in request.files:
            return jsonify({'error': 'Photo is required'}), 400
        
        photo = request.files['photo']
        
        if photo.filename == '':
            return jsonify({'error': 'No photo selected'}), 400
        
        # Validate file size
        if not file_service.validate_file_size(photo):
            return jsonify({'error': 'File size too large (max 16MB)'}), 400
        
        # Save the uploaded photo temporarily
        temp_file_path = file_service.save_uploaded_file(photo)
        if not temp_file_path:
            return jsonify({'error': 'Invalid file format'}), 400
        
        try:
            # Detect faces using OpenCV
            detected_faces = face_service.detect_faces_opencv(temp_file_path)
            
            # Extract face encoding for recognition
            unknown_encoding = face_service.extract_face_encoding(temp_file_path)
            
            recognition_result = None
            if unknown_encoding is not None:
                # Get all registered users
                all_users = user_model.get_all_users()
                
                if all_users:
                    # Prepare known encodings and names
                    known_encodings = [user['face_encoding'] for user in all_users]
                    user_names = [user['name'] for user in all_users]
                    
                    # Find best match
                    best_match = face_service.find_best_match(
                        known_encodings, 
                        unknown_encoding, 
                        user_names
                    )
                    
                    if best_match:
                        recognition_result = {
                            'recognized': True,
                            'user_name': best_match['user_name'],
                            'confidence': round(best_match['confidence'], 4),
                            'distance': round(best_match['distance'], 4)
                        }
                    else:
                        recognition_result = {
                            'recognized': False,
                            'message': 'No matching user found'
                        }
                else:
                    recognition_result = {
                        'recognized': False,
                        'message': 'No users registered yet'
                    }
            else:
                recognition_result = {
                    'recognized': False,
                    'message': 'No faces detected for recognition'
                }
            
            return jsonify({
                'faces_detected': len(detected_faces),
                'face_locations': detected_faces,
                'recognition': recognition_result
            }), 200
            
        finally:
            # Clean up temporary file
            file_service.delete_file(temp_file_path)
            
    except Exception as e:
        return jsonify({'error': f'Face detection failed: {str(e)}'}), 500

@api.route('/users', methods=['GET'])
def get_all_users():
    """Get all registered users"""
    try:
        users = user_model.get_all_users()
        
        # Remove face encodings from response (too large)
        for user in users:
            if 'face_encoding' in user:
                del user['face_encoding']
            # Add image URL
            if 'image_path' in user:
                user['image_url'] = file_service.get_file_url(user['image_path'])
        
        return jsonify({
            'users': users,
            'total_count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get users: {str(e)}'}), 500

@api.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user details"""
    try:
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove face encoding from response
        if 'face_encoding' in user:
            del user['face_encoding']
        
        # Add image URL
        if 'image_path' in user:
            user['image_url'] = file_service.get_file_url(user['image_path'])
        
        return jsonify({'user': user}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

@api.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user's image file
        if 'image_path' in user:
            file_service.delete_file(user['image_path'])
        
        # Delete user from database
        success = user_model.delete_user(user_id)
        
        if success:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

@api.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Face Detection API is running'
    }), 200
