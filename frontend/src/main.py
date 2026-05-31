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

    statistics_content, load_statistics = StatisticsPage(session, page)

    def handle_platform_brightness_change(_=None):
        if session.get("selected_tab_index") == 1:
            load_statistics()
            page.update()

    page.on_platform_brightness_change = handle_platform_brightness_change

    app_tab_content_area = ft.Container(
        content=LogFoodPage(session, page),
        padding=20,
        expand=True,
        alignment=ft.Alignment.TOP_CENTER,
    )

    def show_main_app():
        session["selected_tab_index"] = 0
        app_tab_content_area.content = LogFoodPage(session, page)
        nav_bar.selected_index = 0
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
        nav_bar.selected_index = 0
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
        if session["selected_tab_index"] == selected:
            return

        session["selected_tab_index"] = selected
        nav_bar.selected_index = selected
        page.update()

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

        page.update()
        if selected == 1:
            load_statistics()
            page.update()

    def on_nav_change(e):
        switch_to_tab(e.control.selected_index)

    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_BOX_OUTLINED,
                selected_icon=ft.Icons.ADD_BOX,
                label="Log Food",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.BAR_CHART_OUTLINED,
                selected_icon=ft.Icons.BAR_CHART,
                label="Stats",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LIGHTBULB_OUTLINE,
                selected_icon=ft.Icons.LIGHTBULB,
                label="Tips",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINE,
                selected_icon=ft.Icons.PERSON,
                label="Account",
            ),
        ],
    )

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
