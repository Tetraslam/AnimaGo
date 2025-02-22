"""
Computer vision functionality for AnimaGo.
Handles animal detection, segmentation, and image processing.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import moondream as md
import numpy as np
from PIL import Image

from ..core import Animal, Location


class VisionSystem:
    def __init__(self):
        """Initialize API client only - models will be loaded on demand."""
        self.moondream = md.vl(api_key=os.getenv("MOONDREAM_API_KEY"))
        self._yolo = None
        self._sam = None
    
    def process_image(self, image_path: Path) -> List[Animal]:
        """Process an image and return detected animals."""
        # For testing, just do basic image load and Moondream query
        image = Image.open(image_path)
        encoded_image = self.moondream.encode_image(image)
        
        # Simple test query
        result = self.moondream.query(encoded_image, "What animals do you see in this image?")
        print(f"Moondream response: {result}")
        
        # Return empty list for now
        return []
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better detection."""
        # TODO: Implement image enhancement
        return image
    
    def segment_animal(self, image: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
        """Segment animal from background using SAM."""
        self.sam.set_image(image)
        masks = self.sam.predict(box=box)
        return masks[0]  # Return best mask 