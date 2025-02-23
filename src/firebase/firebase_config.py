import firebase_admin
from firebase_admin import credentials, firestore, storage # type: ignore
from google.cloud.firestore import SERVER_TIMESTAMP
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import uuid4, UUID
import os

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
    userID: UUID
    comment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

class Sighting(BaseModel):
    userID: UUID
    timestamp: datetime
    createdAt: datetime = Field(default_factory=lambda: datetime.now())
    updatedAt: datetime = Field(default_factory=lambda: datetime.now())
    coordinates: Coordinates
    species: str
    description: str
    sightingID: UUID = Field(default_factory=uuid4)
    comments: List[Comment] = []
    sightingURL: Optional[str] = None

class Achievement(BaseModel):
    achievementName: str
    dateAcquired: datetime

class User(BaseModel):
    userID: UUID = Field(default_factory=uuid4)
    firstname: str
    lastname: str
    colorblind: bool
    stickers: List[str] = [] # List of sticker URLs
    sightings: List[UUID] = [] # List of sighting IDs
    achievements: List[Achievement] = []
    xp: int

# Repository functions
import json
def add_user(user_data: dict):
    user = User(**user_data)
    user_dict = json.loads(json.dumps(user.dict(), default=custom_encoder))
    db.collection('users').add(user_dict)
    print("User added successfully!")

def add_sighting(sighting_data: dict, user_id: str, sighting_pic_filename: str):

    """
    :param sighting_data: 
    {
        "timestamp": image capture timestamp,
        "coordinates": { lat: 0.0, lng: 0.0 },
        "species": "Species of the animal in image",
        "description": "Moondream description of the animal in image"
    }
    :param user_id: UUID4
    :param sighting_pic_filename: The name of the file to upload present in the 'temp' directory.
    """

    # UserId
    sighting_data['userID'] = user_id

    # Create sightingID = UUID
    sighting_id = uuid4()
    sighting_data['sightingID'] = sighting_id

    # Comments list initially empty
    sighting_data['comments'] = []

    # Upload the image to the sighting_pics bucket with filename as the sightingID = UUID
    destination_blob_name = f"{user_id}/{sighting_id}"
    upload_sighting_image(destination_blob_name, sighting_pic_filename, str(user_id))
    sighting_data['sightingURL'] = destination_blob_name

    sighting_data['createdAt'] = datetime.now()
    sighting_data['updatedAt'] = datetime.now()

    # Add the sighting to the 'sightings_map' collection with sightingID
    sighting = Sighting(**sighting_data)
    sighting_dict = json.loads(json.dumps(sighting.dict(), default=custom_encoder))
    db.collection('sightings_map').add(sighting_dict)
    user_id = sighting_dict['userID']
    
    # Update the user's 'sightings' list and increment the user's 'xp' by 100
    user_ref = db.collection('users').where('userID', '==', str(user_id)).limit(1)
    result = user_ref.get()

    if result:
        doc_ref = result[0].reference
        doc_ref.update({
            'sightings': firestore.ArrayUnion([str(sighting_id)]),
            'xp': firestore.Increment(100)

        })
        print("User updated successfully!")


def upload_sighting_image(destination_blob_name, from_file_name: str, user_id: str):
    """
    Uploads a file to the sighting_pics bucket, organized by userId.
    
    :param file_name: The name of the file to upload.
    :param user_id: The ID of the user.
    """
    file_path = os.path.join("src/temp", from_file_name)
    blob = sighting_pics_bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to {destination_blob_name} in sighting_pics bucket.")

def add_comment(sighting_id: str, comment_by_user_id: str, comment: str):
    sighting_ref = db.collection('sightings_map').where('sightingID', '==', str(sighting_id)).limit(1)
    result = sighting_ref.get()

    if result:
        doc_ref = result[0].reference

        # Update the document with the new comment
        doc_ref.update({
            'comments': firestore.ArrayUnion([{
                'userID': comment_by_user_id,
                'comment': comment,
                'timestamp': datetime.now()
            }])
        })
    
    print(f"Comment added to sighting {sighting_id} by user {comment_by_user_id}.")

def custom_encoder(obj):
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def get_top_users(n):
    users_ref = db.collection('users')
    query = users_ref.order_by('xp', direction=firestore.Query.DESCENDING).limit(n)
    results = query.stream()

    top_users = []
    for user in results:
        top_users.append(user.to_dict())

    return top_users