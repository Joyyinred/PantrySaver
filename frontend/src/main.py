import os

import flet as ft

from api.supabase_db import get_admin_profile, get_household, get_user_profile
from init_db import init_database
from pages.p000_admin import AdminDashboardPage
from pages.p00_signup_setup import SignupSetupPage
from pages.p0_login import LoginPage
from pages.p1_item_entry import LogFoodPage
from pages.p2_statistics import StatisticsPage
from pages.p3_recommendations import RecommendationPage
from pages.p4_account import AccountPage


if not os.path.exists("database.db"):
    init_database()


def main(page: ft.Page):
    session = {
        "access_token": None,
        "refresh_token": None,
        "user": None,
        "user_profile": None,
        "household": None,
        "selected_tab_index": 0,
    }

    page.title = "Pantry Saver"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_800,
            secondary=ft.Colors.BLUE_600,
        ),
    )

    statistics_content, load_statistics = StatisticsPage(session)

    app_tab_content_area = ft.Container(
        content=LogFoodPage(session, page),
        padding=20,
        expand=True,
        alignment=ft.Alignment.TOP_CENTER,
    )

    def show_main_app():
        session["selected_tab_index"] = 0
        app_tab_content_area.content = LogFoodPage(session, page)
        update_nav_bar()
        main_container.content = log_food_screen
        page.update()

    def save_auth_session(auth_result):
        session["access_token"] = auth_result.get("access_token")
        session["refresh_token"] = auth_result.get("refresh_token")
        session["user"] = auth_result.get("user")

    def on_login_click(auth_result):
        save_auth_session(auth_result)

        user = auth_result.get("user")
        access_token = auth_result.get("access_token")

        admin_profile = get_admin_profile(
            access_token=access_token,
            user_id=user.get("id"),
            email=user.get("email"),
        )

        if admin_profile:
            admin_profile["email"] = admin_profile.get("email") or user.get("email")
            admin_profile["access_token"] = access_token
            session["user_profile"] = None
            session["household"] = None
            show_admin_app(admin_profile)
            return

        user_profile = get_user_profile(
            access_token=access_token,
            user_id=user.get("id"),
        )

        if user_profile:
            user_profile["access_token"] = access_token

        household = None
        if user_profile and user_profile.get("household_id"):
            household = get_household(
                access_token=access_token,
                household_id=user_profile.get("household_id"),
            )

        session["user_profile"] = user_profile
        session["household"] = household

        show_main_app()

    def on_signup_click(auth_result):
        save_auth_session(auth_result)

        setup_form = SignupSetupPage(
            auth_result=auth_result,
            on_setup_complete=on_setup_complete,
        )

        main_container.content = setup_form
        page.update()

    def on_setup_complete(auth_result, user_profile, household):
        save_auth_session(auth_result)
        access_token = auth_result.get("access_token")

        if user_profile:
            user_profile["access_token"] = access_token

        session["user_profile"] = user_profile
        session["household"] = household

        show_main_app()

    def on_logout_click(e=None):
        session["access_token"] = None
        session["refresh_token"] = None
        session["user"] = None
        session["user_profile"] = None
        session["household"] = None

        email_field.value = ""
        password_field.value = ""
        session["selected_tab_index"] = 0
        update_nav_bar()
        main_container.content = login_form
        page.update()

    def show_login_screen(e=None):
        email_field.value = ""
        password_field.value = ""
        main_container.content = login_form
        page.update()

    def show_admin_app(admin_profile):
        main_container.content = AdminDashboardPage(
            admin_profile=admin_profile,
            on_logout=show_login_screen,
            page=page,
        )
        page.update()

    login_form, email_field, password_field = LoginPage(
        on_login_click=on_login_click,
        on_signup_click=on_signup_click,
    )

    def switch_to_tab(selected):
        session["selected_tab_index"] = selected

        if selected == 0:
            app_tab_content_area.content = LogFoodPage(session, page)
        elif selected == 1:
            app_tab_content_area.content = statistics_content
        elif selected == 2:
            app_tab_content_area.content = RecommendationPage(session, page)
        elif selected == 3:
            app_tab_content_area.content = AccountPage(
                on_logout_click=on_logout_click,
                user_profile=session.get("user_profile"),
                household=session.get("household"),
            )

        update_nav_bar()
        page.update()
        if selected == 1:
            load_statistics()
            page.update()

    nav_items = [
        (ft.Icons.ADD_BOX_OUTLINED, ft.Icons.ADD_BOX, "Log Food"),
        (ft.Icons.BAR_CHART_OUTLINED, ft.Icons.BAR_CHART, "Stats"),
        (ft.Icons.LIGHTBULB_OUTLINE, ft.Icons.LIGHTBULB, "Tips"),
        (ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, "Account"),
    ]
    nav_row = ft.Row(
        spacing=4,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    nav_bar = ft.Container(
        content=nav_row,
        height=82,
        padding=ft.Padding(top=8, right=10, bottom=10, left=10),
        bgcolor=ft.Colors.WHITE,
        border=ft.Border(top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100)),
    )

    def build_nav_item(index, outline_icon, selected_icon, label):
        selected = session["selected_tab_index"] == index
        color = ft.Colors.BLUE_800 if selected else ft.Colors.BLUE_GREY_500
        bg_color = "#E8F2FF" if selected else ft.Colors.TRANSPARENT

        return ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            selected_icon if selected else outline_icon,
                            size=24 if selected else 22,
                            color=color,
                        ),
                        ft.Text(
                            label,
                            size=11,
                            weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_500,
                            color=color,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=82,
                height=58,
                padding=ft.Padding(top=6, right=4, bottom=5, left=4),
                bgcolor=bg_color,
                border_radius=22,
                animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            ),
            expand=True,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _, tab_index=index: switch_to_tab(tab_index),
        )

    def update_nav_bar():
        nav_row.controls = [
            build_nav_item(index, outline_icon, selected_icon, label)
            for index, (outline_icon, selected_icon, label) in enumerate(nav_items)
        ]

    update_nav_bar()

    log_food_screen = ft.Column(
        [
            app_tab_content_area,
            nav_bar,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        expand=True,
    )

    main_container = ft.Container(
        content=login_form,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=main_container,
        )
    )


if __name__ == "__main__":
    ft.run(main)
