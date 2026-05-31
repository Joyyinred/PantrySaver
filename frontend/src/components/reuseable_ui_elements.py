import flet as ft

def show_header(title: str, subtitle: str):
    header = ft.Column(
        [
            ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(subtitle, color=ft.Colors.GREY_600),
            ft.Divider(height=20)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return header

def show_big_round_button(icn_name: str, clr: str):
    button = ft.FilledButton(
        content=ft.Icon(icn_name, size=24, color=ft.Colors.WHITE),
        width=64,
        height=64,
        style=ft.ButtonStyle(
            bgcolor=clr,
            shape=ft.CircleBorder(),
            padding=0
        )
    )

    return button

# helper for stat row
def get_color_by_value(value):

    if value < 0.3:
        return ft.Colors.YELLOW_300
    elif value < 0.6:
        return ft.Colors.ORANGE_400
    elif value < 0.8:
        return ft.Colors.RED_400
    else:
        return ft.Colors.RED_800

def stat_row(label, value):
    bar_color = get_color_by_value(value)

    return ft.Column([
        ft.Text(f"{label} - {int(value * 100)}%", weight=ft.FontWeight.W_500),
        ft.ProgressBar(
            value=value,
            color=bar_color,
            bgcolor=ft.Colors.GREY_200,
            width=300
        ),
    ], spacing=5)
