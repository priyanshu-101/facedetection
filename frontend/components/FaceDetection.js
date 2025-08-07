import React, { useState, useEffect } from 'react';
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
import { Camera, useCameraPermissions } from 'expo-camera';
import { API_ENDPOINTS, COLORS } from './constants';

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
    await ImagePicker.requestMediaLibraryPermissionsAsync();
  };

  const uploadPhoto = async () => {
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
        
        // Create a proper file object for React Native FormData
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
  };

  const registerUser = async () => {
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
      
      // FIXED: Use the third parameter for filename in React Native
      formData.append('photo', {
        uri: photo.uri,
        type: photo.type,
        name: photo.name,
      }, photo.name);

      const response = await fetch(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        Alert.alert('Success', result.message || 'User registered successfully!');
        setName('');
        setPhoto(null);
      } else {
        Alert.alert('Error', result.error || result.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      Alert.alert('Error', 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const openDetectionCamera = async () => {
    if (!permission) return;
    if (!permission.granted) {
      const response = await requestPermission();
      if (!response.granted) {
        Alert.alert('Permission Required', 'Camera permission is required for detection');
        return;
      }
    }
    setCameraVisible(true);
  };

  const captureAndDetect = async () => {
    if (camera) {
      try {
        setLoading(true);
        const captured = await camera.takePictureAsync({
          quality: 0.8,
          base64: false,
        });

        const formData = new FormData();
        formData.append('image', {
          uri: captured.uri,
          type: 'image/jpeg',
          name: 'detection.jpg',
        });

        const response = await fetch(API_ENDPOINTS.DETECT, {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          Alert.alert(
            'Detection Result',
            result.detected ? `Face detected: ${result.name}` : 'No face detected'
          );
        } else {
          Alert.alert('Error', result.message || 'Detection failed');
        }

        setCameraVisible(false);
      } catch (_error) {
        Alert.alert('Error', 'Detection failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  if (cameraVisible) {
    return (
      <View style={styles.cameraContainer}>
        <Camera
          style={styles.camera}
          ref={setCamera}
          facing="front"
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
              onPress={() => setCameraVisible(false)}
            >
              <Text style={styles.closeCameraButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </Camera>
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
