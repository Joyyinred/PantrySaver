import flet as ft

from api.supabase_auth import login, signup
from api.backend_api import sync_user


def login_view(page: ft.Page, state, go_home):
    email_field = ft.TextField(
        label="Email",
        width=350,
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=350,
    )

    message = ft.Text("", color=ft.Colors.RED)

    def set_loading(is_loading: bool):
        login_button.disabled = is_loading
        signup_button.disabled = is_loading
        page.update()

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

            state.access_token = result.get("access_token")
            state.refresh_token = result.get("refresh_token")

            if not state.access_token:
                message.value = "Login failed: no access token returned."
                return

            user = sync_user(state.access_token)
            state.current_user = user
            state.current_household = user.get("household")

            go_home()

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

            state.access_token = result.get("access_token")
            state.refresh_token = result.get("refresh_token")

            if not state.access_token:
                message.value = (
                    "Signup succeeded, but no access token was returned. "
                    "Email confirmation may be enabled in Supabase."
                )
                return

            user = sync_user(state.access_token)
            state.current_user = user
            state.current_household = user.get("household")

            go_home()

        except Exception as ex:
            message.value = f"Signup failed: {ex}"

        finally:
            set_loading(False)

    login_button = ft.Button(
        content="Login",
        width=160,
        on_click=handle_login,
    )

    signup_button = ft.Button(
        content="Sign up",
        width=160,
        on_click=handle_signup,
    )

    return ft.View(
        route="/login",
        controls=[
            ft.SafeArea(
                content=ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        width=400,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "PantrySaver",
                                size=34,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Track food purchases and household waste",
                                size=14,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                            email_field,
                            password_field,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    login_button,
                                    signup_button,
                                ],
                            ),
                            message,
                        ],
                    ),
                )
            )
        ],
    )