import flet as ft
import time

from api.supabase_db import (
    get_item_intelligence_weight,
    get_recommendations,
    update_recommendation_feedback,
    upsert_item_intelligence_weight,
)
from components.custom_card import show_alert_card, show_ask_card, show_tip_card
from components.reuseable_ui_elements import show_header


def RecommendationPage(session, page: ft.Page):
    access_token = session.get("access_token") if session else None
    household = session.get("household") if session else None
    household_id = household.get("id") if household else None
    is_refreshing = False
    last_pull_refresh_at = 0.0

    header = show_header(
        title="Recommendations",
        subtitle="Adaptive suggestions based on your household waste patterns.",
    )

    card_container = ft.Column(
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
    pull_refresh_indicator = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.REFRESH, size=18, color=ft.Colors.BLUE_800),
                ft.Text("Refreshing", size=12, color=ft.Colors.BLUE_800, weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
        height=32,
        visible=False,
    )

    def show_message(message: str, color=ft.Colors.GREY_500):
        card_container.controls.clear()
        card_container.controls.append(ft.Text(message, color=color, text_align=ft.TextAlign.CENTER))
        page.update()

    def adapt_item_weight(item_name: str, card_type: str, was_positive: bool):
        current_weight = get_item_intelligence_weight(access_token, household_id, item_name)
        positive_delta = {
            "ask": -0.05,
            "tip": 0.05,
            "alert": -0.25,
        }.get(card_type, 0.0)
        negative_delta = {
            "ask": -0.2,
            "tip": -0.3,
            "alert": -0.45,
        }.get(card_type, -0.25)
        delta = positive_delta if was_positive else negative_delta
        new_weight = min(max(current_weight + delta, 0.1), 3.0)
        upsert_item_intelligence_weight(access_token, household_id, item_name, new_weight)

    def handle_user_feedback(card_id: str, item_name: str, card_type: str, was_positive: bool):
        if not access_token or not household_id:
            return

        try:
            target_card = next(
                (
                    control
                    for control in card_container.controls
                    if getattr(control, "key", None) == f"container_{card_id}"
                ),
                None,
            )

            if target_card:
                target_card.opacity = 0.0
                target_card.scale = 0.96
                page.update()
                time.sleep(0.22)

            adapt_item_weight(item_name, card_type, was_positive)
            update_recommendation_feedback(access_token, card_id, was_positive)

            page.snack_bar = ft.SnackBar(
                ft.Text(f"Recommendation feedback saved for {item_name}.")
            )
            page.snack_bar.open = True
            render_cards_from_supabase()
        except Exception as e:
            print(f"Feedback loop error: {e}")
            page.snack_bar = ft.SnackBar(
                ft.Text("Could not save recommendation feedback.")
            )
            page.snack_bar.open = True
            page.update()

    def render_cards_from_supabase(e=None):
        card_container.controls.clear()
        card_container.controls.append(ft.ProgressRing(width=24, height=24))
        page.update()

        if not access_token or not household_id:
            show_message("Log in to view recommendations.")
            return

        try:
            recommendations_data = get_recommendations(access_token, household_id)
            card_container.controls.clear()

            if not recommendations_data:
                show_message("No active recommendations yet. Log purchases and discarded food to run the adaptive loop.")
                return

            for row in recommendations_data:
                card_id = row["id"]
                item = row["item_name"]
                subtitle = row["subtitle"]
                card_type = row["type"]

                if card_type == "ask":
                    card = show_ask_card(card_id, item, subtitle, handle_user_feedback)
                elif card_type == "alert":
                    card = show_alert_card(card_id, item, subtitle, handle_user_feedback)
                else:
                    card = show_tip_card(card_id, item, subtitle, handle_user_feedback)

                card_container.controls.append(card)

            page.update()
        except Exception as e:
            print(f"Error rendering remote cards: {e}")
            show_message("Failed to sync recommendations from Supabase.", ft.Colors.RED_400)

    def handle_pull_to_refresh(e):
        nonlocal is_refreshing, last_pull_refresh_at

        if is_refreshing:
            return

        overscroll = abs(e.overscroll or 0)
        at_top = e.pixels <= e.min_scroll_extent + 1
        now = time.monotonic()

        if at_top and overscroll > 70 and now - last_pull_refresh_at > 1.5:
            is_refreshing = True
            last_pull_refresh_at = now
            pull_refresh_indicator.visible = True
            page.update()
            render_cards_from_supabase()
            pull_refresh_indicator.visible = False
            is_refreshing = False
            page.update()

    render_cards_from_supabase()

    return ft.Column(
        [
            header,
            pull_refresh_indicator,
            card_container,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        on_scroll=handle_pull_to_refresh,
        expand=True,
    )
