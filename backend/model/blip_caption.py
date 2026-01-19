import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

MODEL_NAME = "Salesforce/blip-image-captioning-base"  # original BLIP, lightweight

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_processor, _model = None, None

def get_caption_model():
    global _processor, _model
    if _processor is None or _model is None:
        _processor = BlipProcessor.from_pretrained(MODEL_NAME, use_fast=True)
        _model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
        _model.to(_device)
        _model.eval()
    return _processor, _model

def generate_caption(image_path, prompt=None, style_prompt=None, max_new_tokens=50):
    """
    prompt / style_prompt: optional strings to influence how the caption is framed. 
    If both provided, style_prompt takes precedence for prefixing.
    """
    processor, model = get_caption_model()
    image = Image.open(image_path).convert("RGB")

    inputs = processor(images=image, return_tensors="pt").to(_device)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
        caption = processor.decode(generated_ids[0], skip_special_tokens=True).strip()

    # Apply prefix if given (e.g., tactical summary or domain style)
    prefix = None
    if style_prompt:
        prefix = style_prompt.strip()
    elif prompt:
        prefix = prompt.strip()

    if prefix:
        caption = f"{prefix} {caption}"

    return {
        "label": caption,
        "confidence": None
    }
