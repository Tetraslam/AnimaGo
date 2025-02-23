"""
FastAPI server for AnimaGo backend.
Handles vision processing, geolocation, and user data.
"""

import os
from pathlib import Path
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

# Load environment variables first
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

import base64
import io
import json
import logging
import time
from datetime import datetime
from typing import List, Optional

import moondream as md
import requests
from PIL import Image

from ..config import TEMP_DIR
from ..core import Animal, Location, User
from ..firebase.firebase_config import add_sighting, add_user, db
from ..geo import GeoSystem
from ..vision import VisionSystem

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment setup
logger.info("Starting server with environment:")
logger.info(f"MOONDREAM_API_KEY configured: {'MOONDREAM_API_KEY' in os.environ}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment file path: {env_path}")

app = FastAPI(title="AnimaGo API")
vision_system = VisionSystem()
geo_system = GeoSystem()

# Auth setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configure CORS for mobile client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    firstname: str
    lastname: str
    colorblind: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str
    colorblind: bool
    xp: int
    userID: UUID

# Auth dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # Get user from Firebase by email (token will be email in this simple version)
        user_ref = db.collection('users').where('email', '==', token).limit(1)
        result = user_ref.get()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return result[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user."""
    try:
        # Check if email already exists
        existing_user = db.collection('users').where('email', '==', user.email).limit(1).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user data with default values
        user_data = {
            "email": user.email,
            "password": user.password,  # In production, this should be hashed!
            "firstname": user.firstname,
            "lastname": user.lastname,
            "colorblind": user.colorblind,
            "userID": str(uuid4()),
            "xp": 0,
            "stickers": [],
            "sightings": [],
            "achievements": []
        }
        
        # Add user to Firebase
        add_user(user_data)
        
        # Return user data (excluding password)
        return UserResponse(**user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=UserResponse)
async def login(user: UserLogin):
    """Login with email and password."""
    try:
        # Get user from Firebase
        user_ref = db.collection('users').where('email', '==', user.email).limit(1)
        result = user_ref.get()
        
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        user_data = result[0].to_dict()
        
        # Check password (in production, this should be hashed!)
        if user_data["password"] != user.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Return user data (excluding password)
        return UserResponse(
            email=user_data["email"],
            firstname=user_data["firstname"],
            lastname=user_data["lastname"],
            colorblind=user_data["colorblind"],
            xp=user_data["xp"],
            userID=UUID(user_data["userID"])
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/vision/process")
async def process_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    altitude: float = Form(None),
    accuracy: float = Form(None),
    timestamp: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Process uploaded image and detect animals."""
    try:
        # Read image into memory
        content = await file.read()
        image_buffer = io.BytesIO(content)
        
        # Initialize model
        api_key = os.getenv("MOONDREAM_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="MOONDREAM_API_KEY not configured")
            
        model = md.vl(api_key=api_key)
        
        # Process image with retries
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                with Image.open(image_buffer) as image:
                    # Reset buffer position for each attempt
                    image_buffer.seek(0)
                    
                    # Encode image
                    encoded_image = model.encode_image(image)
                    
                    # Get species
                    species_result = model.query(encoded_image, "What species is in this image? Respond in the format 'Species: YOUR ANSWER HERE'")
                    species = species_result["answer"].split(": ")[1] if ": " in species_result["answer"] else species_result["answer"]
                    
                    # Get description
                    description_result = model.query(encoded_image, "Describe the animal in this image in detail.")
                    description = description_result["answer"]
                    
                    # Create sighting data
                    sighting_data = {
                        "userID": UUID(current_user["userID"]),
                        "timestamp": datetime.now(),
                        "coordinates": {
                            "lat": latitude,
                            "lng": longitude
                        },
                        "species": species,
                        "description": description,
                    }
                    
                    # Save sighting
                    add_sighting(sighting_data, str(current_user["userID"]), content)
                    
                    return {
                        "species": species,
                        "description": description,
                        "sighting": sighting_data
                    }
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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

@app.post("/moondream/describe")
async def moondream_describe(file: UploadFile = File(...)):
    try:
        # Read image into memory
        content = await file.read()
        image_buffer = io.BytesIO(content)
        
        # Initialize model
        api_key = os.getenv("MOONDREAM_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="MOONDREAM_API_KEY not configured")
            
        model = md.vl(api_key=api_key)
        
        # Process image with retries
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                with Image.open(image_buffer) as image:
                    # Reset buffer position for each attempt
                    image_buffer.seek(0)
                    
                    # Process image
                    encoded_image = model.encode_image(image)
                    description = model.query(encoded_image, "What species is in this image? Respond in the format 'Species: YOUR ANSWER HERE'")["answer"]
                    
                    return {"description": description}
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")