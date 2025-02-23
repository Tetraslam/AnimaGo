"""
FastAPI server for AnimaGo backend.
Handles vision processing, geolocation, and user data.
"""

import json
import requests

from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ..config import TEMP_DIR
from ..core import Animal, Location, User
from ..geo import GeoSystem
from ..vision import VisionSystem

app = FastAPI(title="AnimaGo API")
vision_system = VisionSystem()
geo_system = GeoSystem()

# Configure CORS for mobile client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/vision/process")
async def process_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    altitude: float = Form(None),
    accuracy: float = Form(None),
    timestamp: str = Form(None)
):
    """Process uploaded image and detect animals."""
    # Save uploaded file
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create location object
    location = Location(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        accuracy=accuracy,
        timestamp=datetime.fromisoformat(timestamp) if timestamp else datetime.now()
    )
    
    # Process image
    try:
        animals = vision_system.process_image(temp_path)
        for animal in animals:
            animal.location = location
        return {"animals": [animal.__dict__ for animal in animals]}
    finally:
        # Cleanup
        temp_path.unlink(missing_ok=True)

@app.get("/geo/nearby")
async def get_nearby(lat: float, lon: float, radius: float = 1000) -> List[dict]:
    """Get nearby animal sightings."""
    location = Location(latitude=lat, longitude=lon)
    # TODO: Get animals from database
    animals = []  # Placeholder until database integration
    nearby = geo_system.get_nearby_animals(location, animals, radius)
    return [animal.__dict__ for animal in nearby]

@app.post("/users/sync")
async def sync_user(user_data: dict) -> dict:
    """Sync user data with server."""
    user = User(**user_data)
    # TODO: Sync with database
    return user.__dict__ 

@app.get("/geo/user_town_location")
async def user_town_location(latitude: float, longitude: float):
  base_url = "https://nominatim.openstreetmap.org/reverse"
  headers = {
    'User-Agent': 'My User Agent 1.0',
    }   
  
  params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json"
        }   
  response = requests.get(base_url, params=params, headers=headers)
  
  if response.status_code == 200:
    data = response.json()
    address = data.get("address", {})
    town = address.get("city")
    state = address.get("state")
    country = address.get("country")
    return {"latitude": latitude, "longitude": longitude, "town": town, "state": state, "country": country}
  else:   
    return {"error": f"Failed to retrieve location information: {response.text}"}