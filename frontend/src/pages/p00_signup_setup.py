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

    setup_mode = {
        "value": "choice"
    }

    def save_user_with_household(household):
        first_name = (first_name_input.value or "").strip()
        last_name = (last_name_input.value or "").strip()

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

    def validate_name():
        first_name = (first_name_input.value or "").strip()
        last_name = (last_name_input.value or "").strip()

        if not first_name or not last_name:
            message_text.value = "Please enter your name."
            view.controls = get_name_controls()
            view.update()
            return False

        return True

    def show_choice(e=None):
        message_text.value = ""

        if not validate_name():
            return

        setup_mode["value"] = "choice"
        view.controls = get_choice_controls()
        view.update()

    def show_create_household(e=None):
        message_text.value = ""

        if not validate_name():
            return

        setup_mode["value"] = "create"
        view.controls = get_create_household_controls()
        view.update()

    def show_join_household(e=None):
        message_text.value = "Join household will be added later."
        view.controls = get_choice_controls()
        view.update()

    def submit_create_household(e):
        message_text.value = ""

        household_name = (household_name_input.value or "").strip()
        location = (location_input.value or "").strip()

        if not household_name:
            message_text.value = "Please enter household name."
            view.controls = get_create_household_controls()
            view.update()
            return

        try:
            household = create_household(
                access_token=access_token,
                name=household_name,
                location=location,
            )

            save_user_with_household(household)

        except Exception as ex:
            message_text.value = f"Setup failed. {ex}"
            view.controls = get_create_household_controls()
            view.update()

    def title_controls():
        return [
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
        ]

    def get_name_controls():
        return [
            *title_controls(),
            first_name_input,
            last_name_input,
            ft.FilledButton(
                content=ft.Text(
                    "Continue",
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
                width=300,
                height=50,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800),
                on_click=show_choice,
            ),
            message_text,
        ]

    def get_choice_controls():
        return [
            *title_controls(),
            ft.Text(
                "Do you want to create or join a household?",
                width=300,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.GREY_700,
            ),
            ft.FilledButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.HOME, color=ft.Colors.WHITE),
                        ft.Text(
                            "Create Household",
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                width=300,
                height=50,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800),
                on_click=show_create_household,
            ),
            ft.FilledButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.GROUP_ADD, color=ft.Colors.WHITE),
                        ft.Text(
                            "Join Household",
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                width=300,
                height=50,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600),
                on_click=show_join_household,
            ),
            message_text,
        ]

    def get_create_household_controls():
        return [
            *title_controls(),
            household_name_input,
            location_input,
            ft.FilledButton(
                content=ft.Text(
                    "Create Household",
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
                width=300,
                height=50,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800),
                on_click=submit_create_household,
            ),
            ft.TextButton(
                "Back",
                on_click=show_choice,
            ),
            message_text,
        ]

    view = ft.Column(
        get_name_controls(),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=18,
        tight=True,
    )

    return view