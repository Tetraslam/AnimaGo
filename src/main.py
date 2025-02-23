import base64
import io
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import flet as ft
import numpy as np
import requests
from flet import (Colors, Column, Container, ElevatedButton, Icon, IconButton,
                  Icons, Image, Page, Row, Tab, Tabs, Text, TextButton, View,
                  padding)
from flet_webview import WebView
from PIL import Image as PILImage
from PIL import ImageDraw

from components.achievements import AchievementsSection
from components.leaderboard import LeaderboardSection
from config import TEMP_DIR
from firebase.firebase_config import get_user_sightings


@dataclass
class AchievementData:
    title: str
    description: str
    icon: str
    progress: float  # 0.0 to 1.0
    color: str

def create_camera_view(on_capture, page: ft.Page):
    camera = None
    is_running = False
    image = ft.Image(
        width=336,
        height=252,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10,
    )
    
    def start_camera():
        nonlocal camera, is_running
        if camera is None:
            camera = cv2.VideoCapture(1)
            if not camera.isOpened():
                print("Error: Could not open camera")
                return
        
        is_running = True
        threading.Thread(target=update_frame, daemon=True).start()
    
    def stop_camera():
        nonlocal camera, is_running
        is_running = False
        if camera:
            camera.release()
            camera = None
    
    def update_frame():
        while is_running:
            ret, frame = camera.read()
            if ret:
                # Convert frame to format Flet can display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = PILImage.fromarray(rgb_frame)
                
                # Save to bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Convert to base64
                img_base64 = base64.b64encode(img_byte_arr).decode()
                
                # Update image src
                image.src_base64 = img_base64
                page.update()
            
            time.sleep(1/120)  # Limit to ~30 FPS
    
    def capture_photo(e):
        if camera and camera.isOpened():
            ret, frame = camera.read()
            if ret:
                on_capture(frame)
    
    camera_container = Container(
        content=Column([
            image,
            ElevatedButton(
                "Capture",
                icon=Icons.CAMERA,
                on_click=capture_photo,
            ),
        ]),
        padding=10,
    )
    
    # Start camera when view is created
    start_camera()
    
    # Return container and control functions
    return camera_container, start_camera, stop_camera

def main(page: ft.Page):
    # App configuration
    page.title = "AnimaGo"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_bgcolor = Colors.TRANSPARENT
    page.spacing = 0
    page.padding = padding.only(top=40)
    
    # Define reusable colors
    CARD_COLOR = Colors.BLUE_GREY_800
    
    # Auth state
    current_user = None
    
    def handle_login(user_data):
        nonlocal current_user
        current_user = user_data
        show_main_view()
    
    def handle_register(e):
        try:
            # Get form data
            email = register_email.value
            password = register_password.value
            firstname = register_firstname.value
            lastname = register_lastname.value
            colorblind = register_colorblind.value
            
            # Validate form
            if not all([email, password, firstname, lastname]):
                page.snack_bar = ft.SnackBar(content=Text("Please fill in all fields"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Register user
            response = requests.post(
                "http://localhost:8000/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "firstname": firstname,
                    "lastname": lastname,
                    "colorblind": colorblind
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                page.snack_bar = ft.SnackBar(
                    content=Text("Registration successful! Please log in.")
                )
                page.snack_bar.open = True
                page.update()
                # Show login view
                show_login_view()
            else:
                error_msg = response.json().get('detail', "Registration failed. Please try again.")
                page.snack_bar = ft.SnackBar(content=Text(error_msg))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=Text(f"Error: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    def handle_login_submit(e):
        try:
            # Get form data
            email = login_email.value
            password = login_password.value
            
            if not email or not password:
                page.snack_bar = ft.SnackBar(content=Text("Please enter your email and password"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Login user
            response = requests.post(
                "http://localhost:8000/auth/login",
                json={
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                handle_login(user_data)
            else:
                error_msg = response.json().get('detail', "Login failed. Please check your credentials.")
                page.snack_bar = ft.SnackBar(content=Text(error_msg))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=Text(f"Error: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    # Login view
    login_email = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
    )
    
    login_password = ft.TextField(
        label="Password",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        password=True,
    )
    
    login_view = Column(
        controls=[
            Text("Welcome to AnimaGo", size=32, weight=ft.FontWeight.BOLD),
            Container(height=20),
            login_email,
            Container(height=10),
            login_password,
            Container(height=20),
            ElevatedButton(
                "Login",
                width=300,
                on_click=handle_login_submit
            ),
            Container(height=20),
            Text("Don't have an account?", size=16),
            TextButton(
                "Register",
                on_click=lambda _: show_register_view()
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # Register view
    register_email = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
    )
    
    register_password = ft.TextField(
        label="Password",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        password=True,
    )
    
    register_firstname = ft.TextField(
        label="First Name",
        border=ft.InputBorder.UNDERLINE,
        width=300,
    )
    
    register_lastname = ft.TextField(
        label="Last Name",
        border=ft.InputBorder.UNDERLINE,
        width=300,
    )
    
    register_colorblind = ft.Switch(
        label="Colorblind Mode",
        value=False,
    )
    
    register_view = Column(
        controls=[
            Text("Create Account", size=32, weight=ft.FontWeight.BOLD),
            Container(height=20),
            register_email,
            Container(height=10),
            register_password,
            Container(height=10),
            register_firstname,
            Container(height=10),
            register_lastname,
            Container(height=10),
            register_colorblind,
            Container(height=20),
            ElevatedButton(
                "Register",
                width=300,
                on_click=handle_register
            ),
            Container(height=20),
            Text("Already have an account?", size=16),
            TextButton(
                "Login",
                on_click=lambda _: show_login_view()
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    def show_login_view():
        content_area.content = login_view
        page.update()
    
    def show_register_view():
        content_area.content = register_view
        page.update()
    
    def show_main_view():
        content_area.content = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="Capture",
                    icon=Icons.CAMERA_ALT_OUTLINED,
                    content=Container(
                        content=capture_view,
                        padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Map", 
                    icon=Icons.MAP_OUTLINED,
                    content=Container(
                      content=map_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Biodex",
                    icon=Icons.MENU_BOOK_OUTLINED, 
                    content=Container(
                      content=biodex_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Leaderboard",
                    icon=Icons.LEADERBOARD_OUTLINED,
                    content=leaderboard_view,
                ),
                Tab(
                    text="Achievements",
                    icon=Icons.EMOJI_EVENTS_OUTLINED,
                    content=Container(
                      content=AchievementsSection(page),
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Profile",
                    icon=Icons.PERSON_OUTLINED,
                    content=Container(
                      content=profile_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
            ],
        )
        page.update()
    
    def handle_capture(frame):
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image and save as JPEG
        pil_image = PILImage.fromarray(rgb_frame)
        
        # Save to bytes for display
        display_buffer = io.BytesIO()
        pil_image.save(display_buffer, format='PNG')
        img_base64 = base64.b64encode(display_buffer.getvalue()).decode()
        
        # Save to temporary JPEG for API
        temp_buffer = io.BytesIO()
        pil_image.save(temp_buffer, format='JPEG')
        
        # Add auth header
        headers = {"Authorization": f"Bearer {current_user['email']}"}  # Use email as token
        
        # Immediately call process_image
        process_image(None, temp_buffer.getvalue(), img_base64, headers)
    
    def process_image(e, image_bytes=None, display_base64=None, headers=None):
        try:
            # Show loading state
            content_area.content = Column(
                controls=[
                    Text("Processing image...", size=20),
                    ft.ProgressRing(),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            page.update()
            
            try:
                # Make request to Moondream endpoint
                files = {
                    "file": ("image.jpg", io.BytesIO(image_bytes), "image/jpeg")
                }
                response = requests.post(
                    "http://localhost:8000/moondream/describe",
                    files=files,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get('detail', 'Unknown error')
                    raise Exception(f"API request failed: {error_detail}")
                    
                result = response.json()
                description = result.get('description', 'No description available')
                # Extract species from the description (format: "Species: X")
                species = description.split(": ")[1] if ": " in description else "Unknown species"

                # Save sighting to Firebase
                def handle_save_sighting(e):
                    try:
                        # Create a temporary file-like object in memory
                        temp_buffer = io.BytesIO(image_bytes)
                        temp_buffer.name = "image.jpg"  # Set a name for the file

                        def on_location(e):
                            try:
                                # Get coordinates from location event
                                lat = e.data['latitude']
                                lng = e.data['longitude']
                                accuracy = e.data.get('accuracy', 0)
                                
                                # Upload to server
                                files = {"file": ("image.jpg", temp_buffer, "image/jpeg")}
                                data = {
                                    "latitude": lat,
                                    "longitude": lng,
                                    "accuracy": accuracy,
                                    "timestamp": datetime.now().isoformat()
                                }
                                
                                response = requests.post(
                                    "http://localhost:8000/vision/process",
                                    files=files,
                                    data=data,
                                    headers=headers
                                )

                                if response.status_code == 200:
                                    page.snack_bar = ft.SnackBar(content=Text("Sighting saved!"))
                                    page.snack_bar.open = True
                                    page.update()
                                    show_main_view()  # Return to main view
                                else:
                                    raise Exception(f"Failed to save sighting: {response.text}")

                            except Exception as e:
                                page.snack_bar = ft.SnackBar(content=Text(f"Error saving sighting: {str(e)}"))
                                page.snack_bar.open = True
                                page.update()
                            finally:
                                # Clean up
                                temp_buffer.close()

                        def on_location_error(e):
                            page.snack_bar = ft.SnackBar(content=Text("Could not get location. Using default coordinates."))
                            page.snack_bar.open = True
                            page.update()
                            
                            # Fall back to default coordinates
                            on_location(ft.LocationData({"latitude": 0.0, "longitude": 0.0, "accuracy": 0}))

                        # Request location
                        page.client_storage.clear()
                        page.get_location(on_location, on_location_error)
                        
                    except Exception as e:
                        page.snack_bar = ft.SnackBar(content=Text(f"Error preparing sighting: {str(e)}"))
                        page.snack_bar.open = True
                        page.update()
                
                # Display results with Save button
                content_area.content = Column(
                    controls=[
                        Row(
                            controls=[
                                IconButton(
                                    icon=Icons.ARROW_BACK,
                                    icon_color=Colors.WHITE,
                                    on_click=lambda _: show_capture_view(),
                                ),
                                Text("Analysis:", size=24, weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        Image(
                            src_base64=display_base64,
                            width=300,
                            height=300,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        Container(height=10),
                        Text(f"Species: {species}", size=20, weight=ft.FontWeight.BOLD),
                        Container(height=5),
                        Text(description, size=16),
                        Container(height=20),
                        Row(
                            controls=[
                                ElevatedButton(
                                    "Save Sighting",
                                    icon=Icons.SAVE,
                                    on_click=handle_save_sighting,
                                ),
                                ElevatedButton(
                                    "Capture Another",
                                    icon=Icons.CAMERA_ALT,
                                    on_click=lambda _: show_capture_view(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            except Exception as e:
                # Handle any errors during processing
                content_area.content = Column(
                    controls=[
                        Row(
                            controls=[
                                IconButton(
                                    icon=Icons.ARROW_BACK,
                                    icon_color=Colors.WHITE,
                                    on_click=lambda _: show_capture_view(),
                                ),
                                Text("Error processing image", size=24, color=Colors.RED),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        Text(str(e), size=16),
                        Container(height=20),
                        ElevatedButton(
                            "Try Again",
                            icon=Icons.CAMERA_ALT,
                            on_click=lambda _: show_capture_view(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
        except Exception as e:
            # Handle any errors during processing
            content_area.content = Column(
                controls=[
                    Row(
                        controls=[
                            IconButton(
                                icon=Icons.ARROW_BACK,
                                icon_color=Colors.WHITE,
                                on_click=lambda _: show_capture_view(),
                            ),
                            Text("Error processing image", size=24, color=Colors.RED),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    Text(str(e), size=16),
                    Container(height=20),
                    ElevatedButton(
                        "Try Again",
                        icon=Icons.CAMERA_ALT,
                        on_click=lambda _: show_capture_view(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        finally:
            page.update()
    
    # Add the show_capture_view function
    def show_capture_view():
        show_main_view()  # Return to main tabbed view
        page.update()
    
    # Create camera view
    camera_view, start_camera, stop_camera = create_camera_view(handle_capture, page)
    
    # View: Capture
    capture_view = Column(
        controls=[
            Text("\n  Ready to discover\n  wildlife?", size=32, weight=ft.FontWeight.BOLD),
            Text("Point your camera at an animal to begin", size=16),
            Container(height=8),
            camera_view,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # View: Map
    def create_map_view():
        def create_map_image(width=400, height=600):
            try:
                # Get absolute path to the image
                current_dir = os.getcwd()
                image_path = os.path.join(current_dir, "image.png")  # Removed @ symbol
                print(f"Attempting to load map from: {image_path}")
                
                # Check if file exists
                if not os.path.exists(image_path):
                    print(f"Error: Map image not found at {image_path}")
                    raise FileNotFoundError(f"Map image not found at {image_path}")
                
                # Load the world map image
                world_map = PILImage.open(image_path)
                
                # Calculate aspect ratio to maintain proportions
                aspect_ratio = world_map.width / world_map.height
                new_height = int(width / aspect_ratio)
                
                # Resize image maintaining aspect ratio
                world_map = world_map.resize((width, new_height), PILImage.Resampling.LANCZOS)
                
                # Create a dark background image
                background = PILImage.new('RGB', (width, height), (30, 41, 59))
                
                # Calculate position to center the map vertically
                y_offset = (height - new_height) // 2
                
                # Paste the world map onto the background
                background.paste(world_map, (0, y_offset))
                
                # Create drawing object
                draw = ImageDraw.Draw(background)
                
                # Convert Boston's coordinates to pixels
                # Boston: 42.3601° N, 71.0589° W
                boston_x = int(width * (180 - 71.0589) / 360)  # Convert longitude to x
                boston_y = int(y_offset + (new_height * (90 - 42.3601) / 180))  # Convert latitude to y
                
                # Draw Boston marker
                marker_size = 5
                draw.ellipse((boston_x - marker_size, boston_y - marker_size,
                            boston_x + marker_size, boston_y + marker_size),
                            fill=(255, 69, 0))  # Bright orange marker
                
                # Label Boston
                draw.text((boston_x + 10, boston_y), "Boston", fill=(255, 255, 255))
                
                # Convert to base64 for display
                img_byte_arr = io.BytesIO()
                background.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                img_base64 = base64.b64encode(img_byte_arr).decode()
                
                return img_base64
                
            except Exception as e:
                print(f"Error creating map image: {str(e)}")
                # Create a fallback solid color image
                img = PILImage.new('RGB', (width, height), (30, 41, 59))
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode()

        def refresh_map():
            try:
                # Get user's sightings
                if current_user:
                    sightings = get_user_sightings(str(current_user['userID']))
                    print(f"Found {len(sightings)} sightings")
                else:
                    sightings = []

                # Create base64 map image
                map_base64 = create_map_image()
                
                # Display map image
                map_container.content = Column(
                    controls=[
                        Container(
                            content=Image(
                                src_base64=map_base64,
                                width=400,
                                height=600,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=10,
                            ),
                            bgcolor=Colors.BLUE_GREY_900,
                            border_radius=10,
                            padding=10,
                        ),
                        Container(height=10),
                        Text(f"Found {len(sightings)} sightings", size=14, color=Colors.GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                page.update()
                
            except Exception as e:
                print(f"Error loading map: {str(e)}")
                map_container.content = Column(
                    controls=[
                        Text("Error loading map", size=16, color=Colors.RED),
                        Text(str(e), size=14, color=Colors.RED),
                        ElevatedButton(
                            "Retry",
                            on_click=lambda _: refresh_map()
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                page.update()

        # Create refresh button
        refresh_button = IconButton(
            icon=Icons.REFRESH,
            icon_color=Colors.BLUE_400,
            on_click=lambda _: refresh_map(),
            tooltip="Refresh map",
        )

        # Create map container
        map_container = Container(
            content=Text("Loading map...", size=16),
            bgcolor=Colors.BLUE_GREY_900,
            border_radius=10,
            padding=10,
            alignment=ft.alignment.center,
        )

        map_view = Column(
            controls=[
                Row(
                    controls=[
                        Text("Wildlife Map", size=32, weight=ft.FontWeight.BOLD),
                        refresh_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                Text("View your wildlife sightings", size=16),
                Container(height=20),
                map_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Initial load of map
        refresh_map()
        return map_view

    # Update the map tab to use the new view
    map_view = create_map_view()
    
    # View: Biodex
    def create_biodex_view():
        def create_sighting_card(sighting: dict) -> Container:
            # Add debug logging
            print(f"Creating card for sighting: {sighting.get('sightingID')}")
            print(f"Image URL: {sighting.get('sightingURL')}")
            print(f"Species: {sighting.get('species')}")
            
            def handle_create_sticker(e):
                try:
                    # Show loading state
                    page.snack_bar = ft.SnackBar(content=Text("Creating sticker..."))
                    page.snack_bar.open = True
                    page.update()
                    
                    # Download the image from sightingURL
                    image_url = sighting.get('sightingURL')
                    if not image_url:
                        raise Exception("No image URL found")
                        
                    # Get the image data
                    response = requests.get(image_url)
                    if response.status_code != 200:
                        raise Exception("Failed to download image")
                    
                    # Save to a temporary file
                    temp_dir = os.path.join(os.getcwd(), "temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_input = os.path.join(temp_dir, f"temp_input_{sighting.get('sightingID')}.jpg")
                    
                    with open(temp_input, "wb") as f:
                        f.write(response.content)
                    
                    # Extract the animal using the sticker function
                    from services.sticker import extract_animal
                    output_path = os.path.join(temp_dir, f"sticker_{sighting.get('sightingID')}.png")
                    extracted_path = extract_animal(temp_input, output_path)
                    
                    # Read the extracted image for download
                    with open(extracted_path, "rb") as f:
                        sticker_data = f.read()
                    
                    # Clean up temporary files
                    os.remove(temp_input)
                    os.remove(extracted_path)
                    
                    # Trigger download using Flet's download functionality
                    species_name = sighting.get('species', 'animal').replace(' ', '_').lower()
                    page.client_storage.set(f"sticker_{species_name}.png", base64.b64encode(sticker_data).decode())
                    page.launch_url(f"data:image/png;base64,{base64.b64encode(sticker_data).decode()}")
                    
                    # Show success message
                    page.snack_bar = ft.SnackBar(content=Text("Sticker created! Check your downloads."))
                    page.snack_bar.open = True
                    page.update()
                    
                except Exception as e:
                    print(f"Error creating sticker: {str(e)}")
                    page.snack_bar = ft.SnackBar(content=Text(f"Error creating sticker: {str(e)}"))
                    page.snack_bar.open = True
                    page.update()

            # Create the card with explicit size and margin
            return Container(
                content=Column(
                    controls=[
                        Container(
                            content=Image(
                                src=sighting.get('sightingURL'),
                                width=120,
                                height=120,
                                fit=ft.ImageFit.COVER,
                                border_radius=10,
                            ),
                            width=120,
                            height=120,
                            border_radius=10,
                            bgcolor=Colors.BLUE_GREY_900,
                        ),
                        Text(sighting.get('species', 'Unknown'), size=16),
                        Text(
                            sighting.get('description', '')[:50] + '...' if len(sighting.get('description', '')) > 50 else sighting.get('description', ''),
                            size=12,
                            color=Colors.GREY_400
                        ),
                        Container(height=5),
                        ElevatedButton(
                            text="Create Sticker",
                            icon=Icons.EMOJI_EMOTIONS,
                            on_click=handle_create_sticker,
                            color=Colors.WHITE,
                            bgcolor=Colors.BLUE_400,
                        ),
                    ],
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
                margin=5,
                bgcolor=CARD_COLOR,
                border_radius=10,
                width=150,  # Fixed width for consistent card size
            )

        def refresh_sightings():
            if not current_user:
                return
            
            # Fetch user's sightings using the user's ID
            sightings = get_user_sightings(str(current_user['userID']))
            print(f"Fetched {len(sightings)} sightings for user {current_user['userID']}")
            
            # Create grid of sighting cards
            sighting_cards = [create_sighting_card(sighting) for sighting in sightings]
            
            # Update the grid
            sightings_grid.controls = sighting_cards if sighting_cards else [
                Container(
                    content=Text("No sightings yet. Go capture some wildlife!", 
                               size=16, 
                               color=Colors.GREY_400,
                               text_align=ft.TextAlign.CENTER),
                    padding=20,
                )
            ]
            page.update()

        # Create grid for sightings
        sightings_grid = Row(
            controls=[],
            wrap=True,
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Create refresh button
        refresh_button = IconButton(
            icon=Icons.REFRESH,
            icon_color=Colors.BLUE_400,
            on_click=lambda _: refresh_sightings(),
            tooltip="Refresh sightings",
        )

        biodex_view = Column(
            controls=[
                Row(
                    controls=[
                        Text("Your Biodex", size=32, weight=ft.FontWeight.BOLD),
                        refresh_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                Text("Animals you've discovered", size=16),
                Container(height=20),
                sightings_grid,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        # Initial load of sightings
        refresh_sightings()
        return biodex_view

    # Update the biodex tab to use the new view
    biodex_view = create_biodex_view()
    
    # View: Profile
    profile_view = Column(
        controls=[
            # User info section
            Container(
                content=Column(
                    controls=[
                        Row(
                            controls=[
                                Container(
                                    content=Icon(
                                        name=Icons.ACCOUNT_CIRCLE,
                                        size=60,
                                        color=Colors.BLUE_400,
                                    ),
                                    margin=padding.only(right=20),
                                ),
                                Column(
                                    controls=[
                                        Text(
                                            "Wildlife Explorer",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        Text(
                                            "Level 5",
                                            size=16,
                                            color=Colors.BLUE_400,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        Container(height=20),
                        Row(
                            controls=[
                                Container(
                                    content=Column(
                                        controls=[
                                            Text(
                                                "42",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            Text("Sightings"),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                                Container(
                                    content=Column(
                                        controls=[
                                            Text(
                                                "12",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            Text("Species"),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                                Container(
                                    content=Column(
                                        controls=[
                                            Text(
                                                "3",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            Text("Badges"),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),
            # Add achievements section
            AchievementsSection(page),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # View: Leaderboard
    leaderboard_view = Container(
        content=LeaderboardSection(page=page),
        padding=20,
    )
    
    # Content area with tabs
    content_area = Container(
        content=Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="Capture",
                    icon=Icons.CAMERA_ALT_OUTLINED,
                    content=Container(
                      content=capture_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Map", 
                    icon=Icons.MAP_OUTLINED,
                    content=Container(
                      content=map_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Biodex",
                    icon=Icons.MENU_BOOK_OUTLINED, 
                    content=Container(
                      content=biodex_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Leaderboard",
                    icon=Icons.LEADERBOARD_OUTLINED,
                    content=leaderboard_view,
                ),
                Tab(
                    text="Achievements",
                    icon=Icons.EMOJI_EVENTS_OUTLINED,
                    content=Container(
                      content=AchievementsSection(page),
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
                Tab(
                    text="Profile",
                    icon=Icons.PERSON_OUTLINED,
                    content=Container(
                      content=profile_view,
                      padding=padding.only(top=10, left=10, right=10),
                    ),
                ),
            ],
        ),
        expand=True,
        padding=0,
    )
    
    # Store content area in page session for achievement navigation
    page.session.set("content_area", content_area)
    
    # Handle cleanup
    page.on_view_pop = lambda _: stop_camera()
    page.on_disconnect = lambda _: stop_camera()
    
    # Start with login view
    content_area = Container(
        content=login_view,
        expand=True,
        padding=0,
    )
    
    # Main layout
    page.add(content_area)

ft.app(target=main)
