import flet as ft

from state.app_state import AppState
from views.login_view import login_view
from views.home_view import home_view
from views.household_view import household_view


def main(page: ft.Page):
    page.title = "PantrySaver"

    # Mobile-like window size
    page.window_width = 410
    page.window_height = 780
    page.window_resizable = False

    page.padding = 0
    page.bgcolor = "#F7F5EF"

    page.theme = ft.Theme(
        color_scheme_seed="#4F8A5B",
        font_family="Arial",
    )

    state = AppState()

    def go_home():
        page.go("/home")

    def go_household():
        page.go("/household")

    def logout():
        state.access_token = None
        state.refresh_token = None
        state.current_user = None
        state.current_household = None
        state.household_members = []
        page.go("/login")

    def route_change(route):
        page.views.clear()

        if page.route == "/login":
            page.views.append(
                login_view(
                    page=page,
                    state=state,
                    go_home=go_home,
                )
            )

        elif page.route == "/home":
            if not state.access_token:
                page.go("/login")
                return

            page.views.append(
                home_view(
                    page=page,
                    state=state,
                    go_household=go_household,
                    logout=logout,
                )
            )

        elif page.route == "/household":
            if not state.access_token:
                page.go("/login")
                return

            page.views.append(
                household_view(
                    page=page,
                    state=state,
                    go_home=go_home,
                )
            )

        else:
            page.go("/login")
            return

        page.update()

    def view_pop(view):
        page.views.pop()

        if page.views:
            page.go(page.views[-1].route)
        else:
            page.go("/login")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/login")


ft.run(main)