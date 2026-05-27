import math
import flet as ft
import flet.canvas as cv
from components.reuseable_ui_elements import show_header, stat_row, show_big_round_button
from db import supabase

PIE_COLORS = [
    ft.Colors.BLUE_400, ft.Colors.RED_400, ft.Colors.GREEN_400,
    ft.Colors.ORANGE_400, ft.Colors.PURPLE_400, ft.Colors.TEAL_400,
    ft.Colors.PINK_400, ft.Colors.AMBER_400, ft.Colors.CYAN_400,
    ft.Colors.LIME_400,
]

def build_pie_canvas(data, size=260):
    if not data:
        return ft.Container(height=size)

    cx = cy = size / 2
    r = size / 2 - 20
    shapes = []
    start_angle = -math.pi / 2

    for i, item in enumerate(data):
        ratio = item["portion"]
        if ratio <= 0:
            continue
        sweep = ratio * 2 * math.pi
        end_angle = start_angle + sweep
        mid_angle = start_angle + sweep / 2

        steps = max(3, int(sweep * 30))
        angles = [start_angle + sweep * j / steps for j in range(steps + 1)]

        elements = [cv.Path.MoveTo(cx, cy)]
        for angle in angles:
            elements.append(cv.Path.LineTo(cx + r * math.cos(angle), cy + r * math.sin(angle)))
        elements.append(cv.Path.Close())

        shapes.append(cv.Path(
            elements=elements,
            paint=ft.Paint(color=PIE_COLORS[i % len(PIE_COLORS)], style=ft.PaintingStyle.FILL)
        ))

        if ratio > 0.05:
            label_r = r * 0.65
            shapes.append(cv.Text(
                x=cx + label_r * math.cos(mid_angle),
                y=cy + label_r * math.sin(mid_angle),
                value=item["item_name"],
                style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                text_align=ft.TextAlign.CENTER,
            ))

        start_angle = end_angle

    return cv.Canvas(shapes=shapes, width=size, height=size)


def StatisticsPage(session):
    header = show_header(
        title="Statistics",
        subtitle="Your household waste distribution ratios:"
    )

    showing_pie = False

    toggle_stats_btn = show_big_round_button(ft.Icons.PIE_CHART, ft.Colors.BLUE_800)

    stat_bars_column = ft.Column(
        controls=[],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    pie_canvas_container = ft.Container(height=260, alignment=ft.Alignment.CENTER)
    legend_column = ft.Column(controls=[], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.START)
    pie_view = ft.Column([pie_canvas_container, legend_column], spacing=12)

    view_container = ft.Container(
        content=stat_bars_column,
        expand=True,
        padding=20,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    def toggle_statistics(_):
        nonlocal showing_pie
        showing_pie = not showing_pie
        view_container.content = pie_view if showing_pie else stat_bars_column
        toggle_stats_btn.style.bgcolor = ft.Colors.ORANGE_400 if showing_pie else ft.Colors.BLUE_800
        toggle_stats_btn.update()
        view_container.update()

    toggle_stats_btn.on_click = toggle_statistics

    floating_action_layout = ft.Row(
        [ft.Column([toggle_stats_btn], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END)],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.MainAxisAlignment.END,
        expand=True
    )

    def load_data():
        if session.get('household') is None:
            return

        household_id = session.get('household').get('id')
        response = (
            supabase.table("ratios")
            .select("*")
            .eq("household_id", household_id)
            .execute()
        )
        data = response.data

        stat_bars_column.controls = [
            stat_row(item["item_name"], item["ratio"])
            for item in data
            if item["ratio"] is not None
        ]

        pie_canvas_container.content = build_pie_canvas(data)

        legend_column.controls = [
            ft.Row([
                ft.Container(width=14, height=14, bgcolor=PIE_COLORS[i % len(PIE_COLORS)], border_radius=3),
                ft.Text(f"{item['item_name']} – {int(item['portion'] * 100)}%", size=13),
            ], spacing=8)
            for i, item in enumerate(data)
        ]

        stat_bars_column.update()
        if showing_pie:
            pie_canvas_container.update()
            legend_column.update()

    content = ft.Column(
        [
            header,
            ft.Container(
                content=floating_action_layout,
                padding=ft.Padding(top=0, bottom=20, left=0, right=20),
                height=100
            ),
            view_container,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    return content, load_data
