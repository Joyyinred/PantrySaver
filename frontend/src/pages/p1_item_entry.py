import tempfile
from pathlib import Path

import flet as ft
from components.reuseable_ui_elements import show_header, show_big_round_button
from api.supabase_db import (
    get_log_entry_suggestions,
    log_discarded_item,
    log_purchased_items,
    mark_household_modified,
)
from database import log_purchased_item_local, log_discarded_item_local
from receipt_scanner import scan_receipt_or_list_file

def LogFoodPage(session, page: ft.Page):

    file_picker = getattr(page, "_pantry_file_picker", None)
    if file_picker is None:
        file_picker = ft.FilePicker()
        page._pantry_file_picker = file_picker
        session["_file_picker"] = file_picker

    header = show_header(
        title="Log Food",
        subtitle="Keep track of your pantry items and reduce waste!"
    )

    dscrd_btn = show_big_round_button(ft.Icons.DELETE_OUTLINE, ft.Colors.RED_700)
    dscrd_btn.on_click = lambda _: open_log_dialog(False)

    log_prchs_btn = show_big_round_button(ft.Icons.ADD_SHOPPING_CART, ft.Colors.BLUE_800)

    # Opens camera on click
    by_pht_btn = show_big_round_button(ft.Icons.PHOTO_CAMERA, ft.Colors.BLUE_800)
    by_pht_btn.on_click = lambda _: start_file_pick(ft.FilePickerFileType.IMAGE)

    # Opens selection for a file
    by_img_btn = show_big_round_button(ft.Icons.IMAGE, ft.Colors.BLUE_800)
    by_img_btn.on_click = lambda _: start_file_pick(
        file_type=ft.FilePickerFileType.CUSTOM,
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

    def start_file_pick(file_type=ft.FilePickerFileType.ANY, allowed_extensions=None):
        try:
            page.run_task(
                pick_file_task,
                file_type=file_type,
                allowed_extensions=allowed_extensions,
            )
        except Exception as e:
            print(f"Could not start file picker task: {e}")
            page.snack_bar = ft.SnackBar(ft.Text("Could not open the file picker."))
            page.snack_bar.open = True
            page.update()

    async def pick_file_task(file_type=ft.FilePickerFileType.ANY, allowed_extensions=None):
        try:
            page.snack_bar = ft.SnackBar(ft.Text("Opening file picker..."))
            page.snack_bar.open = True
            page.update()

            result = await file_picker.pick_files(
                allow_multiple=False,
                file_type=file_type,
                allowed_extensions=allowed_extensions,
                with_data=True,
            )
        except Exception as e:
            print(f"File picker error: {e}")
            page.snack_bar = ft.SnackBar(ft.Text("File picking is not available in this runtime."))
            page.snack_bar.open = True
            page.update()
            return

        if result:
            selected_file = result[0]
            page.snack_bar = ft.SnackBar(ft.Text(f"File '{selected_file.name}' selected. Starting OCR..."))
            page.snack_bar.open = True
            page.update()

            selected_path = selected_file.path
            selected_bytes = getattr(selected_file, "bytes", None)
            path_is_readable = bool(selected_path and Path(selected_path).exists())

            if not path_is_readable and selected_bytes:
                suffix = Path(selected_file.name).suffix or ".receipt"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(selected_bytes)
                    selected_path = temp_file.name
                    path_is_readable = True

            if not path_is_readable:
                print(
                    "Receipt file is not readable by the Python app: "
                    f"path={selected_file.path}, has_bytes={bool(selected_bytes)}"
                )
                page.snack_bar = ft.SnackBar(
                    ft.Text("The selected file was not readable for OCR. Try running from the Mac web app or choose an image.")
                )
                page.snack_bar.open = True
                page.update()
                return

            try:
                _, receipt_items = scan_receipt_or_list_file(selected_path)
            except Exception as e:
                print(f"Receipt scan failed: {e}")
                page.snack_bar = ft.SnackBar(ft.Text("Could not scan the receipt on this device."))
                page.snack_bar.open = True
                page.update()
                return

            if not receipt_items:
                page.snack_bar = ft.SnackBar(ft.Text("No receipt items were found. Try a clearer PDF or image."))
                page.snack_bar.open = True
                page.update()
                return

            open_receipt_review_dialog(receipt_items)


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

    def handle_bulk_purchase_log(items):
        try:
            access_token = session.get('access_token')
            user_id = session.get('user').get('id')
            household_id = session.get('household').get('id')

            for item in items:
                item_name = item["item_name"]
                quantity = item["quantity"]
                log_purchased_items(access_token, household_id, item_name, quantity)
                log_purchased_item_local(user_id, household_id, item_name, quantity)

            mark_household_modified(access_token, household_id)
            page.snack_bar = ft.SnackBar(ft.Text(f"Logged {len(items)} receipt items."))
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            print(f"Error bulk logging receipt items: {e}")
            page.snack_bar = ft.SnackBar(ft.Text("Could not save receipt items."))
            page.snack_bar.open = True
            page.update()

    def open_receipt_review_dialog(receipt_items):
        row_controls = []
        rows_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)

        def add_editable_row(item_name="", quantity=1):
            field_border_color = ft.Colors.BLUE_GREY_100
            name_input = ft.TextField(
                label="Item",
                value=item_name,
                dense=True,
                expand=True,
                border_color=field_border_color,
                focused_border_color=ft.Colors.BLUE_300,
            )
            qty_input = ft.TextField(
                label="Pcs",
                value=str(int(quantity) if float(quantity).is_integer() else quantity),
                width=56,
                dense=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=field_border_color,
                focused_border_color=ft.Colors.BLUE_300,
            )
            row_container = ft.Container()

            def remove_row(_):
                row_container.visible = False
                page.update()

            row_container.content = ft.Row(
                [
                    name_input,
                    qty_input,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_700,
                        icon_size=20,
                        tooltip="Remove row",
                        on_click=remove_row,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            row_container.padding = ft.Padding(top=4, bottom=6, left=0, right=0)
            rows_column.controls.append(row_container)
            row_controls.append(
                {
                    "container": row_container,
                    "name_input": name_input,
                    "qty_input": qty_input,
                }
            )
            if dialog.open:
                page.update()

        def add_blank_row(_=None):
            add_editable_row("", 1)

        def save_rows(_=None):
            items_to_save = []

            for row in row_controls:
                if not row["container"].visible:
                    continue

                item_name = (row["name_input"].value or "").strip()
                if not item_name:
                    continue

                try:
                    quantity = float((row["qty_input"].value or "1").replace(",", "."))
                except ValueError:
                    quantity = 1.0

                if quantity <= 0:
                    continue

                items_to_save.append({"item_name": item_name, "quantity": quantity})

            if not items_to_save:
                page.snack_bar = ft.SnackBar(ft.Text("No receipt items to save."))
                page.snack_bar.open = True
                page.update()
                return

            dialog.open = False
            page.update()
            handle_bulk_purchase_log(items_to_save)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Review receipt items"),
            content=ft.Container(
                width=360,
                height=430,
                content=ft.Column(
                    [
                        ft.Text(
                            "Edit names and quantities before saving.",
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        rows_column,
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            actions=[
                ft.TextButton("Add row", on_click=add_blank_row),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or page.update()),
                ft.TextButton("Save all", on_click=save_rows),
            ],
        )

        for item in receipt_items:
            add_editable_row(item["item_name"], item["quantity"])

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_log_dialog(is_purchased):

        field_border_color = ft.Colors.BLUE_GREY_100
        name_input = ft.TextField(
            label='Item Name',
            border_color=field_border_color,
            focused_border_color=ft.Colors.BLUE_300,
        )
        qty_input = ft.TextField(
            label='Quantity',
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=field_border_color,
            focused_border_color=ft.Colors.BLUE_300,
        )
        item_suggestions = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        quantity_suggestions = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def format_quantity(value):
            return str(int(value)) if float(value).is_integer() else str(value)

        def suggestion_button(label, on_click):
            return ft.OutlinedButton(
                content=ft.Text(
                    label,
                    size=12,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                height=34,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_800,
                    side=ft.BorderSide(1, ft.Colors.BLUE_200),
                    shape=ft.RoundedRectangleBorder(radius=18),
                ),
                on_click=on_click,
            )

        def suggestion_section(title, values, on_select):
            if not values:
                return None

            return ft.Column(
                [
                    ft.Text(title, size=12, color=ft.Colors.BLUE_GREY_500),
                    ft.Row(
                        [
                            suggestion_button(str(value), lambda _, selected=value: on_select(selected))
                            for value in values
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        wrap=True,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        def set_quantity_suggestions(selected_item=None):
            access_token = session.get('access_token')
            household_id = session.get('household').get('id') if session.get('household') else None

            if not access_token or not household_id:
                return

            suggestions = get_log_entry_suggestions(
                access_token,
                household_id,
                is_purchase=is_purchased,
                item_name=selected_item,
            )
            quantity_suggestions.controls.clear()

            recent_section = suggestion_section(
                "Last amount",
                [format_quantity(value) for value in suggestions["recent_quantities"]],
                lambda value: setattr(qty_input, "value", str(value)) or page.update(),
            )
            popular_section = suggestion_section(
                "Popular amounts",
                [format_quantity(value) for value in suggestions["popular_quantities"]],
                lambda value: setattr(qty_input, "value", str(value)) or page.update(),
            )

            for section in [recent_section, popular_section]:
                if section:
                    quantity_suggestions.controls.append(section)

        def set_item_suggestions():
            access_token = session.get('access_token')
            household_id = session.get('household').get('id') if session.get('household') else None

            if not access_token or not household_id:
                return

            suggestions = get_log_entry_suggestions(
                access_token,
                household_id,
                is_purchase=is_purchased,
            )

            def choose_item(value):
                name_input.value = value
                set_quantity_suggestions(value)
                page.update()

            item_suggestions.controls.clear()
            recent_section = suggestion_section("Recent items", suggestions["recent_items"], choose_item)
            popular_section = suggestion_section("Popular items", suggestions["popular_items"], choose_item)

            for section in [recent_section, popular_section]:
                if section:
                    item_suggestions.controls.append(section)

            set_quantity_suggestions()

        set_item_suggestions()

        def on_submit(e):

            if name_input.value:

                handle_log(name_input.value, float(qty_input.value), is_purchased)
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            title = ft.Text('Log Purchase' if is_purchased else 'Log Discard'),
            content = ft.Container(
                width=360,
                content=ft.Column(
                    [
                        name_input,
                        item_suggestions,
                        qty_input,
                        quantity_suggestions,
                    ],
                    tight=True,
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            actions = [
                ft.TextButton('Cancel', on_click=lambda _: setattr(dialog, 'open', False) or page.update()),
                ft.TextButton('Log', on_click=on_submit)
            ]
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    return content
