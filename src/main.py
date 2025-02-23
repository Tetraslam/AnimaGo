import base64
import io
import threading
import time
from dataclasses import dataclass

import cv2
import flet as ft
import numpy as np
import requests
from flet import (Colors, Column, Container, ElevatedButton, Icon, IconButton,
                  Icons, Image, Page, Row, Tab, Tabs, Text, View, padding)
from PIL import Image as PILImage

from components.achievements import AchievementsSection
from components.leaderboard import LeaderboardSection

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
            camera = cv2.VideoCapture(0)
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
    
    def handle_capture(frame):
        global img_byte_arr, img_base64  # Make these variables accessible in process_image
        
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert frame to format Flet can display
        pil_image = PILImage.fromarray(rgb_frame)
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode()
        
        # Immediately call process_image instead of waiting for button click
        process_image(None)  # Pass None since we don't need the event parameter
    
    def process_image(e):
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
                    "file": ("image.png", io.BytesIO(img_byte_arr), "image/png")
                }
                response = requests.post("http://localhost:8000/moondream/describe", files=files)
                
                if response.status_code != 200:
                    error_detail = response.json().get('detail', 'Unknown error')
                    raise Exception(f"API request failed: {error_detail}")
                    
                result = response.json()
                description = result.get('description', 'No description available')
                
                # Display results
                content_area.content = Column(
                    controls=[
                        Text("Analysis:", size=24, weight=ft.FontWeight.BOLD),
                        Image(
                            src_base64=img_base64,
                            width=300,
                            height=300,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        Container(height=10),
                        Text(description, size=16),
                        Container(height=20),
                        ElevatedButton(
                            "Capture Another",
                            icon=Icons.CAMERA_ALT,
                            on_click=lambda _: start_camera(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            except Exception as e:
                # Handle any errors during processing
                content_area.content = Column(
                    controls=[
                        Text("Error processing image", size=24, color=Colors.RED),
                        Text(str(e), size=16),
                        Container(height=20),
                        ElevatedButton(
                            "Try Again",
                            icon=Icons.CAMERA_ALT,
                            on_click=lambda _: start_camera(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
        except Exception as e:
            # Handle any errors during processing
            content_area.content = Column(
                controls=[
                    Text("Error processing image", size=24, color=Colors.RED),
                    Text(str(e), size=16),
                    Container(height=20),
                    ElevatedButton(
                        "Try Again",
                        icon=Icons.CAMERA_ALT,
                        on_click=lambda _: start_camera(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        finally:
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
    map_view = Column(
        controls=[
            Text("Nearby Wildlife", size=32, weight=ft.FontWeight.BOLD),
            Container(
                content=Text("Map coming soon!", size=16),
                bgcolor=CARD_COLOR,
                border_radius=10,
                padding=20,
                margin=10,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # View: Biodex
    biodex_view = Column(
        controls=[
            Text("Your Biodex", size=32, weight=ft.FontWeight.BOLD),
            Text("Animals you've discovered", size=16),
            Container(height=20),
            Row(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Icon(Icons.PETS, size=40, color=Colors.GREEN),
                                Text("Red Fox", size=16),
                                Text("Common", size=12, color=Colors.GREY_400),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor=CARD_COLOR,
                        border_radius=10,
                    ),
                    Container(
                        content=Column(
                            controls=[
                                Icon(Icons.PETS, size=40, color=Colors.BLUE),
                                Text("Rabbit", size=16),
                                Text("Common", size=12, color=Colors.GREY_400),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor=CARD_COLOR,
                        border_radius=10,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
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
                    text="Leaderboard",
                    icon=Icons.LEADERBOARD_OUTLINED,
                    content=leaderboard_view,
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
    
    # Main layout
    page.add(content_area)

ft.app(target=main)
