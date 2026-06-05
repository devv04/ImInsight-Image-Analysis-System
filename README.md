# ImInsight Image Analysis System

**ImInsight** is an AI-powered image analysis and surveillance dashboard designed to perform advanced reconnaissance, military, and naval visual intelligence. It combines several state-of-the-art machine learning models into a unified interface for captioning, classification, object detection, and anomaly flagging.

## 🚀 Features

- **Zero-Shot Classification** using OpenAI's CLIP model to determine the scene context (e.g., ground vs naval vs aerial).
- **Advanced Object Detection** powered by **YOLOv8x**, with interactive coordinate mapping and bounding box visualization overlaid directly onto the uploaded images in the frontend.
- **Image Captioning** utilizing Salesforce's BLIP to generate descriptive intelligence reports.
- **Anomaly Detection**, analyzing bounding box limits, person counts, and identifying high-priority targets (e.g., warships or unauthorized personnel).
- **Responsive Dashboard** built with React, Vite, and Tailwind CSS.

## 📂 Project Structure

- `/backend`: A Flask-based REST API that hosts the machine learning inference logic.
- `/frontend`: A React/Vite-based Single Page Application (SPA) offering an intuitive drag-and-drop analytics dashboard.

---

## 🛠️ Setup Instructions'

### 1. Backend Integration (Python/Flask)
The backend utilizes PyTorch, Transformers, and Ultralytics YOLO. It requires a virtual environment to manage dependencies safely.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# Start the Flask development server on port 5000
python app.py
```

*Note: The first time you upload an image for analysis, the backend will download the necessary pre-trained weights (YOLOv8x, BLIP, CLIP), which may take several minutes depending on your internet connection.*

### 2. Frontend Integration (React/Vite)
The frontend uses Vite for lightning-fast bundling. You will need Node.js and `npm` installed.

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to access the ImInsight dashboard.

## 📝 Usage

1. Launch both the backend server and the frontend application using the instructions above.
2. Navigate to the frontend UI and upload an image (JPG, PNG).
3. Wait for the `Analyzing...` progress bar to finish processing.
4. View the Intelligence Report, including contextual classification, the generated caption, real-time object bounding boxes dynamically drawn over the image, and any detected anomalies and naval baseline assessments.

---
*Developed by the Deepmind Advanced Agentic Coding Team as an example AI utility project.*
