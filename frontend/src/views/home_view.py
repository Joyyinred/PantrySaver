import flet as ft


GREEN = "#4F8A5B"
DARK_GREEN = "#2F5D3A"
CREAM = "#F7F5EF"
CARD = "#FFFFFF"
TEXT_DARK = "#263A29"
TEXT_MUTED = "#6E7D6B"


def stat_card(title, value, icon):
    return ft.Container(
        width=160,
        padding=16,
        border_radius=20,
        bgcolor=CARD,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(icon, size=26),
                ft.Text(title, size=12, color=TEXT_MUTED),
                ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ],
        ),
    )


def home_view(page: ft.Page, state, go_household, logout):
    user = state.current_user or {}
    household = user.get("household") or state.current_household or {}

    email = user.get("email", "Unknown user")
    household_name = household.get("name", "No household")
    household_id = household.get("id", "")

    short_email = email if len(email) <= 28 else email[:25] + "..."

    return ft.View(
        route="/home",
        bgcolor=CREAM,
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        spacing=18,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                "Hello 👋",
                                                size=16,
                                                color=TEXT_MUTED,
                                            ),
                                            ft.Text(
                                                "PantrySaver",
                                                size=28,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXT_DARK,
                                            ),
                                        ],
                                    ),
                                    ft.Button(
                                        content="Logout",
                                        bgcolor="#E8EFE5",
                                        color=DARK_GREEN,
                                        on_click=lambda e: logout(),
                                    ),
                                ],
                            ),

                            ft.Container(
                                padding=20,
                                border_radius=28,
                                bgcolor=GREEN,
                                content=ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Text(
                                            "Current household",
                                            size=13,
                                            color="#DDEDDD",
                                        ),
                                        ft.Text(
                                            household_name,
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                            color="white",
                                        ),
                                        ft.Text(
                                            short_email,
                                            size=13,
                                            color="#EEF8EE",
                                        ),
                                        ft.Container(height=6),
                                        ft.Button(
                                            content="Manage household",
                                            bgcolor="white",
                                            color=DARK_GREEN,
                                            on_click=lambda e: go_household(),
                                        ),
                                    ],
                                ),
                            ),

                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    stat_card("Purchased", "Coming soon", "🛒"),
                                    stat_card("Discarded", "Coming soon", "🗑️"),
                                ],
                            ),

                            ft.Container(
                                padding=18,
                                border_radius=22,
                                bgcolor=CARD,
                                content=ft.Column(
                                    spacing=10,
                                    controls=[
                                        ft.Text(
                                            "Household ID",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_DARK,
                                        ),
                                        ft.Text(
                                            household_id,
                                            size=12,
                                            selectable=True,
                                            color=TEXT_MUTED,
                                        ),
                                        ft.Text(
                                            "Share this ID only with people you want to join your household.",
                                            size=12,
                                            color=TEXT_MUTED,
                                        ),
                                    ],
                                ),
                            ),

                            ft.Container(
                                padding=18,
                                border_radius=22,
                                bgcolor="#FFF6DD",
                                content=ft.Row(
                                    controls=[
                                        ft.Text("💡", size=28),
                                        ft.Column(
                                            expand=True,
                                            spacing=4,
                                            controls=[
                                                ft.Text(
                                                    "Next step",
                                                    weight=ft.FontWeight.BOLD,
                                                    color=TEXT_DARK,
                                                ),
                                                ft.Text(
                                                    "Food purchase and waste logging pages can be added to this dashboard.",
                                                    size=12,
                                                    color=TEXT_MUTED,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                )
            )
        ],
    )