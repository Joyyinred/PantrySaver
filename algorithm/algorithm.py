from datetime import datetime, timezone
from enum import Enum


class ItemStatus(Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


def evaluate_item_status(
        purchased_items: list,
        discarded_items: list
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
        for d in discarded_items:
            dt_str = d["logged_at"].replace("Z", "+00:00")
            timestamps.append(datetime.fromisoformat(dt_str))

        last_discard_date = max(timestamps)
        days_since_waste = (now - last_discard_date).days

        if days_since_waste >= 90:
            status = ItemStatus.green
        elif days_since_waste >= 30 and status == ItemStatus.red:
            status = ItemStatus.yellow

    return status, was_logged_as_purchased


def give_recommendation(
        item_name: str, status: ItemStatus,
        was_logged_as_purchased: bool,
        categories: list
        ) -> list:

    categories = f" [{', '.join(categories)}]" if categories else ""
    messages = [f"Product: {item_name.capitalize()}, categories: {categories}, internal label: {status.name}"]

    if status == ItemStatus.yellow:
        messages.append(f"  Tip: You still have {item_name} left. Try consuming them soon to prevent waste!")

    elif status == ItemStatus.red:
        if was_logged_as_purchased:
            messages.append(f"  Alert: You have {item_name} left! Let's eat some!")
        else:
            messages.append(f"  Log question: Did you buy more {item_name} recently? Keep your tracking log current.")

    return messages
