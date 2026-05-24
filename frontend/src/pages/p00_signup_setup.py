import flet as ft

from api.supabase_db import create_household, create_user_profile


def SignupSetupPage(auth_result, on_setup_complete):
    user = auth_result.get("user", {})
    access_token = auth_result.get("access_token")

    first_name_input = ft.TextField(label="First Name", width=300)
    last_name_input = ft.TextField(label="Last Name", width=300)
    household_name_input = ft.TextField(label="Household Name", width=300)
    location_input = ft.TextField(label="Location", width=300)

    message_text = ft.Text(
        "",
        color=ft.Colors.RED_700,
        width=300,
        text_align=ft.TextAlign.CENTER,
    )

    def submit_setup(e):
        message_text.value = ""

        first_name = (first_name_input.value or "").strip()
        last_name = (last_name_input.value or "").strip()
        household_name = (household_name_input.value or "").strip()
        location = (location_input.value or "").strip()

        if not first_name or not last_name:
            message_text.value = "Please enter your name."
            view.update()
            return

        if not household_name:
            message_text.value = "Please enter household name."
            view.update()
            return

        try:
            household = create_household(
                access_token=access_token,
                name=household_name,
                location=location,
            )

            user_profile = create_user_profile(
                access_token=access_token,
                user_id=user.get("id"),
                email=user.get("email"),
                household_id=household.get("id"),
                first_name=first_name,
                last_name=last_name,
            )

            on_setup_complete(
                auth_result=auth_result,
                user_profile=user_profile,
                household=household,
            )

        except Exception as ex:
            message_text.value = f"Setup failed. {ex}"
            view.update()

    create_button = ft.FilledButton(
        content=ft.Text(
            "Create Household",
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
        ),
        width=300,
        height=50,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800),
        on_click=submit_setup,
    )

    view = ft.Column(
        [
            ft.Text(
                "PANTRY\nSAVER",
                size=40,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.BLUE_800,
            ),
            ft.Text(
                "Set up your account",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_800,
            ),
            first_name_input,
            last_name_input,
            household_name_input,
            location_input,
            create_button,
            message_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=18,
        tight=True,
    )

    return view