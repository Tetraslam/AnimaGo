"""
API client for AnimaGo mobile app.
Handles communication with the backend server.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from ..config import APP_VERSION
from ..core import Animal, Location, User


class APIClient:
    def __init__(self, base_url: str = None):
        """Initialize API client."""
        self.base_url = base_url or "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.version = APP_VERSION
        
    async def upload_image(self, image_path: Path, location: Location) -> Dict:
        """Upload image for processing."""
        files = {"file": open(image_path, "rb")}
        data = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "altitude": location.altitude,
            "accuracy": location.accuracy,
            "timestamp": location.timestamp.isoformat()
        }
        
        async with self.client as client:
            response = await client.post(
                f"{self.base_url}/vision/process",
                files=files,
                data=data
            )
            return response.json()
            
    async def get_nearby_animals(self, location: Location, radius: float = 1000) -> List[Animal]:
        """Get animals near the specified location."""
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "radius": radius
        }
        
        async with self.client as client:
            response = await client.get(
                f"{self.base_url}/geo/nearby",
                params=params
            )
            return [Animal(**data) for data in response.json()]
            
    async def sync_user_data(self, user: User) -> User:
        """Sync user data with the server."""
        async with self.client as client:
            response = await client.post(
                f"{self.base_url}/users/sync",
                json=user.__dict__
            )
            return User(**response.json()) 