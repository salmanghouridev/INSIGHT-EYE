'use client'
import React, { useEffect, useState, useRef } from 'react';
import Webcam from 'react-webcam';
import * as faceapi from 'face-api.js';

function WebcamFaceDetection() {
  const [isClient, setIsClient] = useState(false);
  const [faceDistance, setFaceDistance] = useState<number | null>(null);
  const webcamRef = useRef<Webcam | null>(null);

  useEffect(() => {
    setIsClient(true);
    loadModels();
  }, []);

  const loadModels = async () => {
    await faceapi.nets.tinyFaceDetector.load('/models');
    startFaceDetection();
  };

  const startFaceDetection = () => {
    setInterval(async () => {
      const video = webcamRef.current?.video as HTMLVideoElement;
      if (video && video.readyState === 4) {
        const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());
        if (detections.length > 0) {
          const distance = calculateFaceDistance(detections[0].box.width);
          setFaceDistance(distance);
        } else {
          setFaceDistance(null);
        }
      }
    }, 1000);
  };

  const calculateFaceDistance = (width: number): number => {
    // Convert the width from pixels to centimeters based on some conversion factor
    const conversionFactor = 0.0264583333; // Example conversion factor for webcam
    const distanceInCentimeters = width * conversionFactor * 2.54; // Convert inches to centimeters
    return distanceInCentimeters;
  };

  return isClient ? (
    <div className="container">
      <Webcam audio={false} ref={webcamRef} height={600} width={600} />
      {faceDistance && <p>Face distance: {faceDistance.toFixed(2)} cm</p>}
    </div>
  ) : null;
}

export default WebcamFaceDetection;