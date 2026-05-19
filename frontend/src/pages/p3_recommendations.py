import flet as ft
from components.custom_card import show_ask_card, show_alert_card, show_tip_card
from components.reuseable_ui_elements import show_header

def RecommendationPage():

    header = show_header(
        title="Recommendations",
        subtitle="Smart alerts based on usage algorithm:"
    )

    # TODO: Need to fetch this from database
    recommendations_data = [
        ("banana", "Did you recently buy banana and forgot to log it?", "ask"),
        ("bread", "There is a high risk that you have some bread that will go bad. If so, eat or donate.", "alert"),
        ("apple", "Why not to eat some apple?", "tip"),
        ("milk", "Did you recently buy milk and forgot to log it?", "ask"),
        ("spinach", "There is a high risk that you have some spinach that will go bad. If so, eat or donate.", "alert"),
        ("yogurt", "Why not to eat some yogurt?", "tip"),
        ("egg", "Did you recently buy egg and forgot to log it?", "ask"),
        ("chicken", "There is a high risk that you have some chicken that will go bad. If so, eat or donate.", "alert"),
        ("avocado", "Why not to eat some avocado?", "tip"),
        ("cheese", "Did you recently buy cheese and forgot to log it?", "ask"),
        ("tomato", "There is a high risk that you have some tomato that will go bad. If so, eat or donate.", "alert"),
        ("lemon", "Why not to eat some lemon?", "tip"),
        ("potato", "Did you recently buy potato and forgot to log it?", "ask"),
        ("beef", "There is a high risk that you have some beef that will go bad. If so, eat or donate.", "alert"),
        ("orange", "Why not to eat some orange?", "tip"),
    ]

    card_elements = []

    for item, recommendation, card_type in recommendations_data:
        
        if card_type == "ask":
            card = show_ask_card(item=item, subtitle=recommendation)
            
        elif card_type == "alert":
            card = show_alert_card(item=item, subtitle=recommendation)
            
        elif card_type == "tip":
            card = show_tip_card(item=item, subtitle=recommendation)
            
        else:
            print(f"Unknown card type for item {item}: {card_type}")

        card_elements.append(card)

    
    contents = ft.Column(
        [
            header,
            
            ft.Column(
                controls=card_elements,
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    return contents