# How to Run the Project Manually

## Step-by-Step Instructions

### 1. Navigate to the Project Directory
```bash
cd "/Users/nikhilpradipmore/real time object detection"
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

If you don't have a virtual environment, create one first:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

### 4. Run the Flask Server
```bash
python app.py
```

### 5. Open in Browser
Once you see:
```
* Running on http://127.0.0.1:8080
```

Open your web browser and go to:
- **http://127.0.0.1:8080/** or
- **http://localhost:8080/**

### 6. Stop the Server
Press `Ctrl+C` in the terminal

---

## Quick One-Line Commands

### Windows (Command Prompt):
```cmd
cd "real time object detection" && .venv\Scripts\activate && python app.py
```

### Mac/Linux:
```bash
cd "/Users/nikhilpradipmore/real time object detection" && source .venv/bin/activate && python app.py
```

---

## What to Expect

1. **Startup**: You'll see "YOLOv8 model loaded successfully with 80 classes"
2. **Server Running**: "Running on http://127.0.0.1:8080"
3. **In Browser**: 
   - Upload an image for detection
   - Click "Start Live Detection" for webcam

---

## Troubleshooting

- **Port 8080 already in use**: Change the port in `app.py` (line 274) from `8080` to another port like `5000`
- **Module not found**: Run `pip install -r requirements.txt`
- **Camera not working**: Check camera permissions in System Settings (macOS) or Privacy settings

