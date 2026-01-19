import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image

# Internal ML modules
from model.clip_utils import classify_image
from model.object_detection import detect_objects
from model.blip_caption import generate_caption
from model.anomaly_detector import detect_anomalies

# Supported image formats
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}

# Flask setup
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Domain-specific label sets (for zero-shot classification)
LABEL_SETS = {
    "ground": [
        "infantry soldier", "sniper", "camouflage gear", "rocket launcher", "RPG operator",
        "combat training", "military exercise", "bulletproof vest", "military base",
        "tank", "urban warfare", "army officer", "radio operator"
    ],
    "naval": [
        "aircraft carrier", "destroyer", "frigate", "submarine", "fighter jet", "drone",
        "cargo ship", "tanker", "patrol boat", "helicopter", "missile", "torpedo",
        "lifeboat", "supply vessel", "amphibious assault ship", "crew member",
        "naval officer", "naval base", "naval exercise", "naval patrol",
        "naval surveillance", "naval operation", "naval fleet", "naval patrol aircraft"
    ],
    "aerial": [
        "fighter jet", "drone", "helicopter", "radar", "missile launch", "airstrike zone",
        "reconnaissance aircraft", "military UAV", "jet pilot"
    ]
}

# Alert keywords (includes warship)
ALERT_KEYWORDS = ["unauthorized", "hazard", "enemy", "unknown", "warship"]


def count_people(objects):
    return sum(1 for obj in objects if obj.get("label", "").strip().lower() == "person")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        return jsonify({'error': f'Format "{file_ext}" not supported. Accepted: JPG, PNG, TIFF, BMP.'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    try:
        img = Image.open(file_path)
        file_info = {
            'filename': filename,
            'size': img.size,
            'format': img.format,
            'message': 'Image received and analyzed successfully for military surveillance.'
        }

        # Context and label set
        context = request.form.get("context", "ground").strip().lower()
        labels = LABEL_SETS.get(context, LABEL_SETS["ground"])

        # Classification (confidence removed)
        classification = classify_image(file_path, labels) or {}
        classification_payload = {
            "label": classification.get("label", "Unknown")
        }

        # Captioning
        try:
            caption_result = generate_caption(file_path, style_prompt="", max_new_tokens=60) or {}
        except Exception:
            caption_result = {"label": "Caption generation failed"}

        caption_payload = {"text": caption_result.get("label", "No caption")}
        if caption_result.get("object_count") not in (None, "N/A"):
            caption_payload["object_count"] = caption_result["object_count"]

        # Object detection
        detections = detect_objects(file_path, conf_threshold=0.4, iou_threshold=0.6) or {}
        objects_detected = detections.get("objects_detected", [])
        summary = detections.get("summary", {})

        # Count people
        person_count = count_people(objects_detected)

        # Anomaly detection
        anomalies = detect_anomalies(file_path, summary, objects_detected) or {}
        anomalies_list = anomalies.get("anomalies_detected", [])
        anomaly_count = anomalies.get("count", len(anomalies_list))

        # High person count anomaly
        if person_count > 8 and not any(
            isinstance(a, dict) and a.get("type") == "person_count_threshold" for a in anomalies_list
        ):
            anomalies_list.append({
                "type": "person_count_threshold",
                "description": f"High human presence: {person_count} persons detected (threshold 8)",
                
            })
            anomaly_count += 1

        # Warship anomaly
        warship_present = any("warship" in obj.get("label", "").lower() for obj in objects_detected)
        if warship_present and not any(
            isinstance(a, dict) and a.get("type") == "warship_detected" for a in anomalies_list
        ):
            anomalies_list.append({
                "type": "warship_detected",
                "description": "Warship detected in scene",
                "severity": "high",
                "reason": "Presence of warship triggers critical alert"
            })
            anomaly_count += 1

        # Keyword alert logic
        is_keyword_alert = any(
            any(keyword in str(anomaly).lower() for keyword in ALERT_KEYWORDS)
            for anomaly in anomalies_list
        )

        status = 'Nominal' if anomaly_count == 0 else 'Alert'
        priority = 'Low' if status == 'Nominal' else ('Critical' if is_keyword_alert else 'High')
        recommendation = 'Monitor' if anomaly_count == 0 else 'Investigate and report to command'

        # Military assessment
        naval_assessment = {
            'status': status,
            'priority': priority,
            'recommendation': recommendation
        }

        return jsonify({
            'classification': classification_payload,
            'caption': caption_payload,
            'detections': {
                **detections,
                'person_count': person_count
            },
            'anomalies_detected': {
                'anomalies_detected': anomalies_list,
                'count': anomaly_count
            },
            'military_assessment': naval_assessment,
            'naval_assessment': naval_assessment,
            'file_info': file_info
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Analysis Failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
