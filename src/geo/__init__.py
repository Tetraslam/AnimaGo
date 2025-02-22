"""
Geospatial functionality for AnimaGo.
Handles location services, mapping, and spatial analysis.
"""

from typing import Dict, List, Tuple

from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from ..core import Animal, Location


class GeoSystem:
    def __init__(self):
        """Initialize geospatial services."""
        self.geolocator = Nominatim(user_agent="anima_go")
        
    def get_location_info(self, location: Location) -> Dict:
        """Get detailed information about a location."""
        try:
            location_str = f"{location.latitude}, {location.longitude}"
            address = self.geolocator.reverse(location_str)
            return {
                "address": address.address,
                "raw": address.raw
            }
        except Exception as e:
            return {"error": str(e)}
            
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations in meters."""
        return geodesic(
            (loc1.latitude, loc1.longitude),
            (loc2.latitude, loc2.longitude)
        ).meters
        
    def get_nearby_animals(self, location: Location, animals: List[Animal], radius: float = 1000) -> List[Animal]:
        """Get animals within specified radius (meters) of location."""
        nearby = []
        for animal in animals:
            distance = self.calculate_distance(location, animal.location)
            if distance <= radius:
                nearby.append(animal)
        return nearby
        
    def get_biome(self, location: Location) -> str:
        """Determine the biome type at given location."""
        # TODO: Implement biome detection using external API or dataset
        return "unknown"
        
    def generate_heatmap_data(self, animals: List[Animal]) -> List[Tuple[float, float, float]]:
        """Generate heatmap data from animal sightings."""
        return [(a.location.latitude, a.location.longitude, 1.0) for a in animals] 