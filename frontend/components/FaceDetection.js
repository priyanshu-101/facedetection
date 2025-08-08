import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Image,
  Alert,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { CameraView, useCameraPermissions } from 'expo-camera';

const API_ENDPOINTS = {
  REGISTER: 'http://10.196.57.169:5000/api/register', 
  DETECT: 'http://10.196.57.169:5000/api/detect',     
};

const COLORS = {
  PRIMARY: '#007AFF',
  SUCCESS: '#28A745',
  ERROR: '#DC3545',
  BACKGROUND: '#F5F5F5',
  WHITE: '#FFFFFF',
  TEXT: '#333333',
  PLACEHOLDER: '#999999',
};

const FaceDetection = () => {
  const [name, setName] = useState('');
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraVisible, setCameraVisible] = useState(false);
  const [camera, setCamera] = useState(null);
  const [permission, requestPermission] = useCameraPermissions();

  useEffect(() => {
    requestMediaPermissions();
  }, []);

  const requestMediaPermissions = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Media library permission is required');
      }
    } catch (error) {
      console.error('Media permission error:', error);
    }
  };

  const uploadPhoto = useCallback(async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
        allowsMultipleSelection: false,
      });

      console.log('Image picker result:', result);

      if (!result.canceled && result.assets?.length > 0) {
        const asset = result.assets[0];
        console.log('Selected asset details:', asset);
        
        const selectedImage = {
          uri: asset.uri,
          type: asset.mimeType || 'image/jpeg',
          name: asset.fileName || 'photo.jpg',
        };
        
        console.log('Processed image object:', selectedImage);
        setPhoto(selectedImage);
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Failed to pick image');
    }
  }, []);

  const registerUser = useCallback(async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter a name');
      return;
    }

    if (!photo) {
      Alert.alert('Error', 'Please upload a photo');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('name', name.trim());
      
      formData.append('photo', {
        uri: photo.uri,
        type: photo.type,
        name: photo.name,
      });

      console.log('Sending registration request to:', API_ENDPOINTS.REGISTER);

      const response = await fetch(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Registration result:', result);

      Alert.alert('Success', result.message || 'User registered successfully!');
      setName('');
      setPhoto(null);
    } catch (error) {
      console.error('Registration error:', error);
      Alert.alert('Error', `Registration failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [name, photo]);

  const openDetectionCamera = useCallback(async () => {
    try {
      if (!permission) {
        console.log('Requesting camera permission...');
        const response = await requestPermission();
        if (!response?.granted) {
          Alert.alert('Permission Required', 'Camera permission is required for detection');
          return;
        }
      }
      
      if (!permission?.granted) {
        console.log('Camera permission not granted, requesting...');
        const response = await requestPermission();
        if (!response?.granted) {
          Alert.alert('Permission Required', 'Camera permission is required for detection');
          return;
        }
      }
      
      console.log('Opening camera for detection...');
      setCameraVisible(true);
    } catch (error) {
      console.error('Camera permission error:', error);
      Alert.alert('Error', 'Failed to access camera');
    }
  }, [permission, requestPermission]);

  const captureAndDetect = useCallback(async () => {
    if (!camera) {
      Alert.alert('Error', 'Camera not ready');
      return;
    }

    try {
      setLoading(true);
      console.log('Capturing image for detection...');
      
      const captured = await camera.takePictureAsync({
        quality: 0.8,
        base64: false,
        skipProcessing: false,
      });

      if (!captured || !captured.uri) {
        throw new Error('Failed to capture image');
      }

      console.log('Captured image:', captured);

      // Create form data with the correct format for React Native
      const formData = new FormData();
      
      // Use the exact format that React Native expects for file uploads
      formData.append('photo', {
        uri: captured.uri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });

      console.log('FormData created with photo field');
      console.log('Sending detection request to:', API_ENDPOINTS.DETECT);

      // Add timeout to the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.log('Request timed out after 30 seconds');
      }, 30000); // 30 second timeout

      const response = await fetch(API_ENDPOINTS.DETECT, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearTimeout(timeoutId);
      console.log('Response received:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.log('Error response body:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Detection result:', JSON.stringify(result, null, 2));

      // Handle the actual backend response format
      if (result.faces_detected > 0) {
        if (result.recognition && result.recognition.recognized === true) {
          // User recognized successfully
          Alert.alert(
            'Recognition Successful! ',
            `Welcome back, ${result.recognition.user_name}!\n\nConfidence: ${(result.recognition.confidence * 100).toFixed(1)}%\nMethod: ${result.recognition.method}`
          );
        } else {
          // Face detected but not recognized
          const message = result.recognition?.message || 'Face detected but not recognized';
          Alert.alert(
            'Face Detected',
            `${message}\n\nPlease register first or try again with better lighting.`
          );
        }
      } else {
        Alert.alert('No Face Detected 😞', 'Please ensure your face is clearly visible and try again.');
      }

      setCameraVisible(false);
      setCamera(null);
    } catch (error) {
      console.error('Detection error details:', error);
      
      if (error.name === 'AbortError') {
        Alert.alert('Error', 'Request timed out. Please check your network connection.');
      } else if (error.message.includes('Network request failed')) {
        Alert.alert('Error', 'Network error. Please check if the server is running and accessible.');
      } else {
        Alert.alert('Error', `Detection failed: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [camera]);



  const closeCameraHandler = useCallback(() => {
    setCameraVisible(false);
    setCamera(null);
  }, []);

  const onCameraReady = useCallback(() => {
    console.log('Camera is ready');
  }, []);

  if (cameraVisible) {
    return (
      <View style={styles.cameraContainer}>
        <CameraView
          style={styles.camera}
          ref={setCamera}
          facing="front"
          onCameraReady={onCameraReady}
        >
          <View style={styles.cameraButtonContainer}>
            <TouchableOpacity
              style={styles.captureButton}
              onPress={captureAndDetect}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.captureButtonText}>Detect</Text>
              )}
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.closeCameraButton}
              onPress={closeCameraHandler}
            >
              <Text style={styles.closeCameraButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Face Detection App</Text>

      <View style={styles.formContainer}>
        <Text style={styles.label}>Name</Text>
        <TextInput
          style={styles.input}
          value={name}
          onChangeText={setName}
          placeholder="Enter your name"
          placeholderTextColor={COLORS.PLACEHOLDER}
        />

        <Text style={styles.label}>Photo</Text>
        <TouchableOpacity style={styles.photoUploadButton} onPress={uploadPhoto}>
          {photo ? (
            <Image source={{ uri: photo.uri }} style={styles.uploadedPhoto} />
          ) : (
            <Text style={styles.uploadButtonText}>Upload Photo</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.registerButton, loading && styles.buttonDisabled]}
          onPress={registerUser}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Register</Text>
          )}
        </TouchableOpacity>

        <View style={styles.separator} />

        <TouchableOpacity
          style={styles.detectionButton}
          onPress={openDetectionCamera}
        >
          <Text style={styles.buttonText}>Start Detection</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: COLORS.BACKGROUND,
    padding: 20,
    paddingTop: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: COLORS.TEXT,
  },
  formContainer: {
    backgroundColor: COLORS.WHITE,
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: COLORS.TEXT,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#fafafa',
  },
  photoUploadButton: {
    borderWidth: 2,
    borderColor: COLORS.PRIMARY,
    borderStyle: 'dashed',
    borderRadius: 10,
    height: 150,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: '#f9f9f9',
  },
  uploadButtonText: {
    color: COLORS.PRIMARY,
    fontSize: 16,
    fontWeight: '600',
  },
  uploadedPhoto: {
    width: '100%',
    height: '100%',
    borderRadius: 10,
  },
  registerButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  detectionButton: {
    backgroundColor: COLORS.SUCCESS,
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  separator: {
    height: 1,
    backgroundColor: '#ddd',
    marginVertical: 20,
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: 'black',
  },
  camera: {
    flex: 1,
  },
  cameraButtonContainer: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-end',
    paddingBottom: 50,
    paddingHorizontal: 20,
  },
  captureButton: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 50,
    padding: 20,
    marginRight: 20,
    minWidth: 80,
    alignItems: 'center',
  },
  captureButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  closeCameraButton: {
    backgroundColor: COLORS.ERROR,
    borderRadius: 50,
    padding: 20,
    minWidth: 80,
    alignItems: 'center',
  },
  closeCameraButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default FaceDetection;