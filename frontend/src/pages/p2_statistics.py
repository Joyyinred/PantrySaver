import flet as ft
from components.reuseable_ui_elements import show_header, stat_row, show_big_round_button

def StatisticsPage():
    header = show_header(
        title="Statistics",
        subtitle="Your household waste distribution ratios:"
    )

    stats_data = [
        ("Milk", 0.95), ("Bread", 0.88), ("Eggs", 0.75), ("Cheese", 0.65),
        ("Yogurt", 0.60), ("Butter", 0.55), ("Chicken", 0.40), ("Beef", 0.35),
        ("Apples", 0.30), ("Oranges", 0.25), ("Bananas", 0.20), ("Carrots", 0.15),
        ("Potatoes", 0.10), ("Onions", 0.05), ("Tomatoes", 0.85), ("Cucumber", 0.70),
        ("Spinach", 0.62), ("Broccoli", 0.58), ("Pasta", 0.52), ("Rice", 0.48),
        ("Beans", 0.42), ("Lentils", 0.38), ("Coffee", 0.33), ("Tea", 0.28),
        ("Sugar", 0.22), ("Flour", 0.18), ("Cereal", 0.12), ("Oats", 0.08),
        ("Honey", 0.04), ("Jam", 0.90), ("Peanut Butter", 0.82), ("Chocolate", 0.78)
    ]

    stat_bars = []

    for label, value in stats_data:
        stat_bars.append(stat_row(label, value))


    toggle_stats_btn = show_big_round_button(ft.Icons.PIE_CHART, ft.Colors.BLUE_800)

    def toggle_statistics(e):
        if toggle_stats_btn.style.bgcolor == ft.Colors.BLUE_800:
            toggle_stats_btn.style.bgcolor = ft.Colors.ORANGE_400
        else:
            toggle_stats_btn.style.bgcolor = ft.Colors.BLUE_800

        toggle_stats_btn.update()

    toggle_stats_btn.on_click = toggle_statistics

    floating_action_layout = ft.Row(
        [ft.Column([toggle_stats_btn], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END)],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.MainAxisAlignment.END,
        expand=True
    )

    content = ft.Column(
        [
            header,
            ft.Container(
                content=floating_action_layout,
                padding=ft.Padding(top=0, bottom=20, left=0, right=20),
                height=100
            ),
            ft.Container(
                content=ft.Column(
                    controls=stat_bars,
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                padding=20,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    return content