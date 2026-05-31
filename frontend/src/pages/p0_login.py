import flet as ft
import re
from api.supabase_auth import login, signup


def is_valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def LoginPage(on_login_click, on_signup_click):

    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=300,
    )
    confirm_password_input = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=300,
        visible=False,
    )
    message_text = ft.Text(
        "",
        color=ft.Colors.RED_700,
        width=300,
        text_align=ft.TextAlign.CENTER,
    )

    is_signup = [False]

    # login and signup handler
    def submit_auth(e):
        message_text.value = ""

        email = (email_input.value or "").strip()
        password = password_input.value or ""
        confirm_password = confirm_password_input.value or ""

        if not is_valid_email(email):
            message_text.value = "Please enter a valid email address."
            view.update()
            return

        if is_signup[0] and password != confirm_password:
            message_text.value = "Passwords do not match."
            view.update()
            return

        try:
            if is_signup[0]:
                result = signup(email, password)
                on_signup_click(result)
            else:
                result = login(email, password)
                on_login_click(result)


        except Exception as ex:
            error_text = str(ex).lower()

            if is_signup[0]:
                if "user_already_exists" in error_text or "user already registered" in error_text:
                    message_text.value = "User already exists."
                elif "weak_password" in error_text:
                    message_text.value = "Password should be at least 6 characters."
                else:
                    message_text.value = "Signup failed. Please try again."
            else:
                message_text.value = "Email or password is not correct."

            view.update()

    login_button = ft.FilledButton(
        content=ft.Text("Login", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        width=300,
        height=50,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800),
        on_click=submit_auth # change this to really use supabase
    )

    def toggle_mode(e):
        is_signup[0] = not is_signup[0]
        confirm_password_input.visible = is_signup[0]
        message_text.value = ""

        if is_signup[0]:
            login_button.content.value = "Sign Up"
            signup_text.value = "Already have an account? Sign in"
        else:
            login_button.content.value = "Login"
            signup_text.value = "Don't have an account? Sign up"
        view.update()

    signup_text = ft.Text(
        "Don't have an account? Sign up",
        color=ft.Colors.BLUE_800, text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.W_100
        )

    signup_container = ft.GestureDetector(content=signup_text, on_tap=toggle_mode)

    view = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("PANTRY\nSAVER",
                                size=40,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                                color=ft.Colors.BLUE_800
                                ),
                        email_input,
                        password_input,
                        confirm_password_input,
                        login_button,
                        signup_container,
                        message_text, # add error message
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
            ),
        ],

        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True,
    )

    return view, email_input, password_input
