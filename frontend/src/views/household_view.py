import flet as ft

from api.backend_api import (
    get_my_household,
    get_household_members,
    create_household,
    join_household,
    update_household,
    leave_household,
)


def household_view(page: ft.Page, state, go_home):
    household_name = ft.TextField(label="Household name", width=350)
    household_location = ft.TextField(label="Location", width=350)
    join_household_id = ft.TextField(label="Household ID to join", width=350)

    message = ft.Text("", selectable=True)
    household_info = ft.Text("", selectable=True)
    members_list = ft.Column()

    def show_message(text: str, is_error: bool = False):
        message.value = text
        message.color = ft.Colors.RED if is_error else ft.Colors.GREEN
        page.update()

    def render_household(household: dict):
        state.current_household = household

        household_info.value = (
            f"Household ID: {household.get('id')}\n"
            f"Name: {household.get('name')}\n"
            f"Location: {household.get('location')}"
        )

        household_name.value = household.get("name") or ""
        household_location.value = household.get("location") or ""

        page.update()

    def refresh_household():
        household = get_my_household(state.access_token)
        render_household(household)

    def refresh_members():
        members = get_household_members(state.access_token)
        state.household_members = members

        members_list.controls.clear()

        for member in members:
            members_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON),
                    title=ft.Text(member.get("email", "Unknown")),
                    subtitle=ft.Text(member.get("id", "")),
                )
            )

        page.update()

    def handle_refresh(e=None):
        try:
            refresh_household()
            refresh_members()
            show_message("Household refreshed.")
        except Exception as ex:
            show_message(f"Failed to refresh household: {ex}", True)

    def handle_create_household(e):
        try:
            name = household_name.value.strip()
            location = household_location.value.strip()

            if not name:
                show_message("Household name is required.", True)
                return

            household = create_household(
                state.access_token,
                name,
                location if location else None,
            )

            render_household(household)
            refresh_members()

            show_message("New household created. You have been moved into it.")
        except Exception as ex:
            show_message(f"Failed to create household: {ex}", True)

    def handle_update_household(e):
        try:
            name = household_name.value.strip()
            location = household_location.value.strip()

            if not name:
                show_message("Household name is required.", True)
                return

            household = update_household(
                state.access_token,
                name,
                location if location else None,
            )

            render_household(household)
            show_message("Household updated.")
        except Exception as ex:
            show_message(f"Failed to update household: {ex}", True)

    def handle_join_household(e):
        try:
            household_id = join_household_id.value.strip()

            if not household_id:
                show_message("Please enter a household ID.", True)
                return

            household = join_household(state.access_token, household_id)

            render_household(household)
            refresh_members()

            show_message("Joined household successfully.")
        except Exception as ex:
            show_message(f"Failed to join household: {ex}", True)

    def handle_leave_household(e):
        try:
            household = leave_household(state.access_token)

            render_household(household)
            refresh_members()

            show_message("You left the household and now have a personal household.")
        except Exception as ex:
            show_message(f"Failed to leave household: {ex}", True)

    handle_refresh()

    return ft.View(
        route="/household",
        controls=[
            ft.AppBar(
                title=ft.Text("Household"),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: go_home(),
                ),
            ),
            ft.Container(
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text(
                            "Manage Household",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        message,
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Current household", weight=ft.FontWeight.BOLD),
                                        household_info,
                                        ft.Button(
                                            content="Refresh",
                                            on_click=handle_refresh,
                                        ),
                                    ]
                                ),
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Edit / Create household", weight=ft.FontWeight.BOLD),
                                        household_name,
                                        household_location,
                                        ft.Row(
                                            controls=[
                                                ft.Button(
                                                    content="Update current household",
                                                    on_click=handle_update_household,
                                                ),
                                                ft.Button(
                                                    content="Create new household",
                                                    on_click=handle_create_household,
                                                ),
                                            ],
                                            wrap=True,
                                        ),
                                    ]
                                ),
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Join household", weight=ft.FontWeight.BOLD),
                                        join_household_id,
                                        ft.Button(
                                            content="Join existing household",
                                            on_click=handle_join_household,
                                        ),
                                    ]
                                ),
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Members", weight=ft.FontWeight.BOLD),
                                        members_list,
                                    ]
                                ),
                            )
                        ),
                        ft.Button(
                            content="Leave and create personal household",
                            on_click=handle_leave_household,
                        ),
                    ],
                ),
            ),
        ],
    )