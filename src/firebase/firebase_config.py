import firebase_admin
from firebase_admin import credentials, firestore, storage # type: ignore
from google.cloud.firestore import SERVER_TIMESTAMP
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("src/firebase/anima-go-50202ba9d2b2.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'anima-go.appspot.com'
})

# Initialize the 'sighting_pics' bucket
sighting_pics_bucket = storage.bucket('sighting_pics')

db = firestore.client()
bucket = storage.bucket()

print("Firebase initialized successfully!")

# Pydantic models
class Coordinates(BaseModel):
    lat: float
    lng: float

class Comment(BaseModel):
    user_id: str
    comment: str

class Sighting(BaseModel):
    userID: str
    timestamp: datetime
    createdAt: datetime = Field(default_factory=lambda: datetime.now())
    updatedAt: datetime = Field(default_factory=lambda: datetime.now())
    coordinates: Coordinates
    species: str
    description: str
    sightingID: str
    comments: List[Comment] = []

class Achievement(BaseModel):
    achievementName: str
    dateAcquired: datetime

class User(BaseModel):
    userID: str
    firstname: str
    lastname: str
    colorblind: bool
    stickers: List[str] = []
    sightings: List[str] = []
    achievements: List[Achievement] = []
    xp: int

# Repository functions
def add_sighting(sighting_data: dict):
    sighting = Sighting(**sighting_data)
    db.collection('sightings_map').add(sighting.dict())
    print("Sighting added successfully!")

def add_user(user_data: dict):
    user = User(**user_data)
    db.collection('users').add(user.dict())
    print("User added successfully!")

# Initialize the 'sighting_pics' bucket
sighting_pics_bucket = storage.bucket('sighting_pics')

def upload_sighting_image(file_path: str, destination_blob_name: str):
    """
    Uploads a file to the sighting_pics bucket.
    
    :param file_path: Path to the file to upload.
    :param destination_blob_name: The name of the destination blob in the bucket.
    """
    blob = sighting_pics_bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to {destination_blob_name} in sighting_pics bucket.")

def add_comment(sighting_id: str, user_id: str, comment: str):
    sighting_ref = db.collection('sightings_map').document(sighting_id)
    
    # Check if the document exists
    if not sighting_ref.get().exists:
        # Create the document if it does not exist
        sighting_ref.set({
            'comments': []
        })
    
    # Update the document with the new comment
    sighting_ref.update({
        'comments': firestore.ArrayUnion([{
            'user_id': user_id,
            'comment': comment,
            'timestamp': SERVER_TIMESTAMP
        }])
    })
    print(f"Comment added to sighting {sighting_id} by user {user_id}.")