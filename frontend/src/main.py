import flet as ft
from init_db import init_database
import os

from pages.p0_login import LoginPage
from pages.p00_signup_setup import SignupSetupPage
from pages.p1_item_entry import LogFoodPage
from pages.p2_statistics import StatisticsPage
from pages.p3_recommendations import RecommendationPage
from pages.p4_account import AccountPage

from api.supabase_db import get_user_profile, get_household

if not os.path.exists('database.db'):
    init_database()

def main(page: ft.Page):
    
    # stores the logged-in Supabase user information while the app is open
    session = {
        "access_token": None,
        "refresh_token": None,
        "user": None,
        "user_profile": None,
        "household": None,

    }
    
    page.title = "Pantry Saver"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_800,
            secondary=ft.Colors.BLUE_600,
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            indicator_color=ft.Colors.BLUE_100,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        )
    )

    print(session)
    log_food_content = LogFoodPage()
    statistics_content = StatisticsPage(session["household"][1])
    recommendations_content = RecommendationPage()

    app_tab_content_area = ft.Container(
        content=log_food_content, 
        padding=20, 
        expand=True, 
        alignment=ft.Alignment.TOP_CENTER
    )
    
    # after login succedds call this function, auth_result is the response from Supabase
    def save_auth_session(auth_result):
        session["access_token"] = auth_result.get("access_token")
        session["refresh_token"] = auth_result.get("refresh_token")
        session["user"] = auth_result.get("user")


    def show_main_app():
        nav_bar.selected_index = 0
        app_tab_content_area.content = log_food_content
        main_container.content = log_food_screen
        page.update()


    def on_login_click(auth_result):
        nonlocal account_content

        save_auth_session(auth_result)

        user = auth_result.get("user")
        access_token = auth_result.get("access_token")

        user_profile = get_user_profile(
            access_token=access_token,
            user_id=user.get("id"),
        )

        household = None

        if user_profile and user_profile.get("household_id"):
            household = get_household(
                access_token=access_token,
                household_id=user_profile.get("household_id"),
            )

        session["user_profile"] = user_profile
        session["household"] = household

        account_content = AccountPage(
            on_logout_click=on_logout_click,
            user_profile=session["user_profile"],
            household=session["household"],
        )

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
        nonlocal account_content

        save_auth_session(auth_result)

        session["user_profile"] = user_profile
        session["household"] = household

        account_content = AccountPage(
            on_logout_click=on_logout_click,
            user_profile=session["user_profile"],
            household=session["household"],
        )

        show_main_app()
    
    def on_logout_click():
        nonlocal account_content

        session["access_token"] = None
        session["refresh_token"] = None
        session["user"] = None
        session["user_profile"] = None
        session["household"] = None
        account_content = None
        
        email_field.value = ""
        password_field.value = ""
        main_container.content = login_form
        page.update()

    login_form, email_field, password_field = LoginPage(
        on_login_click=on_login_click,
        on_signup_click=on_signup_click,)
    
    account_content = None

    def on_tab_change(e):
        tab_routing_map = {
            0: log_food_content,
            1: statistics_content,
            2: recommendations_content,
            3: account_content
        }
        app_tab_content_area.content = tab_routing_map.get(e.control.selected_index, log_food_content)
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.ADD_BOX, label="Log Food"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Statistics"),
            ft.NavigationBarDestination(icon=ft.Icons.LIGHTBULB, label="Recommendations"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Account"),
        ],
        selected_index=0,
        on_change=on_tab_change
    )

    log_food_screen = ft.Column(
        [
            app_tab_content_area,  
            nav_bar
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        expand=True
    )

    main_container = ft.Container(
        content=login_form,
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=main_container,
        )
    )

ft.run(main)
