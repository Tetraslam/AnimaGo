import flet as ft
from typing import List, Optional

class BiodexSpeciesCard(ft.Container):
    def __init__(self, number: int, name: Optional[str] = None):
        super().__init__()
        self.number = number
        self.name = name
        self.width = 160
        self.height = 140
        self.content = self._build_content()
        
    def _build_content(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"#{self.number:03d}",
                        size=14,
                        color=ft.colors.WHITE70 if self.name else ft.colors.WHITE24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "???",
                            size=32,
                            color=ft.colors.WHITE24,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        height=50,
                        margin=ft.margin.only(top=1, bottom=1),
                    ),
                    ft.Container(
                        content=ft.Text(
                            self.name if self.name else "???",
                            size=14,
                            color=ft.colors.WHITE if self.name else ft.colors.WHITE24,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.W_500,
                        ),
                        width=150,
                        height=50,
                        alignment=ft.alignment.center,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            border=ft.border.all(1, ft.colors.WHITE10),
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.colors.BLACK87 if self.name else ft.colors.BLACK54,
            padding=8,
        )

class BiodexSection(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.spacing = 0
        self.expand = True
        
        # Sample discovered species (hardcoded for now)
        self.discovered_species = {
            1: "Red Fox",
            3: "Great Horned Owl",
            4: "Eastern Gray Squirrel"
        }
        
        self._build()
        
    def _build(self):
        # Create exactly 18 species cards
        species_cards = []
        for i in range(18):
            number = i + 1
            name = self.discovered_species.get(number)
            species_cards.append(
                BiodexSpeciesCard(
                    number=number,
                    name=name
                )
            )
        
        # Count discovered species
        total = 18
        discovered = len(self.discovered_species)
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            "BIODEX",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                        margin=ft.margin.only(left=20, top=20, bottom=10),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    f"REPORTED: {discovered}",
                                    color=ft.colors.LIGHT_BLUE_ACCENT_400,
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                                ft.Text(
                                    f"FOUND: {total}",
                                    color=ft.colors.WHITE70,
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ],
                            spacing=20,
                        ),
                        margin=ft.margin.only(left=20, bottom=20),
                    ),
                ]),
                bgcolor=ft.colors.BLACK87,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.ResponsiveRow(
                                controls=[
                                    ft.Container(
                                        content=card,
                                        col=4,
                                        padding=5,
                                    )
                                    for card in species_cards
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            expand=True,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                bgcolor=ft.colors.BLACK,
                padding=5,
            ),
        ]