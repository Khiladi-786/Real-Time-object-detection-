import cv2
import numpy as np
import os

# Check if required files exist
weights_file = 'yolov3_training_last.weights'
config_file = 'yolov3_testing.cfg'
classes_file = 'classes.txt'
video_file = 'test1.mp4'

if not os.path.exists(weights_file):
    print(f"Error: {weights_file} not found!")
    print("Please download the YOLO weights file or update the filename.")
    exit()

if not os.path.exists(config_file):
    print(f"Error: {config_file} not found!")
    print("Please download the YOLO config file or update the filename.")
    exit()

if not os.path.exists(classes_file):
    print(f"Error: {classes_file} not found!")
    print("Creating a default classes.txt file...")
    # Create default classes file
    default_classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat']
    with open(classes_file, 'w') as f:
        for class_name in default_classes:
            f.write(f"{class_name}\n")
    print("Default classes.txt file created!")

if not os.path.exists(video_file):
    print(f"Error: {video_file} not found!")
    print("Please provide a video file or update the filename.")
    print("You can also use your webcam by changing the video source to 0")
    exit()

# Load the YOLO network
try:
    net = cv2.dnn.readNet(weights_file, config_file)
    print("YOLO network loaded successfully!")
except Exception as e:
    print(f"Error loading YOLO network: {e}")
    exit()

# Load class names
classes = []
try:
    with open(classes_file, "r") as f:
        classes = f.read().splitlines()
    print(f"Loaded {len(classes)} classes")
except Exception as e:
    print(f"Error loading classes: {e}")
    exit()

# Initialize video capture
try:
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_file}")
        exit()
    print(f"Video file {video_file} opened successfully!")
except Exception as e:
    print(f"Error opening video: {e}")
    exit()
font = cv2.FONT_HERSHEY_PLAIN
colors = np.random.uniform(0, 255, size=(100, 3))

print("Starting object detection... Press 'q' to quit, 'ESC' to quit")

while True:
    ret, img = cap.read()
    
    if not ret:
        print("End of video or failed to read frame")
        break
    
    height, width, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

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
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    # Only apply NMS if we have detections
    if len(boxes) > 0:
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
        
        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                if class_ids[i] < len(classes):
                    label = str(classes[class_ids[i]])
                else:
                    label = f"Class_{class_ids[i]}"
                confidence = str(round(confidences[i],2))
                color = colors[class_ids[i] % len(colors)]
                cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                cv2.putText(img, label + " " + confidence, (x, y+20), font, 2, (255,255,255), 2)

    cv2.imshow('Object Detection', img)
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):  # ESC or 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()


