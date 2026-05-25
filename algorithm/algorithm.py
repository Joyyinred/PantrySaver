from datetime import datetime, timezone
from enum import Enum
from db import supabase


class ItemStatus(Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


def evaluate_item_status(
        purchased_items: list,
        discarded_items: list,
        shortterm_change_in_days: int = 30,
        longterm_change_in_days: int = 90
        ) -> tuple[ItemStatus, bool]:

    now = datetime.now(timezone.utc)
    discard_count = len(discarded_items)
    was_logged_as_purchased = len(purchased_items) > 0

    if discard_count == 0:
        status = ItemStatus.green
    elif discard_count == 1:
        status = ItemStatus.yellow
    else:
        status = ItemStatus.red

    if discarded_items:
        timestamps = []
        for discarded_item in discarded_items:
            dt_str = discarded_item["logged_at"].replace("Z", "+00:00")
            timestamps.append(datetime.fromisoformat(dt_str))

        last_discard_date = max(timestamps)
        days_since_waste = (now - last_discard_date).days

        if days_since_waste >= longterm_change_in_days:
            status = ItemStatus.green
        elif days_since_waste >= shortterm_change_in_days and status == ItemStatus.red:
            status = ItemStatus.yellow

    return status, was_logged_as_purchased


def give_recommendation(
        item_name: str, status: ItemStatus,
        purchased_items: list,
        discarded_items: list,
        categories: list
        ) -> list:

    categories_str = f" [{', '.join(categories)}]" if categories else ""
    messages = [f"Product: {item_name.capitalize()}, categories: {categories_str}, internal label: {status.name}"]

    # a helper for timestamps
    def get_sorted_timestamps(items_list, key="logged_at"):

        timestamps = []

        for item in items_list:
            dt_str = item[key].replace("Z", "+00:00")
            timestamps.append(datetime.fromisoformat(dt_str))

        return sorted(timestamps)

    purchase_dates = get_sorted_timestamps(purchased_items)
    discard_dates = get_sorted_timestamps(discarded_items)

    last_purchase = purchase_dates[-1] if purchase_dates else None
    last_discard = discard_dates[-1] if discard_dates else None
    second_last_discard = discard_dates[-2] if len(discard_dates) >= 2 else None

    was_logged_between_last_two_discards = False
    was_logged_before_only_discard = False

    if last_purchase:

        if last_discard and second_last_discard:

            if second_last_discard < last_purchase < last_discard:
                was_logged_between_last_two_discards = True

        if last_discard and not second_last_discard:

            if last_purchase < last_discard:
                was_logged_before_only_discard = True

    forgot_to_log = False

    if len(discard_dates) >= 2 and not was_logged_between_last_two_discards:
        forgot_to_log = True
    elif len(discard_dates) == 1 and not was_logged_before_only_discard:
        forgot_to_log = True

    if status == ItemStatus.yellow:

        if last_purchase and (not last_discard or last_purchase > last_discard):
            messages.append(f"  Reminder: looks like you bought some {item_name} recently. Let's eat some.")

        if forgot_to_log:
            messages.append(f"  Log question: Did you forget to log purchase of {item_name}?")

        if categories:
            messages.append(f"  Category suggestion: Do you have any product in this category ({', '.join(categories)})? You can eat some.")

    elif status == ItemStatus.red:

        if last_purchase and last_discard and last_purchase > last_discard:
            messages.append(f"  Alert: high chance that you have some {item_name}, please eat.")

        if forgot_to_log:
            messages.append(f"  Log question: Did you forget to log purchase of {item_name}?")

        messages.append(f"  Question: Do you have any of these ({item_name}) at home? can eat or donate.")

    return messages


def calculate_ratios(household_id, purchased, discarded):
    calculated_ratios = {}
    discarded_unique = {d["item_name"] for d in discarded}
    total_discarded = sum(i["quantity_discarded"] for i in discarded)
    for name in discarded_unique:
        purchased_quant = 0
        discarded_quant = 0

        for i in purchased:
            if i["item_name"] == name:
                purchased_quant += i["quantity"]

        for i in discarded:
            if i["item_name"] == name:
                discarded_quant += i["quantity_discarded"]

        if purchased_quant == 0:
            continue

        ratio = discarded_quant / purchased_quant
        if ratio > 1:
            ratio = 1
        calculated_ratios[name] = ratio

        portion = discarded_quant / total_discarded

        supabase.table("ratios").upsert(
            {"item_name": name, "household_id": household_id, "ratio": ratio, "portion":portion},
            on_conflict="item_name,household_id"
        ).execute()

    return calculated_ratios
    

