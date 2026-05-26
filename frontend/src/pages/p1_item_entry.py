import flet as ft
from components.reuseable_ui_elements import show_header, show_big_round_button
from api.supabase_db import log_purchased_items, log_discarded_item, mark_household_modified
from database import log_purchased_item_local, log_discarded_item_local

def LogFoodPage(session, page: ft.Page):

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    header = show_header(
        title="Log Food",
        subtitle="Keep track of your pantry items and reduce waste!"
    )

    dscrd_btn = show_big_round_button(ft.Icons.DELETE_OUTLINE, ft.Colors.RED_700)
    dscrd_btn.on_click = lambda _: open_log_dialog(False)

    log_prchs_btn = show_big_round_button(ft.Icons.ADD_SHOPPING_CART, ft.Colors.BLUE_800)

    # Opens camera on click
    by_pht_btn = show_big_round_button(ft.Icons.PHOTO_CAMERA, ft.Colors.BLUE_800)
    by_pht_btn.on_click = lambda _: page.run_task(pick_file_task, file_type='image')

    # Opens selection for a file
    by_img_btn = show_big_round_button(ft.Icons.IMAGE, ft.Colors.BLUE_800)
    by_img_btn.on_click = lambda _: page.run_task(
        pick_file_task,
        file_type='custom',
        allowed_extensions=['pdf', 'png', 'jpg', 'jpeg']
    )

    by_key_btn = show_big_round_button(ft.Icons.KEYBOARD, ft.Colors.BLUE_800)
    by_key_btn.on_click = lambda _: open_log_dialog(True)

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

    async def pick_file_task(file_type='any', allowed_extensions=None):

        result = await file_picker.pick_files(
            allow_multiple=False,
            file_type=file_type,
            allowed_extensions=allowed_extensions
        )

        if result:

            page.snack_bar = ft.SnackBar(ft.Text(f"File '{result[0].name}' selected. Starting OCR..."))
            page.snack_bar.open = True
            page.update()


    # Manual Logging Logic
    def handle_log(item_name, quantity, is_purchase):

        try:

            access_token = session.get('access_token')
            user_id = session.get('user').get('id')
            household_id = session.get('household').get('id')

            if is_purchase:

                log_purchased_items(access_token, household_id, item_name, quantity)
                log_purchased_item_local(user_id, household_id, item_name, quantity)

            else:

                log_discarded_item(access_token, household_id, item_name, quantity)
                log_discarded_item_local(user_id, household_id, item_name, quantity)

            mark_household_modified(access_token, household_id)
            page.snack_bar = ft.SnackBar(ft.Text(f'Logged {item_name}!'))
            page.snack_bar.open = True
            page.update()

        except Exception as e:

            print(f'Error logging item: {e}')

    def open_log_dialog(is_purchased):

        name_input = ft.TextField(label='Item Name')
        qty_input = ft.TextField(label='Quantity', value="1", keyboard_type=ft.KeyboardType.NUMBER)

        def on_submit(e):

            if name_input.value:

                handle_log(name_input.value, float(qty_input.value), is_purchased)
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            title = ft.Text('Log Purchase' if is_purchased else 'Log Discard'),
            content = ft.Column([name_input, qty_input], tight=True),
            actions = [
                ft.TextButton('Cancel', on_click=lambda _: setattr(dialog, 'open', False) or page.update()),
                ft.TextButton('Log', on_click=on_submit)
            ]
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    return content
