import os
import requests

# Hugging Face Image Captioning API
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

def generate_caption(image_path, prompt=None, style_prompt=None, max_new_tokens=50):
    hf_token = os.environ.get("HF_API_TOKEN")
    if not hf_token:
        print("Warning: HF_API_TOKEN is not set.")
        return {"label": "HF_API_TOKEN not set", "confidence": 0.0}

    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        
        response = requests.post(API_URL, headers=headers, data=data, timeout=30)
        
        if response.status_code == 503:
            print("BLIP Model is loading on HF...")
            return {"label": "Caption model warming up, try again in 10s", "confidence": 0.0}
            
        response.raise_for_status()
        result = response.json()
        
        caption = result[0].get("generated_text", "").strip() if isinstance(result, list) else ""

        # Apply prefix if given
        prefix = style_prompt.strip() if style_prompt else (prompt.strip() if prompt else None)
        if prefix:
            caption = f"{prefix} {caption}"

        return {"label": caption, "confidence": None}

    except Exception as e:
        print("BLIP API Error:", e)
        return {"label": "Caption generation failed.", "confidence": 0.0}
