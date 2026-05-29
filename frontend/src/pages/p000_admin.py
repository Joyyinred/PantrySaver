from collections import Counter
from datetime import datetime, timezone

import flet as ft

from components.reuseable_ui_elements import show_big_round_button, show_header
from db import supabase


def build_food_waste_report() -> str:
    discarded_response = supabase.table("discarded_items").select("item_name,quantity_discarded").execute()
    ratios_response = supabase.table("ratios").select("item_name,portion").execute()

    discarded_rows = discarded_response.data or []
    ratio_rows = ratios_response.data or []
    item_totals = Counter()

    for row in discarded_rows:
        item_name = (row.get("item_name") or "Unknown item").strip().lower()
        quantity = float(row.get("quantity_discarded") or 0)
        item_totals[item_name] += quantity

    total_discarded = sum(item_totals.values())
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "Pantry Saver - Anonymised Food Waste Report",
        "=" * 44,
        f"Generated: {generated_at}",
        "",
        "Overall summary",
        "-" * 15,
        f"Discard log entries: {len(discarded_rows)}",
        f"Total quantity discarded: {total_discarded:g}",
        f"Unique discarded item names: {len(item_totals)}",
        "",
        "Discarded quantity by item",
        "-" * 26,
    ]

    if item_totals:
        for item_name, quantity in item_totals.most_common():
            percentage = (quantity / total_discarded * 100) if total_discarded else 0
            lines.append(f"{item_name.title():<24} {quantity:>8g}  {percentage:>5.1f}%")
    else:
        lines.append("No discarded food data found.")

    if ratio_rows:
        ratio_totals = Counter()
        for row in ratio_rows:
            item_name = (row.get("item_name") or "Unknown item").strip().lower()
            ratio_totals[item_name] += float(row.get("portion") or 0)

        lines.extend(["", "Overall waste distribution signal", "-" * 33])
        for item_name, portion in ratio_totals.most_common():
            lines.append(f"{item_name.title():<24} {portion * 100:>6.1f}%")

    lines.extend([
        "",
        "Privacy note",
        "-" * 12,
        "This report is anonymised. It does not include user names, emails, household IDs, or purchase IDs.",
        "",
    ])

    return "\n".join(lines)


def AdminDashboardPage(admin_profile, on_logout, page: ft.Page):
    email = admin_profile.get("email", "Administrator") if admin_profile else "Administrator"
    file_picker = getattr(page, "_pantry_admin_file_picker", None)

    if file_picker is None:
        file_picker = ft.FilePicker()
        page._pantry_admin_file_picker = file_picker

    header = show_header(
        title="Admin Console",
        subtitle="Export anonymised waste reports.",
    )

    status_text = ft.Text("", color=ft.Colors.BLUE_GREY_600, text_align=ft.TextAlign.CENTER)

    async def export_report_task():
        try:
            status_text.value = "Preparing anonymised report..."
            page.update()

            report = build_food_waste_report()
            saved_path = await file_picker.save_file(
                dialog_title="Save anonymised food waste report",
                file_name="pantry_saver_food_waste_report.txt",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt"],
                src_bytes=report.encode("utf-8"),
            )

            status_text.value = "Report saved." if saved_path else "Report export cancelled."
            page.update()
        except Exception as e:
            print(f"Admin report export failed: {e}")
            status_text.value = "Could not export report."
            page.update()

    def export_report(_=None):
        page.run_task(export_report_task)

    logout_btn = show_big_round_button(ft.Icons.LOGOUT, ft.Colors.RED_700)
    logout_btn.tooltip = "Admin logout"
    logout_btn.on_click = on_logout

    report_btn = show_big_round_button(ft.Icons.DESCRIPTION, ft.Colors.BLUE_800)
    report_btn.tooltip = "Print report"
    report_btn.on_click = export_report

    return ft.Column(
        [
            ft.Column(
                [
                    header,
                    ft.Icon(ft.Icons.VERIFIED_USER, size=80, color=ft.Colors.BLUE_800),
                    ft.Text("Signed in as administrator", weight=ft.FontWeight.BOLD, size=20),
                    ft.Text(email, size=14, color=ft.Colors.GREY_600),
                    status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    [logout_btn, report_btn],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
                padding=ft.Padding(top=0, bottom=20, left=0, right=20),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=0,
        expand=True,
    )
