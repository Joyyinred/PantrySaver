import asyncio
import flet as ft
from components.reuseable_ui_elements import show_big_round_button, show_header
from api.backend_api import generate_join_code

def AccountPage(on_logout_click, user_profile=None, household=None, access_token=None):

    first_name = ""
    last_name = ""
    

    if user_profile:
        first_name = user_profile.get("first_name") or ""
        last_name = user_profile.get("last_name") or ""

    full_name = f"{first_name} {last_name}".strip()

    if not full_name:
        full_name = "Unknown user"

    household_name = "No household"

    if household:
        household_name = household.get("name") or "No household"

    header = show_header(
        title="My Account",
        subtitle="Manage your household and invite members!"
    )

    code_display = ft.Text(
        "12345", 
        size=40, 
        weight=ft.FontWeight.BOLD, 
        color=ft.Colors.BLUE_800,
        opacity=0, 
        animate_opacity=1000
    )

    async def on_invite_click(e):
        print(access_token)
        try:
            code = generate_join_code(access_token)
            code_display.value = code
            code_display.opacity = 1
            code_display.update()
            await asyncio.sleep(10)
            code_display.opacity = 0
            code_display.update()
        except Exception as ex:
            print("Invite error:", ex)
            if hasattr(ex, 'response'):
                print("Response content:", ex.response.text) 
            code_display.opacity = 1
            code_display.update()

    logout_btn = show_big_round_button(ft.Icons.LOGOUT, ft.Colors.RED_700)
    logout_btn.on_click = on_logout_click
    
    invite_btn = show_big_round_button(ft.Icons.GROUP_ADD, ft.Colors.BLUE_800)
    invite_btn.on_click = on_invite_click

    return ft.Column(
        [
            ft.Column(
                [
                    header,
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color=ft.Colors.BLUE_800),
                    ft.Text(full_name, weight=ft.FontWeight.BOLD, size=20),
                    ft.Text(household_name.upper(), size=14, color=ft.Colors.GREY_600),
                    code_display, 
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True
            ),
            ft.Container(
                content=ft.Column(
                    [logout_btn, invite_btn],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
                padding=ft.Padding(top=0, bottom=20, left=0, right=20),
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True
    )