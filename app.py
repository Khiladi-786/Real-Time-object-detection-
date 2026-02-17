
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS



import cv2
import numpy as np
import os
import base64
import io
from PIL import Image
import json
import threading
import time
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# Global variables for YOLO model (YOLOv8)
yolo_model = None
classes = []
colors = None

# Global variables for live detection
camera = None
detection_active = False

def open_camera():
    """Try to open a webcam using several indices and backends (helps on macOS)."""
    # Common indices to try
    indices = [0, 1, 2, 3]
    # Try default backend first
    for idx in indices:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            return cap
    # On macOS, also try AVFoundation backend explicitly
    if hasattr(cv2, 'CAP_AVFOUNDATION'):
        for idx in indices:
            cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
            if cap.isOpened():
                return cap
    # As a final fallback
    return cv2.VideoCapture(0)

def load_yolo_model():
    """Load YOLOv8 model and class names."""
    global yolo_model, classes, colors
    
    try:
        if yolo_model is None:
            # Use local model if present, otherwise let Ultralytics auto-download a small model
            default_model_path = 'yolov8n.pt'
            model_path = default_model_path if os.path.exists(default_model_path) else 'yolov8n.pt'
            yolo_model = YOLO(model_path)
            
            # Derive class names from model
            names_dict = yolo_model.model.names if hasattr(yolo_model, 'model') else yolo_model.names
            # names_dict maps id->name
            classes = [names_dict[i] for i in sorted(names_dict.keys())]
            colors = np.random.uniform(0, 255, size=(len(classes), 3))
            return True, f"YOLOv8 model loaded successfully with {len(classes)} classes"
        else:
            return True, f"YOLOv8 model already loaded with {len(classes)} classes"
    except Exception as e:
        return False, f"Error loading YOLOv8 model: {str(e)}"

def detect_objects(image):
    """Detect objects in the given image using YOLOv8."""
    global yolo_model, classes, colors
    
    if yolo_model is None:
        return None, "YOLOv8 model not loaded"
    
    try:
        results = yolo_model(image, conf=0.25, iou=0.45, imgsz=640, verbose=False)
        detections = []
        annotated = image.copy()
        if len(results) > 0:
            r = results[0]
            if hasattr(r, 'boxes') and r.boxes is not None:
                for box in r.boxes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy.tolist()
                    w = x2 - x1
                    h = y2 - y1
                    conf = float(box.conf[0].cpu().item()) if box.conf is not None else 0.0
                    cls_id = int(box.cls[0].cpu().item()) if box.cls is not None else 0
                    label = r.names.get(cls_id, f"Class_{cls_id}") if hasattr(r, 'names') else (classes[cls_id] if cls_id < len(classes) else f"Class_{cls_id}")
                    detections.append({
                        'label': label,
                        'confidence': round(conf, 2),
                        'bbox': [int(x1), int(y1), int(w), int(h)]
                    })
                    color = colors[cls_id % len(colors)] if colors is not None else (0, 255, 0)
                    cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(annotated, f"{label} {conf:.2f}", (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        return annotated, detections
    except Exception as e:
        return None, f"Error during detection: {str(e)}"

def detect_objects_live(image):
    """Detect objects in live video frame using YOLOv8."""
    global yolo_model, classes, colors
    
    if yolo_model is None:
        return image, []
    
    try:
        results = yolo_model(image, conf=0.30, iou=0.45, imgsz=640, verbose=False)
        detections = []
        annotated = image.copy()
        if len(results) > 0:
            r = results[0]
            if hasattr(r, 'boxes') and r.boxes is not None:
                for box in r.boxes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy.tolist()
                    w = x2 - x1
                    h = y2 - y1
                    conf = float(box.conf[0].cpu().item()) if box.conf is not None else 0.0
                    cls_id = int(box.cls[0].cpu().item()) if box.cls is not None else 0
                    label = r.names.get(cls_id, f"Class_{cls_id}") if hasattr(r, 'names') else (classes[cls_id] if cls_id < len(classes) else f"Class_{cls_id}")
                    detections.append({
                        'label': label,
                        'confidence': round(conf, 2),
                        'bbox': [int(x1), int(y1), int(w), int(h)]
                    })
                    color = colors[cls_id % len(colors)] if colors is not None else (0, 255, 0)
                    cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(annotated, f"{label} {conf:.2f}", (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        return annotated, detections
    except Exception:
        return image, []

def generate_frames():
    """Generate video frames with object detection"""
    global camera, detection_active
    
    while detection_active:
        success, frame = camera.read()
        if not success or frame is None:
            time.sleep(0.05)
            continue
        
        # Detect objects in the frame
        frame_with_detections, detections = detect_objects_live(frame)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame_with_detections)
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Small delay to control frame rate
        time.sleep(0.03)  # ~30 FPS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and object detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        image_data = file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Detect objects
        result_image, detections = detect_objects(image.copy())
        
        if result_image is None:
            return jsonify({'error': detections}), 400
        
        # Convert result image to base64
        _, buffer = cv2.imencode('.jpg', result_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': image_base64,
            'detections': detections
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Check YOLO model status"""
    success, message = load_yolo_model()
    return jsonify({
        'success': success,
        'message': message,
        'classes_loaded': len(classes) if classes else 0
    })

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_live_detection', methods=['POST'])
def start_live_detection():
    """Start live object detection"""
    global camera, detection_active
    
    try:
        # Make this endpoint idempotent: if already active, respond success so UI can proceed
        if detection_active:
            # Ensure camera is available
            if camera is None or not camera.isOpened():
                camera = open_camera()
            return jsonify({'success': True, 'message': 'Detection already active'})
        
        # Initialize camera with robust fallback
        camera = open_camera()
        if not camera.isOpened():
            return jsonify({'success': False, 'message': 'Could not access camera'})
        
        detection_active = True
        return jsonify({'success': True, 'message': 'Live detection started'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting detection: {str(e)}'})

@app.route('/stop_live_detection', methods=['POST'])
def stop_live_detection():
    """Stop live object detection"""
    global camera, detection_active
    
    try:
        detection_active = False
        if camera is not None:
            camera.release()
            camera = None
        
        return jsonify({'success': True, 'message': 'Live detection stopped'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping detection: {str(e)}'})

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Load YOLO model on startup
    success, message = load_yolo_model()
    print(f"YOLO Model Status: {message}")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
