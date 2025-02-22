import flet as ft
from flet import (Colors, Column, Container, ElevatedButton, Icon, IconButton,
                  Icons, Image, Page, Row, Tab, Tabs, Text, View, padding)


def main(page: ft.Page):
    # App configuration
    page.title = "AnimaGo"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = padding.only(top=50)  # Add safe area padding at the top
    page.window_bgcolor = Colors.TRANSPARENT  # Make sure padding color matches theme
    
    # Define reusable colors
    CARD_COLOR = Colors.BLUE_GREY_800
    
    def handle_camera_upload(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        # Show loading state
        content_area.content = Column(
            controls=[
                Text("Processing image...", size=20),
                ft.ProgressRing(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()
        
        # TODO: Process image with vision system
        # For now, just show a success message
        content_area.content = Column(
            controls=[
                Text("Found:", size=24, weight=ft.FontWeight.BOLD),
                Text("• Red Fox (87% confidence)", color=Colors.GREEN),
                Text("• European Rabbit (92% confidence)", color=Colors.GREEN),
                Container(height=20),
                ElevatedButton(
                    "Capture Another",
                    icon=Icons.CAMERA_ALT,
                    on_click=lambda _: file_picker.pick_files(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()
    
    # File picker for camera simulation
    file_picker = ft.FilePicker(
        on_result=handle_camera_upload
    )
    page.overlay.append(file_picker)
    
    # View: Capture
    capture_view = Column(
        controls=[
            Text("Ready to discover wildlife?", size=32, weight=ft.FontWeight.BOLD),
            Text("Point your camera at an animal to begin", size=16),
            Container(height=20),
            ElevatedButton(
                "Open Camera",
                icon=Icons.CAMERA_ALT,
                on_click=lambda _: file_picker.pick_files(),
            ),
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
            Row(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Icon(Icons.PETS, size=30),
                                Text("Red Fox", size=14),
                                Text("2 km away", size=12, color=Colors.GREY_400),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                        bgcolor=CARD_COLOR,
                        border_radius=10,
                    ),
                    Container(
                        content=Column(
                            controls=[
                                Icon(Icons.PETS, size=30),
                                Text("Rabbit", size=14),
                                Text("0.5 km away", size=12, color=Colors.GREY_400),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
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
            Text("Profile", size=32, weight=ft.FontWeight.BOLD),
            Container(
                content=Column(
                    controls=[
                        Icon(Icons.ACCOUNT_CIRCLE, size=80),
                        Text("Guest User", size=24),
                        Container(height=10),
                        Row(
                            controls=[
                                Icon(Icons.STAR, color=Colors.YELLOW),
                                Text("Level 1", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        Container(height=20),
                        ElevatedButton(
                            "Sign In",
                            icon=Icons.LOGIN,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                    content=capture_view,
                ),
                Tab(
                    text="Map",
                    icon=Icons.MAP_OUTLINED,
                    content=map_view,
                ),
                Tab(
                    text="Biodex",
                    icon=Icons.MENU_BOOK_OUTLINED,
                    content=biodex_view,
                ),
                Tab(
                    text="Profile",
                    icon=Icons.PERSON_OUTLINED,
                    content=profile_view,
                ),
            ],
        ),
        expand=True,
    )
    
    # Main layout
    page.add(content_area)

ft.app(target=main)
