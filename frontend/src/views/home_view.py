import flet as ft


def home_view(page: ft.Page, state, go_household, logout):
    user = state.current_user or {}
    household = user.get("household") or state.current_household or {}

    email = user.get("email", "Unknown user")
    household_name = household.get("name", "No household")
    household_id = household.get("id", "")

    return ft.View(
        route="/home",
        controls=[
            ft.AppBar(
                title=ft.Text("PantrySaver"),
                actions=[
                    ft.Button(content="Logout", on_click=lambda e: logout()),
                ],
            ),
            ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Home",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Current user", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Email: {email}"),
                                    ]
                                ),
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Current household", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Name: {household_name}"),
                                        ft.Text(f"ID: {household_id}", selectable=True),
                                    ]
                                ),
                            )
                        ),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Manage household",
                                    on_click=lambda e: go_household(),
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Food purchase and waste pages can be connected here later.",
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                ),
            ),
        ],
    )