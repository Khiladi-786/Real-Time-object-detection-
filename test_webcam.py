import cv2
import numpy as np
import os

# Simple test script to check if webcam works
def test_webcam():
    cap = cv2.VideoCapture(0)  # Try webcam
    
    if not cap.isOpened():
        print("Webcam not available. Trying video file...")
        cap = cv2.VideoCapture('test1.mp4')
        if not cap.isOpened():
            print("No video source available!")
            return
    
    print("Video source opened successfully!")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Just show the video feed
        cv2.imshow('Test Video', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test completed!")

if __name__ == "__main__":
    test_webcam()
