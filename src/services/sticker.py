from segment_anything import sam_model_registry, SamPredictor
import numpy as np
from PIL import Image
import torch
import cv2
import os

def extract_animal(image_path: str, output_path: str = None) -> str:
    """
    Extract an animal from an image and create a PNG with transparent background.
    
    Args:
        image_path: Path to the input image
        output_path: Optional path for the output PNG. If not provided, will use input filename with _extracted.png
        
    Returns:
        Path to the saved PNG file
    """
    # Load the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Initialize SAM
    sam_checkpoint = "sam_vit_h_4b8939.pth"  # You'll need to download this
    model_type = "vit_h"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    
    # Set image in predictor
    predictor.set_image(image)
    
    # Get image center point for prompting
    h, w = image.shape[:2]
    center_x, center_y = w // 2, h // 2
    input_point = np.array([[center_x, center_y]])
    input_label = np.array([1])  # 1 indicates foreground
    
    # Generate mask
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True
    )
    
    # Use the mask with highest score
    mask = masks[np.argmax(scores)]
    
    # Convert to RGBA
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[..., :3] = image
    result[..., 3] = mask * 255  # Use mask as alpha channel
    
    # Convert to PIL Image
    result_image = Image.fromarray(result)
    
    # Save the result
    if output_path is None:
        base_path = os.path.splitext(image_path)[0]
        output_path = f"{base_path}_extracted.png"
    
    result_image.save(output_path, "PNG")
    return output_path