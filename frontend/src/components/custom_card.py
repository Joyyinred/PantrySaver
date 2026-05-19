import flet as ft


def show_recommendation_card(
    title: str, 
    subtitle: str, 
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
                    title=ft.Text(title, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(subtitle),
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

    return ft.Card(
        content=ft.Container(
            content=card_content,
            width=380, 
            padding=5, 
            bgcolor=bg_color, 
            border_radius=12
        )
    )


def show_ask_card(item: str, subtitle: str):
    buttons = [
        ft.FilledButton(
            content=ft.Text("Yes", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
            width=110, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE)
        ),
        ft.OutlinedButton(
            content=ft.Text("No", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
            width=110, height=36
        )
    ]
    return show_recommendation_card(
        title="Log Reminder", 
        subtitle=subtitle, 
        icon=ft.Icons.HELP_OUTLINE, 
        icon_color=ft.Colors.BLUE_800, 
        bg_color="#EBF8FF", 
        action_buttons=buttons
    )


def show_alert_card(item: str, subtitle: str):
    buttons = [
        ft.FilledButton(
            content=ft.Text("Thanx", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
            width=110, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
        ),
        ft.OutlinedButton(
            content=ft.Text("No", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
            width=110, height=36
        )
    ]
    return show_recommendation_card(
        title=f"Attention: {item.capitalize()}", 
        subtitle=subtitle, 
        icon=ft.Icons.WARNING_AMBER_ROUNDED, 
        icon_color=ft.Colors.RED_700, 
        bg_color="#FFF5F5", 
        action_buttons=buttons
    )
\
def show_tip_card(item: str, subtitle: str):
    buttons = [
        ft.FilledButton(
            content=ft.Text(
                "Useful",
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                text_align=ft.TextAlign.CENTER
                ),

            width=110, height=36,
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE)
        ),

        ft.OutlinedButton(
            content=ft.Text(
                "Nope",
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                text_align=ft.TextAlign.CENTER
                ),

            width=110, height=36
        )
    ]

    return show_recommendation_card(
        title="Smart Tip", 
        subtitle=subtitle, 
        icon=ft.Icons.LIGHTBULB_OUTLINE, 
        icon_color=ft.Colors.AMBER_800, 
        bg_color="#FFFDF0", 
        action_buttons=buttons
    )
