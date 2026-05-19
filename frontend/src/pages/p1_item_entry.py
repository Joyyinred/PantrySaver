import flet as ft
from components.reuseable_ui_elements import show_header, show_big_round_button

def LogFoodPage():
    
    header = show_header(
        title="Log Food",
        subtitle="Keep track of your pantry items and reduce waste!"
    )

    dscrd_btn = show_big_round_button(ft.Icons.DELETE_OUTLINE, ft.Colors.RED_700)
    log_prchs_btn = show_big_round_button(ft.Icons.ADD_SHOPPING_CART, ft.Colors.BLUE_800)

    by_pht_btn = show_big_round_button(ft.Icons.PHOTO_CAMERA, ft.Colors.BLUE_800)
    by_img_btn = show_big_round_button(ft.Icons.IMAGE, ft.Colors.BLUE_800)
    by_key_btn = show_big_round_button(ft.Icons.KEYBOARD, ft.Colors.BLUE_800)

    log_popup_row = ft.Row(
        [
            by_pht_btn,
            by_img_btn,
            by_key_btn,
        ],
        spacing=8,
        visible=False
    )

    def toggle_log_options():
        log_popup_row.visible = not log_popup_row.visible
        log_popup_row.update()

        if log_popup_row.visible:
            log_prchs_btn.style.bgcolor = ft.Colors.BLUE_400
        else:
            log_prchs_btn.style.bgcolor = ft.Colors.BLUE_800
        log_prchs_btn.update()

    log_prchs_btn.on_click = toggle_log_options

    add_button_group = ft.Row(
        [
            log_popup_row,
            log_prchs_btn
        ],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    floating_action_layout = ft.Row(
        [
            ft.Column(
                [
                    dscrd_btn,
                    add_button_group
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.END
            )
        ],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.END,
        expand=True
    )

    content = ft.Column(
        [
            header,
            ft.Container(
                content=floating_action_layout,
                padding=ft.Padding(top=0, bottom=20, left=0, right=20),
                expand=True
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        expand=True 
    )

    return content