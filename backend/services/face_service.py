import cv2
import face_recognition
import numpy as np
from PIL import Image
import os

class FaceService:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces_opencv(self, image_path):
        """Detect faces using OpenCV with improved parameters"""
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization to improve detection
            gray = cv2.equalizeHist(gray)
            
            # Try multiple detection parameters for better results
            detection_params = [
                {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (30, 30)},
                {'scaleFactor': 1.05, 'minNeighbors': 4, 'minSize': (20, 20)},
                {'scaleFactor': 1.2, 'minNeighbors': 6, 'minSize': (40, 40)},
                {'scaleFactor': 1.3, 'minNeighbors': 3, 'minSize': (15, 15)}
            ]
            
            faces = []
            for params in detection_params:
                detected = self.face_cascade.detectMultiScale(gray, **params)
                if len(detected) > 0:
                    faces = detected
                    break
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            print(f"Error detecting faces with OpenCV: {e}")
            return []
    
    def extract_face_encoding(self, image_path):
        """Extract face encoding using face_recognition library"""
        try:
            # Load the image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return None
            
            # Get face encodings (use the first face found)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if face_encodings:
                return face_encodings[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def compare_faces(self, known_encodings, unknown_encoding, tolerance=0.6):
        """Compare face encodings to find matches"""
        try:
            if not known_encodings or unknown_encoding is None:
                return []
            
            # Convert known_encodings to numpy arrays if they aren't already
            known_encodings_array = []
            for encoding in known_encodings:
                if isinstance(encoding, list):
                    known_encodings_array.append(np.array(encoding))
                else:
                    known_encodings_array.append(encoding)
            
            # Compare faces
            matches = face_recognition.compare_faces(
                known_encodings_array, 
                unknown_encoding, 
                tolerance=tolerance
            )
            
            # Calculate face distances
            face_distances = face_recognition.face_distance(
                known_encodings_array, 
                unknown_encoding
            )
            
            return {
                'matches': matches,
                'distances': face_distances.tolist()
            }
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return {'matches': [], 'distances': []}
    
    def find_best_match(self, known_encodings, unknown_encoding, user_names, tolerance=0.6):
        """Find the best matching face"""
        try:
            comparison_result = self.compare_faces(known_encodings, unknown_encoding, tolerance)
            matches = comparison_result['matches']
            distances = comparison_result['distances']
            
            if not any(matches):
                return None
            
            # Find the best match (smallest distance among matches)
            best_match_index = None
            best_distance = float('inf')
            
            for i, (match, distance) in enumerate(zip(matches, distances)):
                if match and distance < best_distance:
                    best_distance = distance
                    best_match_index = i
            
            if best_match_index is not None:
                return {
                    'user_name': user_names[best_match_index],
                    'confidence': 1 - best_distance,  # Convert distance to confidence
                    'distance': best_distance
                }
            
            return None
            
        except Exception as e:
            print(f"Error finding best match: {e}")
            return None
    
    def validate_image(self, image_path):
        """Validate if the image is valid and contains a face"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return False, "Image file does not exist"
            
            # Try to load the image
            try:
                image = cv2.imread(image_path)
                if image is None:
                    return False, "Invalid image format"
            except Exception:
                return False, "Cannot read image file"
            
            # Check if image contains at least one face
            faces = self.detect_faces_opencv(image_path)
            if not faces:
                return False, "No faces detected in the image"
            
            return True, "Image is valid"
            
        except Exception as e:
            return False, f"Error validating image: {e}"
    
    def preprocess_image(self, image_path, output_path=None):
        """Preprocess image for better face detection"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Resize image if too large
            height, width = image.shape[:2]
            if width > 1024 or height > 1024:
                scale = min(1024/width, 1024/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Enhance contrast
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            if output_path:
                cv2.imwrite(output_path, enhanced)
                return output_path
            else:
                return enhanced
                
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
