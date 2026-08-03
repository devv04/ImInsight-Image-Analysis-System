from ultralytics import YOLO
from collections import Counter
import traceback
import cv2

# 🎯 Define relevant naval classes
ALLOWED_CLASSES = {
    "person", "boat", "ship", "helicopter", "truck", "backpack", "lifeboat", "naval officer",
    "suitcase", "aircraft carrier", "rifle", "submarine", "military vehicle"
}

_model = None

def get_yolo_model():
    global _model
    if _model is None:
        try:
            _model = YOLO("yolov8n.pt")  # Lightweight Nano model for low RAM environments
        except Exception as e:
            print("Failed to load YOLOv8n:", e)
            _model = None
    return _model


def detect_objects(image_path, conf_threshold=0.4, iou_threshold=0.6):
    try:
        model = get_yolo_model()
        if model is None:
            raise Exception("YOLO model not loaded properly.")


        results = model.predict(
            source=image_path,
            conf=conf_threshold,
            iou=iou_threshold,
            imgsz=640
        )[0]

        objects = []
        for box in results.boxes:
            label_index = int(box.cls)
            label = results.names.get(label_index, f"Unknown-{label_index}")

            # 🧼 Filter out non-naval objects
            if label not in ALLOWED_CLASSES:
                continue

            confidence = f"{box.conf.item() * 100:.1f}%"
            xyxy = box.xyxy[0].tolist()

            objects.append({
                "label": label,
                "confidence": confidence,
                "bbox": xyxy
            })

        summary = dict(Counter(obj["label"] for obj in objects))
        return {"objects_detected": objects, "summary": summary}

    except Exception as e:
        print("Object Detection Error:", e)
        traceback.print_exc()
        return {"error": f"Object detection failed: {str(e)}"}
