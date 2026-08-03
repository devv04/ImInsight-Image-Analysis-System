import torch
import open_clip
from PIL import Image

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_MODEL_NAME = "ViT-B-32"
_PRETRAINED = "openai"

_model = None
_preprocess = None
_tokenizer = None

def get_clip_model():
    global _model, _preprocess, _tokenizer
    if _model is None:
        _model, _, _preprocess = open_clip.create_model_and_transforms(_MODEL_NAME, pretrained=_PRETRAINED)
        _tokenizer = open_clip.get_tokenizer(_MODEL_NAME)
        _model.to(_device)
        _model.eval()
    return _model, _preprocess, _tokenizer


def classify_image(image_path, label_list, top_k=1):
    """
    Zero-shot classification. Returns best label/confidence from label_list.
    """
    try:
        model, preprocess, tokenizer = get_clip_model()
        image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(_device)  # [1,C,H,W]
        text_tokens = tokenizer(label_list).to(_device)  # [len(labels), ...]
        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text_tokens)


            # Normalize for cosine similarity
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            logits_per_image = (image_features @ text_features.T)  # [1, num_labels]
            probs = logits_per_image.softmax(dim=-1)[0]  # [num_labels]

        top_probs, top_idxs = probs.topk(top_k)
        best_idx = top_idxs[0].item()
        best_label = label_list[best_idx]
        confidence = float(top_probs[0].item())
        return {"label": best_label, "confidence": confidence}
    except Exception as e:
        # graceful fallback
        return {"label": "Unknown", "confidence": 0.0}
