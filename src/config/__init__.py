"""
Configuration management for AnimaGo.
Handles environment variables, app settings, and constants.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
ROOT_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = ROOT_DIR / "src" / "assets"
STORAGE_DIR = ROOT_DIR / "storage"
DATA_DIR = STORAGE_DIR / "data"
TEMP_DIR = STORAGE_DIR / "temp"

# Ensure directories exist
for dir_path in [DATA_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# App settings
APP_NAME = "AnimaGo"
APP_VERSION = "0.1.0"

# Firebase config
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

# Vision settings
MOONDREAM_MODEL = "vikhyatk/moondream1"
YOLO_MODEL = "yolov8n.pt"
SAM_MODEL = "sam_vit_h_4b8939.pth"

# Map settings
DEFAULT_ZOOM = 13
MAP_STYLE = "OpenStreetMap" 