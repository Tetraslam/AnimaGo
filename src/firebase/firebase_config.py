import json
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

import firebase_admin
from firebase_admin import credentials, firestore, storage  # type: ignore
from google.cloud.firestore import SERVER_TIMESTAMP
from pydantic import BaseModel, Field, validator

# Initialize Firebase
cred = credentials.Certificate("src/firebase/anima-go-50202ba9d2b2.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'anima-go.firebasestorage.app'
})

# Initialize Firestore and Storage
db = firestore.client()
bucket = storage.bucket(app=firebase_admin.get_app())

# Verify bucket exists and create if needed
if not bucket.exists():
    bucket.create()
    print(f"Created new bucket: {bucket.name}")
else:
    print(f"Using existing bucket: {bucket.name}")

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
    email: str
    password: str
    firstname: str
    lastname: str
    colorblind: bool = False
    stickers: List[str] = [] # List of sticker URLs
    sightings: List[UUID] = [] # List of sighting IDs
    achievements: List[Achievement] = []
    xp: int = 0

# Repository functions
def add_user(user_data: dict):
    try:
        # Convert string UUID to UUID object if needed
        if isinstance(user_data.get('userID'), str):
            user_data['userID'] = UUID(user_data['userID'])
        
        # Convert string UUIDs in sightings list if needed
        if 'sightings' in user_data:
            user_data['sightings'] = [UUID(s) if isinstance(s, str) else s for s in user_data['sightings']]
        
        # Create User object to validate data
        user = User(**user_data)
        
        # Convert back to dict for Firestore
        user_dict = json.loads(json.dumps(user.dict(), default=custom_encoder))
        
        # Add to Firestore
        db.collection('users').document(str(user.userID)).set(user_dict)
        print("User added successfully!")
        return user_dict
    except Exception as e:
        print(f"Error adding user: {str(e)}")
        raise e

def add_sighting(sighting_data: dict, user_id: str, image_bytes: bytes):
    """
    Add a sighting to Firebase.
    
    :param sighting_data: Dictionary containing sighting details
    :param user_id: UUID of the user
    :param image_bytes: Raw bytes of the image
    """
    try:
        # Create sightingID
        sighting_id = uuid4()
        sighting_data['sightingID'] = sighting_id
        sighting_data['userID'] = user_id  # Ensure userID is a string to match schema

        # Comments list initially empty
        sighting_data['comments'] = []

        # Upload the image to storage
        destination_blob_name = f"sighting_pics/{user_id}/{sighting_id}.jpg"
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(image_bytes, content_type='image/jpeg')
        print(f"Image uploaded to {destination_blob_name}")
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Set the sightingURL to the public URL
        sighting_data['sightingURL'] = blob.public_url

        # Add timestamps
        now = datetime.now()
        sighting_data['createdAt'] = now
        sighting_data['updatedAt'] = now

        # Add the sighting to the 'sightings_map' collection
        sighting = Sighting(**sighting_data)
        sighting_dict = json.loads(json.dumps(sighting.dict(), default=custom_encoder))
        
        # Add to sightings_map collection with auto-generated document ID
        doc_ref = db.collection('sightings_map').document()
        doc_ref.set(sighting_dict)
        sighting_doc_id = doc_ref.id
        print(f"Sighting added with ID: {sighting_doc_id}")
        
        # Update user's sightings list with the sightings_map document ID
        user_ref = db.collection('users').where('userID', '==', user_id).limit(1)
        result = user_ref.get()

        if result:
            doc_ref = result[0].reference
            doc_ref.update({
                'sightings': firestore.ArrayUnion([sighting_doc_id]),  # Store the sightings_map document ID
                'xp': firestore.Increment(100)
            })
            print(f"User {user_id} updated with sighting {sighting_doc_id}")
            
    except Exception as e:
        print(f"Error adding sighting: {str(e)}")
        raise e

def upload_sighting_image(destination_blob_name, from_file_name: str, user_id: str):
    """
    Uploads a file to the sighting_pics bucket, organized by userId.
    
    :param file_name: The name of the file to upload.
    :param user_id: The ID of the user.
    """
    file_path = os.path.join("src/temp", from_file_name)
    blob = bucket.blob(destination_blob_name)
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

def get_user_sightings(user_id: str) -> List[dict]:
    """
    Fetch all sightings for a given user.
    
    :param user_id: UUID of the user
    :return: List of sighting dictionaries with full details
    """
    try:
        # Get user document
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"User {user_id} not found")
            return []
            
        # Get sighting IDs from user document
        user_data = user_doc.to_dict()
        sighting_ids = user_data.get('sightings', [])
        print(f"Found {len(sighting_ids)} sighting IDs for user {user_id}")
        
        # Fetch full sighting details
        sightings = []
        for sighting_id in sighting_ids:
            sighting_doc = db.collection('sightings_map').document(sighting_id).get()
            if sighting_doc.exists:
                sighting_data = sighting_doc.to_dict()
                sightings.append(sighting_data)
                print(f"Found sighting {sighting_id}")
            else:
                print(f"Sighting {sighting_id} not found")
        
        print(f"Returning {len(sightings)} sightings")
        return sightings
        
    except Exception as e:
        print(f"Error fetching user sightings: {str(e)}")
        return []