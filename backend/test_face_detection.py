#!/usr/bin/env python3
"""
Test script for debugging face detection issues
"""
import os
import sys
import cv2
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_opencv_detection(image_path):
    """Test basic OpenCV face detection"""
    print(f"\n=== Testing OpenCV Face Detection ===")
    print(f"Image path: {image_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"ERROR: Image file does not exist: {image_path}")
            return False
        
        # Check OpenCV installation
        print(f"OpenCV Version: {cv2.__version__}")
        
        # Load cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        print(f"Cascade path: {cascade_path}")
        
        if not os.path.exists(cascade_path):
            print(f"ERROR: Cascade file not found: {cascade_path}")
            return False
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            print("ERROR: Could not load face cascade classifier")
            return False
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"ERROR: Could not load image: {image_path}")
            return False
        
        print(f"Image loaded successfully. Shape: {image.shape}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(f"Grayscale conversion successful. Shape: {gray.shape}")
        
        # Apply histogram equalization
        gray_eq = cv2.equalizeHist(gray)
        
        # Try different detection parameters
        detection_params = [
            {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (30, 30), 'name': 'Default'},
            {'scaleFactor': 1.05, 'minNeighbors': 4, 'minSize': (20, 20), 'name': 'Sensitive'},
            {'scaleFactor': 1.2, 'minNeighbors': 6, 'minSize': (40, 40), 'name': 'Large faces'},
            {'scaleFactor': 1.3, 'minNeighbors': 3, 'minSize': (15, 15), 'name': 'Very sensitive'},
            {'scaleFactor': 1.1, 'minNeighbors': 2, 'minSize': (10, 10), 'name': 'Ultra sensitive'}
        ]
        
        faces_found = False
        for params in detection_params:
            name = params.pop('name')
            print(f"\nTrying {name} parameters: {params}")
            
            # Test on original grayscale
            faces = face_cascade.detectMultiScale(gray, **params)
            print(f"  Original gray: {len(faces)} faces detected")
            if len(faces) > 0:
                faces_found = True
                print(f"  Face locations: {faces.tolist()}")
            
            # Test on equalized image
            faces_eq = face_cascade.detectMultiScale(gray_eq, **params)
            print(f"  Equalized gray: {len(faces_eq)} faces detected")
            if len(faces_eq) > 0:
                faces_found = True
                print(f"  Face locations: {faces_eq.tolist()}")
        
        if faces_found:
            print("\n✅ SUCCESS: At least one face detected!")
        else:
            print("\n❌ FAILURE: No faces detected with any parameters")
        
        return faces_found
        
    except Exception as e:
        print(f"ERROR during face detection test: {e}")
        traceback.print_exc()
        return False

def test_face_service():
    """Test the face service classes"""
    print(f"\n=== Testing Face Services ===")
    
    try:
        # Test importing face services
        print("Testing face_recognition service...")
        try:
            from services.face_service import FaceService
            face_service = FaceService()
            print("✅ face_recognition service imported successfully")
            service_type = "advanced"
        except ImportError as e:
            print(f"❌ face_recognition service failed: {e}")
            face_service = None
            service_type = None
        
        print("Testing OpenCV-only service...")
        try:
            from services.face_service_opencv import FaceServiceOpenCV
            opencv_service = FaceServiceOpenCV()
            print("✅ OpenCV service imported successfully")
            if service_type is None:
                face_service = opencv_service
                service_type = "opencv"
        except ImportError as e:
            print(f"❌ OpenCV service failed: {e}")
            if service_type is None:
                return False
        
        print(f"Using service type: {service_type}")
        return face_service, service_type
        
    except Exception as e:
        print(f"ERROR testing face services: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Face Detection Debug Tool ===")
    
    # Test face services
    service_result = test_face_service()
    if not service_result:
        print("❌ Face service test failed")
        return
    
    face_service, service_type = service_result
    
    # Test with a sample image if provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"\nTesting with provided image: {image_path}")
        
        # Test basic OpenCV detection
        opencv_result = test_opencv_detection(image_path)
        
        # Test face service validation
        print(f"\n=== Testing Face Service Validation ===")
        try:
            is_valid, message = face_service.validate_image(image_path)
            print(f"Face service validation: {is_valid}")
            print(f"Message: {message}")
            
            if is_valid:
                # Test face encoding extraction
                print(f"\n=== Testing Face Encoding Extraction ===")
                encoding = face_service.extract_face_encoding(image_path)
                if encoding is not None:
                    if isinstance(encoding, dict):
                        print(f"✅ Face encoding extracted (OpenCV): keys = {list(encoding.keys())}")
                    else:
                        print(f"✅ Face encoding extracted (face_recognition): shape = {encoding.shape}")
                else:
                    print("❌ Failed to extract face encoding")
            
        except Exception as e:
            print(f"ERROR testing face service: {e}")
            traceback.print_exc()
    
    else:
        print("\nUsage: python test_face_detection.py <image_path>")
        print("Example: python test_face_detection.py uploads/test_image.jpg")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
