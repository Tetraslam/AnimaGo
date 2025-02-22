"""
Core functionality for AnimaGo.
Contains base classes, interfaces, and core business logic.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class AnimalRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    UNDISCOVERED = "undiscovered"

@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime = datetime.now()

@dataclass
class Animal:
    id: str
    name: str
    species: str
    rarity: AnimalRarity
    confidence: float
    location: Location
    image_path: str
    discovered_at: datetime = datetime.now()
    discovered_by: Optional[str] = None
    metadata: dict = None

@dataclass
class User:
    id: str
    username: str
    email: str
    xp: int = 0
    level: int = 1
    discoveries: List[str] = None  # List of animal IDs
    achievements: List[str] = None
    guild_id: Optional[str] = None
    created_at: datetime = datetime.now()
    last_active: datetime = datetime.now() 