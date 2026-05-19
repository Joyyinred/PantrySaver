import asyncio
import flet as ft
from components.reuseable_ui_elements import show_big_round_button, show_header

def AccountPage(on_logout_click):

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

    # TODO - should generate a one time code for new user and add to database of household. The new user can use that code to join household, that should erase the code from the database.
    async def on_invite_click(e):
        code_display.opacity = 1
        code_display.update()
        await asyncio.sleep(10)
        code_display.opacity = 0
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
                    ft.Text("John Doe", weight=ft.FontWeight.BOLD, size=20),
                    ft.Text("DOE HOUSEHOLD", size=14, color=ft.Colors.GREY_600),
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