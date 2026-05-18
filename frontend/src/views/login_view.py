import flet as ft

from api.supabase_auth import login, signup
from api.backend_api import sync_user


GREEN = "#4F8A5B"
DARK_GREEN = "#2F5D3A"
CREAM = "#F7F5EF"
CARD = "#FFFFFF"
TEXT_DARK = "#263A29"
TEXT_MUTED = "#6E7D6B"


def primary_button(label, on_click):
    return ft.Button(
        content=label,
        width=320,
        height=48,
        bgcolor=GREEN,
        color="white",
        on_click=on_click,
    )


def secondary_button(label, on_click):
    return ft.Button(
        content=label,
        width=320,
        height=48,
        bgcolor="#E8EFE5",
        color=DARK_GREEN,
        on_click=on_click,
    )


def login_view(page: ft.Page, state, go_home):
    email_field = ft.TextField(
        label="Email",
        width=320,
        keyboard_type=ft.KeyboardType.EMAIL,
        border_radius=14,
        bgcolor="#FAFAFA",
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=320,
        border_radius=14,
        bgcolor="#FAFAFA",
    )

    message = ft.Text("", color=ft.Colors.RED, size=12, width=320)

    def set_loading(is_loading: bool):
        login_button.disabled = is_loading
        signup_button.disabled = is_loading
        page.update()

    def save_session_and_go_home(result):
        state.access_token = result.get("access_token")
        state.refresh_token = result.get("refresh_token")

        if not state.access_token:
            message.value = (
                "No access token returned. If this is signup, check Supabase email confirmation settings."
            )
            return

        user = sync_user(state.access_token)
        state.current_user = user
        state.current_household = user.get("household")

        go_home()

    def handle_login(e):
        try:
            message.value = ""
            set_loading(True)

            email = email_field.value.strip()
            password = password_field.value.strip()

            if not email or not password:
                message.value = "Please enter email and password."
                return

            result = login(email, password)
            save_session_and_go_home(result)

        except Exception as ex:
            message.value = f"Login failed: {ex}"

        finally:
            set_loading(False)

    def handle_signup(e):
        try:
            message.value = ""
            set_loading(True)

            email = email_field.value.strip()
            password = password_field.value.strip()

            if not email or not password:
                message.value = "Please enter email and password."
                return

            result = signup(email, password)
            save_session_and_go_home(result)

        except Exception as ex:
            message.value = f"Signup failed: {ex}"

        finally:
            set_loading(False)

    login_button = primary_button("Login", handle_login)
    signup_button = secondary_button("Create account", handle_signup)

    return ft.View(
        route="/login",
        bgcolor=CREAM,
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    expand=True,
                    padding=24,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(height=28),

                            ft.Container(
                                width=96,
                                height=96,
                                border_radius=48,
                                bgcolor="#E0EAD7",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text("🥬", size=46),
                            ),

                            ft.Text(
                                "PantrySaver",
                                size=34,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_DARK,
                            ),

                            ft.Text(
                                "Save food. Share smarter. Waste less.",
                                size=14,
                                color=TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),

                            ft.Container(height=18),

                            ft.Container(
                                width=360,
                                padding=22,
                                border_radius=24,
                                bgcolor=CARD,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=14,
                                    controls=[
                                        ft.Text(
                                            "Welcome back",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_DARK,
                                        ),
                                        email_field,
                                        password_field,
                                        message,
                                        login_button,
                                        signup_button,
                                    ],
                                ),
                            ),

                            ft.Container(height=14),

                            ft.Text(
                                "Your household food tracker",
                                size=12,
                                color=TEXT_MUTED,
                            ),
                        ],
                    ),
                )
            )
        ],
    )