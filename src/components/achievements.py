import flet as ft
from flet import (
    Container, Column, Row, Text, Icon, Colors, IconButton, 
    Icons, Page, padding, alignment, CrossAxisAlignment, MainAxisAlignment
)
from dataclasses import dataclass

@dataclass
class AchievementData:
    title: str
    description: str
    icon: str
    progress: float  # 0.0 to 1.0
    color: str

def create_achievement_detail_view(achievement: AchievementData, page: Page):
    def close_detail_view(_):
        # Clear the current view
        page.clean()
        
        # Recreate the main content
        content_area = page.session.get("content_area")
        if content_area:
            content_area.visible = True
            page.add(content_area)
            page.update()

    # Calculate responsive sizes based on screen width
    medal_size = min(page.width * 0.8, 300)
    icon_size = medal_size * 0.4

    # Create the detail view
    return Container(
        content=Column(
            controls=[
                # Close button
                Row(
                    controls=[
                        IconButton(
                            icon=Icons.CLOSE,
                            icon_color=Colors.WHITE,
                            on_click=close_detail_view,
                        ),
                    ],
                    alignment=MainAxisAlignment.END,
                ),
                # Medal icon
                Container(
                    content=Icon(
                        name=achievement.icon,
                        size=icon_size,
                        color=achievement.color,
                    ),
                    width=medal_size,
                    height=medal_size,
                    bgcolor="#2A2D3E",
                    border_radius=15,
                    alignment=alignment.center,
                ),
                # Title
                Container(
                    content=Text(
                        achievement.title,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=Colors.WHITE70,
                    ),
                    margin=padding.only(top=20),
                ),
                # Description
                Container(
                    content=Text(
                        achievement.description,
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=Colors.WHITE54,
                    ),
                    margin=padding.only(top=10, left=20, right=20),
                ),
                # Progress
                Container(
                    content=Row(
                        controls=[
                            Container(
                                content=ft.ProgressBar(
                                    value=achievement.progress,
                                    color=achievement.color,
                                    bgcolor=Colors.BLACK26,
                                    height=4,
                                ),
                                expand=True,
                            ),
                            Container(
                                content=Text(
                                    f"{int(achievement.progress * 100)}%",
                                    size=12,
                                    color=Colors.WHITE54,
                                ),
                                margin=padding.only(left=5),
                            ),
                        ],
                    ),
                    margin=padding.only(top=20),
                    width=medal_size,
                ),
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        padding=20,
        margin=5,
        bgcolor="#1F2133",
        border_radius=20,
    )

def create_achievement_card(achievement: AchievementData, page: Page):
    def show_achievement_details(_):
        # Hide current content
        content_area = page.session.get("content_area")
        if content_area:
            content_area.visible = False
        
        # Show achievement detail view
        detail_view = create_achievement_detail_view(achievement, page)
        page.add(detail_view)
        page.update()

    # Calculate card size based on screen width
    card_size = min(page.width * 0.4, 150)
    icon_size = card_size * 0.4

    return Container(
        content=Column(
            controls=[
                Container(
                    content=Icon(
                        name=achievement.icon,
                        size=icon_size,
                        color=achievement.color,
                    ),
                    width=card_size,
                    height=card_size,
                    bgcolor="#2A2D3E",
                    border_radius=15,
                    alignment=alignment.center,
                    on_click=show_achievement_details,
                ),
                Container(
                    content=Text(
                        achievement.title,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=Colors.WHITE70,
                    ),
                    margin=padding.only(top=10),
                ),
                Container(
                    content=Row(
                        controls=[
                            Container(
                                content=ft.ProgressBar(
                                    value=achievement.progress,
                                    color=achievement.color,
                                    bgcolor=Colors.BLACK26,
                                    height=4,
                                ),
                                expand=True,
                            ),
                            Container(
                                content=Text(
                                    f"{int(achievement.progress * 100)}%",
                                    size=12,
                                    color=Colors.WHITE54,
                                ),
                                margin=padding.only(left=5),
                            ),
                        ],
                    ),
                    margin=padding.only(top=5),
                    width=card_size,
                ),
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=10,
        margin=5,
        bgcolor="#1F2133",
        border_radius=20,
    )

class AchievementsSection(ft.Column):
    def __init__(self, page: Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.horizontal_alignment = CrossAxisAlignment.CENTER
        self.achievements = [
            AchievementData(
                title="First Catch",
                description="Find your first animal.",
                icon=Icons.CATCHING_POKEMON,
                progress=1.0,
                color=Colors.YELLOW_ACCENT_400,
            ),
            AchievementData(
                title="First Flight",
                description="Find a flying animal.",
                icon=Icons.FLIGHT,
                progress=1,
                color="#00E676",  # Green
            ),
                        AchievementData(
                title="Biodex Beginner",
                description="Complete 10% of your Biodex.",
                icon=Icons.BOOK,
                progress=0.60,
                color=Colors.ORANGE_ACCENT_400,
            ),
            AchievementData(
                title="Biodex Master",
                description="Complete 75% of your Biodex in a biome.",
                icon=Icons.COMPUTER,
                progress=0.2,
                color="#FFFFFF",  # White
            ),
            AchievementData(
                title="Ears of the Wild",
                description="Identify an animal using only its sound.",
                icon=Icons.HEADSET,
                progress=1,
                color="#FFC107",  # Amber
            ),
            AchievementData(
                title="Night Explorer",
                description="Find an animal at night.",
                icon=Icons.NIGHTLIGHT,
                progress=1,
                color="#9C27B0",
            ),
            AchievementData(
                title="Night Stalker",
                description="Capture 10 different nocturnal animals.",
                icon=Icons.SHIELD_MOON,
                progress=.3,
                color="#35336b",
            ),
            AchievementData(
                title="Nocturnal Listener",
                description="Identify an animal at night using sound recognition.",
                icon=Icons.SHIELD_MOON_SHARP,
                progress=0,
                color="#F6F1D5",
            ),
            AchievementData(
                title="Citizen Scientist",
                description="Log a rare or endangered species.",
                icon=Icons.BIOTECH,
                progress=0,
                color=Colors.GREEN_ACCENT_400,
            ),
            AchievementData(
                title="Trailblazer",
                description="Discover 10 different species.",
                icon=Icons.MAP,
                progress=1,
                color=Colors.BLUE_ACCENT_400,
            ),
            AchievementData(
                title="Data Contributor",
                description="Submit 50 valid sightings.",
                icon=Icons.ADDCHART,
                progress=.84,
                color=Colors.RED_ACCENT_400,
            ),
            AchievementData(
                title="Master Tracker",
                description="Capture 100 different species",
                icon=Icons.FIBER_PIN,
                progress=.42,
                color="#EFBF04", #Gold
            ),
            AchievementData(
                title="On a Roll",
                description="Capture an animal every day for a week.",
                icon=Icons.HOURGLASS_BOTTOM_ROUNDED,
                progress=2/7,
                color=Colors.YELLOW_ACCENT_400,
            ),
            AchievementData(
                title="Wildlife Warrior",
                description="Maintain a daily streak for a month.",
                icon=Icons.CALENDAR_MONTH,
                progress=1/15,
                color="#008000",
            ),
            AchievementData(
                title="Evolutionary Mystery",
                description="Capture a visually distinct species never cataloged before.",
                icon=Icons.ADD_CHART_ROUNDED,
                progress=0,
                color="#717e00",  # Oil Green
            ),
            AchievementData(
                title="Seasonal Explorer",
                description="Capture an animal in each season.",
                icon=Icons.CLOUD,
                progress=.5,
                color="#87CEEB",  # Sky Blue
            ),
            
        ]
        self._build()

    def _build(self):
        # Create rows of achievement pairs
        achievement_rows = []
        for i in range(0, len(self.achievements), 2):
            row_achievements = self.achievements[i:i+2]
            row = Row(
                controls=[
                    create_achievement_card(achievement, self.page)
                    for achievement in row_achievements
                ],
                alignment=MainAxisAlignment.CENTER,
            )
            achievement_rows.append(row)

        # Create scrollable column of rows
        achievement_grid = ft.Column(
            controls=achievement_rows,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=500,  # Set a fixed height to enable scrolling
        )

        # Add controls to self (Column)
        self.controls = [
            Container(
                content=Text(
                    "Achievements",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=Colors.WHITE,
                ),
                margin=padding.only(bottom=20),
            ),
            Container(
                content=achievement_grid,
                bgcolor="#161927",
                border_radius=30,
                padding=20,
            ),
        ]
        self.margin = padding.only(top=20)