from bson.objectid import ObjectId
from datetime import datetime
from models.database import db_instance
import numpy as np

class User:
    def __init__(self):
        self.collection = db_instance.get_collection('users')
    
    def _serialize_dict_with_numpy(self, data):
        """Recursively convert numpy arrays in dictionaries to lists for MongoDB storage"""
        if isinstance(data, dict):
            return {key: self._serialize_dict_with_numpy(value) for key, value in data.items()}
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, (list, tuple)):
            return [self._serialize_dict_with_numpy(item) for item in data]
        else:
            return data
    
    def _deserialize_dict_with_numpy(self, data):
        """Recursively convert lists back to numpy arrays in dictionaries for OpenCV compatibility"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'histogram' and isinstance(value, list):
                    # Convert histogram back to numpy array for OpenCV operations
                    result[key] = np.array(value)
                elif key == 'face_region' and isinstance(value, list):
                    # Convert face region back to numpy array
                    result[key] = np.array(value)
                else:
                    result[key] = self._deserialize_dict_with_numpy(value)
            return result
        elif isinstance(data, list):
            return [self._deserialize_dict_with_numpy(item) for item in data]
        else:
            return data
    
    def create_user_simple(self, name, image_path):
        """Create a new user without face encoding (just save name and image)"""
        try:
            print(f"Creating user (simple): {name}, image: {image_path}")
            
            # Check if database connection exists
            if self.collection is None:
                print("Error: Database collection is None")
                return None
            
            user_data = {
                'name': name,
                'image_path': image_path,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            print("Inserting user data into database...")
            result = self.collection.insert_one(user_data)
            print(f"User created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_user(self, name, image_path, face_encoding):
        """Create a new user with face encoding"""
        try:
            print(f"Creating user: {name}, image: {image_path}")
            print(f"Face encoding type: {type(face_encoding)}")
            
            # Check if database connection exists
            if self.collection is None:
                print("Error: Database collection is None")
                return None
            
            # Handle different types of face encodings
            if isinstance(face_encoding, np.ndarray):
                # face_recognition library encoding (numpy array)
                print("Converting numpy array to list")
                encoding_data = face_encoding.tolist()
            elif isinstance(face_encoding, dict):
                # OpenCV face service encoding (dictionary) - handle nested numpy arrays
                print("Serializing dictionary with numpy arrays")
                encoding_data = self._serialize_dict_with_numpy(face_encoding)
            elif hasattr(face_encoding, 'tolist'):
                # Any array-like object with tolist method
                print("Converting array-like object to list")
                encoding_data = face_encoding.tolist()
            else:
                # Store as-is for other types
                print("Storing face encoding as-is")
                encoding_data = face_encoding
            
            user_data = {
                'name': name,
                'image_path': image_path,
                'face_encoding': encoding_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            print("Inserting user data into database...")
            result = self.collection.insert_one(user_data)
            print(f"User created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                # Keep face_encoding as stored (don't convert to numpy) for JSON serialization
            return user
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_name(self, name):
        """Get user by name"""
        try:
            user = self.collection.find_one({'name': name})
            if user:
                user['_id'] = str(user['_id'])
                # Keep face_encoding as stored (don't convert to numpy) for JSON serialization
            return user
        except Exception as e:
            print(f"Error getting user by name: {e}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            users = []
            for user in self.collection.find():
                user['_id'] = str(user['_id'])
                # Keep face_encoding as stored (don't convert to numpy) for JSON serialization
                users.append(user)
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_user_with_encoding(self, user_id):
        """Get user by ID with face encoding converted back to numpy for processing"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                # Convert face encoding back to numpy for processing
                if 'face_encoding' in user:
                    encoding = user['face_encoding']
                    if isinstance(encoding, list):
                        # Convert list back to numpy array (for face_recognition library)
                        user['face_encoding'] = np.array(encoding)
                    elif isinstance(encoding, dict):
                        # For dict (OpenCV), convert nested lists back to numpy arrays if needed
                        user['face_encoding'] = self._deserialize_dict_with_numpy(encoding)
            return user
        except Exception as e:
            print(f"Error getting user with encoding: {e}")
            return None
    
    def get_all_users_with_encoding(self):
        """Get all users with face encodings converted back to numpy for processing"""
        try:
            users = []
            for user in self.collection.find():
                user['_id'] = str(user['_id'])
                # Convert face encoding back to numpy for processing
                if 'face_encoding' in user:
                    encoding = user['face_encoding']
                    if isinstance(encoding, list):
                        # Convert list back to numpy array (for face_recognition library)
                        user['face_encoding'] = np.array(encoding)
                    elif isinstance(encoding, dict):
                        # For dict (OpenCV), convert nested lists back to numpy arrays if needed
                        user['face_encoding'] = self._deserialize_dict_with_numpy(encoding)
                users.append(user)
            return users
        except Exception as e:
            print(f"Error getting all users with encoding: {e}")
            return []
    
    def update_user(self, user_id, update_data):
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete user by ID"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def user_exists(self, name):
        """Check if user with given name exists"""
        try:
            return self.collection.find_one({'name': name}) is not None
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False
