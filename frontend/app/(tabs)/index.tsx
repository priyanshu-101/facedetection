import React from 'react';
import { StatusBar } from 'expo-status-bar';
import FaceDetectionApp from '../../components/FaceDetection';


export default function App() {
  return (
    <>
      <FaceDetectionApp />
      <StatusBar style="auto" />
    </>
  );
}