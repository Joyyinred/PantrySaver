import flet as ft
from components.reuseable_ui_elements import show_header, stat_row, show_big_round_button
from db import supabase

def StatisticsPage(household_id):
    header = show_header(
        title="Statistics",
        subtitle="Your household waste distribution ratios:"
    )

    response = (
        supabase.table("ratios")
        .select("*")
        .eq("household_id", household_id)
        .execute()
    )

    stats_data = [
        (item["item_name"], item["ratio"])
        for item in response.data
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