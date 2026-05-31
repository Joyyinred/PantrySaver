import re

import flet as ft


def format_item_name(item_name: str) -> str:
    item = (item_name or "item").strip()
    return item[:1].upper() + item[1:] if item else "Item"


def recommendation_title(card_type: str, item_name: str) -> str:
    item_title = format_item_name(item_name)

    if card_type == "ask":
        return f"Question about {item_title}"

    if card_type == "alert":
        return f"Alert for {item_title}"

    return f"Tip on {item_title}"


def highlighted_item_text(
    text: str,
    item_name: str,
    highlight_color: str,
    base_weight=None,
    text_color=ft.Colors.BLUE_GREY_900,
):
    item = (item_name or "").strip()
    text = text or ""

    if not item:
        return ft.Text(text, weight=base_weight, color=text_color)

    matches = list(re.finditer(re.escape(item), text, flags=re.IGNORECASE))
    if not matches:
        return ft.Text(text, weight=base_weight, color=text_color)

    spans = []
    current_index = 0
    highlight_style = ft.TextStyle(
        color=highlight_color,
        weight=ft.FontWeight.BOLD,
    )

    for match in matches:
        if match.start() > current_index:
            spans.append(
                ft.TextSpan(
                    text[current_index:match.start()],
                    style=ft.TextStyle(color=text_color),
                )
            )

        spans.append(ft.TextSpan(match.group(0), style=highlight_style))
        current_index = match.end()

    if current_index < len(text):
        spans.append(
            ft.TextSpan(
                text[current_index:],
                style=ft.TextStyle(color=text_color),
            )
        )

    return ft.Text(spans=spans, weight=base_weight, color=text_color)


def infer_feedback_labels(card_type: str, subtitle: str) -> tuple[str, str]:
    text = (subtitle or "").lower()

    if card_type == "ask":
        if "forgot" in text or "forget" in text or "log" in text:
            return "Bought", "No"
        if "still" in text and "inventory" in text:
            return "I do", "Gone"
        return "Yes", "No"

    if "donate" in text:
        return "Done", "Later"

    if "process" in text:
        return "Done", "Later"

    if "adding" in text or "add " in text:
        return "Add", "Skip"

    if "salad" in text or "meal" in text:
        return "Try", "Skip"

    if "use" in text or "eat" in text:
        return "Use", "Skip"

    if card_type == "alert":
        return "Done", "Skip"

    if card_type == "tip":
        return "Try", "Skip"

    return "Good", "Skip"


def feedback_button_text(label: str):
    return ft.Text(
        label,
        size=11,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
        text_align=ft.TextAlign.CENTER,
    )


def show_recommendation_card(
    card_id: str,
    title: str,
    subtitle: str,
    item_name: str,
    icon: str,
    icon_color: str,
    bg_color: str,
    action_buttons: list
):
    button_container = ft.Column(
        controls=action_buttons,
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    card_content = ft.Row(
        [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(icon, color=icon_color, size=30),
                    title=highlighted_item_text(
                        title,
                        item_name,
                        icon_color,
                        base_weight=ft.FontWeight.BOLD,
                        text_color=ft.Colors.BLUE_GREY_900,
                    ),
                    subtitle=highlighted_item_text(
                        subtitle,
                        item_name,
                        icon_color,
                        text_color=ft.Colors.BLUE_GREY_800,
                    ),
                ),
                expand=True,
                padding=ft.Padding(top=5, bottom=5, left=0, right=0)
            ),

            ft.Container(
                content=button_container,
                padding=ft.Padding(top=10, bottom=10, left=0, right=10),
                alignment=ft.Alignment(0, 0)
            )
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.Container(
        key=f"container_{card_id}",
        content=ft.Card(
            content=ft.Container(
                content=card_content,
                width=380,
                padding=5,
                bgcolor=bg_color,
                border_radius=12
            )
        ),
        width=380,
        height=None,
        opacity=1.0,
        scale=1.0,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,

        animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN_BACK),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

def format_recommendation(item_name: str, template_text: str, card_type: str):
    body = template_text.replace("!ITEM!", item_name)
    return recommendation_title(card_type, item_name), body

def show_ask_card(card_id: str, item: str, subtitle: str, on_feedback):
    positive_label, negative_label = infer_feedback_labels("ask", subtitle)
    buttons = [
        ft.FilledButton(
            content=feedback_button_text(positive_label),
            width=96, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE),
            on_click=lambda _: on_feedback(card_id, item, "ask", True)
        ),
        ft.OutlinedButton(
            content=feedback_button_text(negative_label),
            width=96, height=36,
            on_click=lambda _: on_feedback(card_id, item, "ask", False)
        )
    ]
    return show_recommendation_card(
        card_id=card_id,
        title=recommendation_title("ask", item),
        subtitle=subtitle,
        item_name=item,
        icon=ft.Icons.HELP_OUTLINE,
        icon_color=ft.Colors.BLUE_800,
        bg_color="#EBF8FF",
        action_buttons=buttons
    )


def show_alert_card(card_id: str, item: str, subtitle: str, on_feedback):
    positive_label, negative_label = infer_feedback_labels("alert", subtitle)
    buttons = [
        ft.FilledButton(
            content=feedback_button_text(positive_label),
            width=96, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
            on_click=lambda _: on_feedback(card_id, item, "alert", True)
        ),
        ft.OutlinedButton(
            content=feedback_button_text(negative_label),
            width=96, height=36,
            on_click=lambda _: on_feedback(card_id, item, "alert", False)
        )
    ]
    return show_recommendation_card(
        card_id=card_id,
        title=recommendation_title("alert", item),
        subtitle=subtitle,
        item_name=item,
        icon=ft.Icons.WARNING_AMBER_ROUNDED,
        icon_color=ft.Colors.RED_700,
        bg_color="#FFF5F5",
        action_buttons=buttons
    )


def show_tip_card(card_id: str, item: str, subtitle: str, on_feedback):
    positive_label, negative_label = infer_feedback_labels("tip", subtitle)
    buttons = [
        ft.FilledButton(
            content=feedback_button_text(positive_label),
            width=96, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE),
            on_click=lambda _: on_feedback(card_id, item, "tip", True)
        ),
        ft.OutlinedButton(
            content=feedback_button_text(negative_label),
            width=96, height=36,
            on_click=lambda _: on_feedback(card_id, item, "tip", False)
        )
    ]
    return show_recommendation_card(
        card_id=card_id,
        title=recommendation_title("tip", item),
        subtitle=subtitle,
        item_name=item,
        icon=ft.Icons.LIGHTBULB_OUTLINE,
        icon_color=ft.Colors.AMBER_800,
        bg_color="#FFFDF0",
        action_buttons=buttons
    )
