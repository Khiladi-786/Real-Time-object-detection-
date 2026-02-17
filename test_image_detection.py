import cv2
import numpy as np
import os

def test_image_detection():
    # Check if required files exist
    weights_file = 'yolov3_training_last.weights'
    config_file = 'yolov3_testing.cfg'
    classes_file = 'classes.txt'
    image_file = 'test_image.jpg'
    
    if not os.path.exists(weights_file):
        print(f"Error: {weights_file} not found!")
        return
    
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found!")
        return
    
    if not os.path.exists(classes_file):
        print(f"Error: {classes_file} not found!")
        return
    
    if not os.path.exists(image_file):
        print(f"Error: {image_file} not found!")
        return
    
    # Load the YOLO network
    try:
        net = cv2.dnn.readNet(weights_file, config_file)
        print("YOLO network loaded successfully!")
    except Exception as e:
        print(f"Error loading YOLO network: {e}")
        return
    
    # Load class names
    classes = []
    try:
        with open(classes_file, "r") as f:
            classes = f.read().splitlines()
        print(f"Loaded {len(classes)} classes")
    except Exception as e:
        print(f"Error loading classes: {e}")
        return
    
    # Load image
    try:
        img = cv2.imread(image_file)
        if img is None:
            print(f"Error: Could not load image {image_file}")
            return
        print(f"Image {image_file} loaded successfully!")
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    height, width, _ = img.shape
    print(f"Image dimensions: {width}x{height}")
    
    # Create blob from image
    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)
    
    boxes = []
    confidences = []
    class_ids = []
    
    # Process detections
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)
                
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    print(f"Found {len(boxes)} potential detections")
    
    # Apply Non-Maximum Suppression
    if len(boxes) > 0:
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
        
        if len(indexes) > 0:
            print(f"After NMS: {len(indexes)} detections")
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                if class_ids[i] < len(classes):
                    label = str(classes[class_ids[i]])
                else:
                    label = f"Class_{class_ids[i]}"
                confidence = confidences[i]
                print(f"Detection: {label} (confidence: {confidence:.2f}) at ({x}, {y}, {w}, {h})")
        else:
            print("No detections after NMS")
    else:
        print("No detections found")

if __name__ == "__main__":
    test_image_detection()
