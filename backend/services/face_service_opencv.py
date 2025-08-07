import cv2
import numpy as np
from PIL import Image
import os
import pickle

class FaceServiceOpenCV:
    """
    Alternative face service using only OpenCV for face detection and basic recognition.
    This version doesn't require the face_recognition library or Visual C++ build tools.
    """
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Remove the face recognizer that requires opencv-contrib-python
        # self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.encodings_file = 'face_encodings.pkl'
        self.user_labels = {}
        self.next_label = 0
        self.load_face_data()
    
    def detect_faces_opencv(self, image_path):
        """Detect faces using OpenCV with multiple detection methods"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization to improve detection
            gray = cv2.equalizeHist(gray)
            
            # Try multiple scale factors and parameters for better detection
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
        """Extract face features using OpenCV (returns face region and histogram)"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return None
            
            # Use the largest face
            (x, y, w, h) = max(faces, key=lambda face: face[2] * face[3])
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Resize to standard size
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Calculate histogram as feature vector
            hist = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
            hist = hist.flatten()
            
            # Normalize
            hist = hist / (np.sum(hist) + 1e-7)
            
            return {
                'face_region': face_roi,
                'histogram': hist,
                'coordinates': (x, y, w, h)
            }
            
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def compare_faces_opencv(self, known_encodings, unknown_encoding, tolerance=0.5):
        """Compare face encodings using histogram correlation"""
        try:
            if not known_encodings or unknown_encoding is None:
                return {'matches': [], 'distances': []}
            
            unknown_hist = unknown_encoding['histogram']
            matches = []
            distances = []
            
            for encoding in known_encodings:
                if isinstance(encoding, dict) and 'histogram' in encoding:
                    known_hist = encoding['histogram']
                    
                    # Calculate correlation coefficient
                    correlation = cv2.compareHist(
                        known_hist.astype(np.float32), 
                        unknown_hist.astype(np.float32), 
                        cv2.HISTCMP_CORREL
                    )
                    
                    # Convert correlation to distance (lower is better)
                    distance = 1 - correlation
                    distances.append(distance)
                    matches.append(distance < tolerance)
                else:
                    distances.append(1.0)
                    matches.append(False)
            
            return {
                'matches': matches,
                'distances': distances
            }
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return {'matches': [], 'distances': []}
    
    def find_best_match(self, known_encodings, unknown_encoding, user_names, tolerance=0.5):
        """Find the best matching face using OpenCV"""
        try:
            comparison_result = self.compare_faces_opencv(known_encodings, unknown_encoding, tolerance)
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
                    'confidence': 1 - best_distance,
                    'distance': best_distance
                }
            
            return None
            
        except Exception as e:
            print(f"Error finding best match: {e}")
            return None
    
    def train_face_recognizer(self, faces, labels):
        """Train the LBPH face recognizer - disabled (requires opencv-contrib-python)"""
        print("Face recognizer training is disabled - requires opencv-contrib-python")
        return False
    
    def save_face_data(self):
        """Save face encodings and labels to file"""
        try:
            data = {
                'user_labels': self.user_labels,
                'next_label': self.next_label
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving face data: {e}")
    
    def load_face_data(self):
        """Load face encodings and labels from file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.user_labels = data.get('user_labels', {})
                    self.next_label = data.get('next_label', 0)
        except Exception as e:
            print(f"Error loading face data: {e}")
    
    def validate_image(self, image_path):
        """Validate if the image is valid and contains a face"""
        try:
            if not os.path.exists(image_path):
                return False, "Image file does not exist"
            
            try:
                image = cv2.imread(image_path)
                if image is None:
                    return False, "Invalid image format"
            except Exception:
                return False, "Cannot read image file"
            
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
