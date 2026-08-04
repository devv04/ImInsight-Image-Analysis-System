import os
import requests
import base64

# Hugging Face Zero-Shot Image Classification API
API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"

def classify_image(image_path, label_list, top_k=1):
    """
    Zero-shot classification using Hugging Face Free Inference API.
    """
    hf_token = os.environ.get("HF_API_TOKEN")
    if not hf_token:
        print("Warning: HF_API_TOKEN is not set.")
        return {"label": "HF_API_TOKEN not set", "confidence": 0.0}

    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
            
        payload = {
            "inputs": image_data,
            "parameters": {"candidate_labels": label_list}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 503:
            # Model is loading on HF servers
            print("CLIP Model is loading on HF...")
            return {"label": "Model is warming up, try again in 10s", "confidence": 0.0}
            
        response.raise_for_status()
        results = response.json()
        
        if isinstance(results, list) and len(results) > 0:
            best = results[0]
            return {"label": best.get("label", "Unknown"), "confidence": best.get("score", 0.0)}
            
        return {"label": "Unknown", "confidence": 0.0}

    except Exception as e:
        print("CLIP API Error:", e)
        return {"label": "Unknown", "confidence": 0.0}
