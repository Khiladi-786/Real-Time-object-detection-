# Real-Time Object Detection with YOLO

This project implements real-time object detection using YOLO (You Only Look Once) with OpenCV.

## Features

- Real-time object detection from video files or webcam
- Proper error handling for missing files
- Automatic creation of default classes file
- Support for custom YOLO weights and configuration

## Requirements

- Python 3.7+
- OpenCV
- NumPy

## Installation

1. Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

## Setup

1. **Download YOLO files:**
   - Download `yolov3_training_last.weights` (or your custom weights file)
   - Download `yolov3_testing.cfg` (or your custom config file)
   - Place both files in the project directory

2. **Prepare your video:**
   - Place your video file as `test1.mp4` in the project directory
   - Or modify the `video_file` variable in the script to point to your video

3. **Classes file:**
   - The script will automatically create a `classes.txt` file with default classes if it doesn't exist
   - You can customize this file with your own class names

## Usage

Run the object detection script:

```bash
python3 Object_Detection.py
```

### Controls

- Press `q` or `ESC` to quit the application
- The script will display detected objects with bounding boxes and confidence scores

## File Structure

```
├── Object_Detection.py          # Main detection script
├── requirements.txt             # Python dependencies
├── classes.txt                  # Object class names (auto-created)
├── yolov3_training_last.weights # YOLO weights file (you need to download)
├── yolov3_testing.cfg          # YOLO config file (you need to download)
└── test1.mp4                   # Input video file (you need to provide)
```

## Customization

- **Video source:** Change the `video_file` variable to use a different video file
- **Webcam:** Change `video_file` to `0` to use your webcam
- **Confidence threshold:** Modify the `confidence > 0.2` condition
- **Classes:** Edit `classes.txt` to add/remove object classes
- **Colors:** Modify the `colors` array to change bounding box colors

## Troubleshooting

- **"Module not found" errors:** Make sure you're using `python3` and have installed the requirements
- **"Weights file not found":** Download the required YOLO weights file
- **"Video file not found":** Make sure your video file exists and the path is correct
- **Poor detection:** Try adjusting the confidence threshold or using different YOLO weights

## Notes

- The script automatically handles missing files with helpful error messages
- Default classes include common objects like person, car, bicycle, etc.
- The script uses Non-Maximum Suppression (NMS) to avoid duplicate detections
