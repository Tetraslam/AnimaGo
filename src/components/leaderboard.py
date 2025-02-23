import flet as ft
from firebase.firebase_config import get_top_users

class LeaderboardSection(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.users = []
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10
        self.expand = True
        self._build()

    def create_user_row(self, rank: int, user: dict) -> ft.Container:
        """Create a leaderboard item for a user"""
        medal_icons = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }
        
        # Create rank display (either medal or number)
        rank_display = medal_icons.get(rank, str(rank))
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Rank column
                    ft.Container(
                        content=ft.Text(
                            rank_display,
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        width=50,
                        alignment=ft.alignment.center
                    ),
                    # User info column
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"{user.get('firstname', 'Unknown')} {user.get('lastname', '')}",
                                    size=16,
                                    weight=ft.FontWeight.W_500
                                ),
                                ft.Text(
                                    f"XP: {user.get('xp', 0):,}",
                                    size=14,
                                    color=ft.colors.GREEN
                                )
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.START
                        ),
                        expand=True
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            margin=ft.margin.only(bottom=5),
            on_click=lambda _: self.show_user_profile(user),
            ink=True,  # Add ripple effect
            data=user  # Store user data for reference
        )

    def show_user_profile(self, user: dict):
        """Show detailed profile view for a user"""
        def close_profile(_):
            # Clear the current view
            self.page.clean()
            
            # Recreate the main content
            content_area = self.page.session.get("content_area")
            if content_area:
                content_area.visible = True
                self.page.add(content_area)
                self.page.update()

        # Hide the main content
        content_area = self.page.session.get("content_area")
        if content_area:
            content_area.visible = False

        # Create profile view
        profile_view = ft.Container(
            content=ft.Column(
                controls=[
                    # Close button
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                icon_color=ft.colors.WHITE,
                                on_click=close_profile,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    # Profile header
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"{user.get('firstname', 'Unknown')} {user.get('lastname', '')}",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Text(
                                    f"XP: {user.get('xp', 0):,}",
                                    size=24,
                                    color=ft.colors.GREEN,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        margin=ft.margin.only(bottom=20)
                    ),
                    # Stats section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Statistics", size=24, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        str(len(user.get('sightings', []))),
                                                        size=24,
                                                        weight=ft.FontWeight.BOLD
                                                    ),
                                                    ft.Text("Sightings")
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                            ),
                                            expand=True
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        str(len(user.get('achievements', []))),
                                                        size=24,
                                                        weight=ft.FontWeight.BOLD
                                                    ),
                                                    ft.Text("Achievements")
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                            ),
                                            expand=True
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                )
                            ],
                            spacing=20
                        ),
                        padding=20,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=10
                    ),
                    # Achievements section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Recent Achievements", size=24, weight=ft.FontWeight.BOLD),
                                *[
                                    ft.Container(
                                        content=ft.Text(achievement.get('achievementName', 'Unknown Achievement')),
                                        padding=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        border_radius=10
                                    )
                                    for achievement in user.get('achievements', [])[:3]  # Show last 3 achievements
                                ]
                            ],
                            spacing=10
                        ),
                        margin=ft.margin.only(top=20)
                    ) if user.get('achievements') else ft.Container()  # Only show if user has achievements
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            expand=True
        )

        # Clear the page and add the profile view
        self.page.clean()
        self.page.add(profile_view)
        self.page.update()

    def create_leaderboard_list(self) -> ft.Column:
        try:
            # Get top 10 users from Firebase
            self.users = get_top_users(10)
            
            # Create list items
            list_items = []
            for i, user in enumerate(self.users, 1):
                if user:  # Only add if user data exists
                    list_items.append(self.create_user_row(i, user))
            
            # If no users found
            if not list_items:
                list_items = [
                    ft.Container(
                        content=ft.Text(
                            "No users found",
                            italic=True,
                            color=ft.colors.GREY_400,
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.alignment.center
                    )
                ]
            
            return ft.Column(
                controls=list_items,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
            
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            return ft.Column(
                controls=[
                    ft.Text(
                        "Error loading leaderboard",
                        color=ft.colors.RED,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.TextButton(
                        "Retry",
                        on_click=lambda _: self.refresh()
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

    def refresh(self, e=None):
        """Refresh the leaderboard data"""
        try:
            self._build()
            self.page.update()
        except Exception as e:
            print(f"Error refreshing leaderboard: {e}")
            self.controls = [
                ft.Text(
                    "Error refreshing leaderboard",
                    color=ft.colors.RED,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.TextButton(
                    "Retry",
                    on_click=self.refresh
                )
            ]
            self.page.update()

    def _build(self):
        """Build the leaderboard layout"""
        try:
            # Title
            header = ft.Container(
                content=ft.Text(
                    "Leaderboard",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                margin=ft.margin.only(bottom=20),
                alignment=ft.alignment.center
            )
            
            # Leaderboard list
            leaderboard_list = self.create_leaderboard_list()
            
            # Update controls
            self.controls = [
                header,
                leaderboard_list
            ]
            
        except Exception as e:
            print(f"Error building leaderboard: {e}")
            self.controls = [
                ft.Text(
                    "Error loading leaderboard",
                    color=ft.colors.RED,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.TextButton(
                    "Retry",
                    on_click=self.refresh
                )
            ]