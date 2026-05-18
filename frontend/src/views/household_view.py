import flet as ft

from api.backend_api import (
    get_my_household,
    get_household_members,
    create_household,
    join_household,
    update_household,
    leave_household,
)


GREEN = "#4F8A5B"
DARK_GREEN = "#2F5D3A"
CREAM = "#F7F5EF"
CARD = "#FFFFFF"
TEXT_DARK = "#263A29"
TEXT_MUTED = "#6E7D6B"


def primary_button(label, on_click):
    return ft.Button(
        content=label,
        height=44,
        bgcolor=GREEN,
        color="white",
        on_click=on_click,
    )


def soft_button(label, on_click):
    return ft.Button(
        content=label,
        height=44,
        bgcolor="#E8EFE5",
        color=DARK_GREEN,
        on_click=on_click,
    )


def danger_button(label, on_click):
    return ft.Button(
        content=label,
        height=44,
        bgcolor="#F8E1DD",
        color="#9B2F22",
        on_click=on_click,
    )


def section_card(title, controls):
    return ft.Container(
        padding=18,
        border_radius=24,
        bgcolor=CARD,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                *controls,
            ],
        ),
    )


def household_view(page: ft.Page, state, go_home):
    household_name = ft.TextField(
        label="Household name",
        width=320,
        border_radius=14,
        bgcolor="#FAFAFA",
    )

    household_location = ft.TextField(
        label="Location",
        width=320,
        border_radius=14,
        bgcolor="#FAFAFA",
    )

    join_household_id = ft.TextField(
        label="Household ID to join",
        width=320,
        border_radius=14,
        bgcolor="#FAFAFA",
    )

    message = ft.Text("", selectable=True, size=12)
    household_info = ft.Text("", selectable=True, size=12, color=TEXT_MUTED)
    members_list = ft.Column(spacing=8)

    def show_message(text: str, is_error: bool = False):
        message.value = text
        message.color = "#B3261E" if is_error else GREEN
        page.update()

    def render_household(household: dict):
        state.current_household = household

        household_info.value = (
            f"ID: {household.get('id')}\n"
            f"Name: {household.get('name')}\n"
            f"Location: {household.get('location') or 'Not set'}"
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
                ft.Container(
                    padding=12,
                    border_radius=16,
                    bgcolor="#F4F7F1",
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=36,
                                height=36,
                                border_radius=18,
                                bgcolor="#DDEDDD",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text("👤", size=18),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        member.get("email", "Unknown"),
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_DARK,
                                    ),
                                    ft.Text(
                                        member.get("id", ""),
                                        size=10,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
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

            show_message("You now have a personal household.")
        except Exception as ex:
            show_message(f"Failed to leave household: {ex}", True)

    handle_refresh()

    return ft.View(
        route="/household",
        bgcolor=CREAM,
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=16,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Button(
                                        content="←",
                                        width=44,
                                        height=44,
                                        bgcolor="#E8EFE5",
                                        color=DARK_GREEN,
                                        on_click=lambda e: go_home(),
                                    ),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                "Household",
                                                size=26,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXT_DARK,
                                            ),
                                            ft.Text(
                                                "Manage your shared pantry group",
                                                size=12,
                                                color=TEXT_MUTED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),

                            message,

                            section_card(
                                "Current household",
                                [
                                    household_info,
                                    soft_button("Refresh", handle_refresh),
                                ],
                            ),

                            section_card(
                                "Edit current household",
                                [
                                    household_name,
                                    household_location,
                                    primary_button("Update household", handle_update_household),
                                    soft_button("Create new household", handle_create_household),
                                ],
                            ),

                            section_card(
                                "Join another household",
                                [
                                    join_household_id,
                                    primary_button("Join household", handle_join_household),
                                    ft.Text(
                                        "Joining another household will move you out of your current one.",
                                        size=11,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),

                            section_card(
                                "Members",
                                [
                                    members_list,
                                ],
                            ),

                            section_card(
                                "Leave household",
                                [
                                    ft.Text(
                                        "This creates a new personal household for you.",
                                        size=12,
                                        color=TEXT_MUTED,
                                    ),
                                    danger_button(
                                        "Leave and become solo",
                                        handle_leave_household,
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )
        ],
    )