from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from db import supabase


class ItemStatus(Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


@dataclass
class RecommendationPlan:
    item_name: str
    card_type: str
    score: float
    reason: str
    template_key: str


def parse_logged_at(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_sorted_timestamps(
    items: list,
    key: str = "logged_at",
) -> list[datetime]:
    timestamps = []

    for item in items:
        logged_at = parse_logged_at(item.get(key))
        if logged_at:
            timestamps.append(logged_at)

    return sorted(timestamps)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return min(max(value, minimum), maximum)


def normalize_item_name(item_name: str | None) -> str:
    return (item_name or "").strip().lower()


def evaluate_item_status(
    purchased_items: list,
    discarded_items: list,
    shortterm_change_in_days: int = 30,
    longterm_change_in_days: int = 90,
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

    discard_dates = get_sorted_timestamps(discarded_items)
    if discard_dates:
        days_since_waste = (now - discard_dates[-1]).days

        if days_since_waste >= longterm_change_in_days:
            status = ItemStatus.green
        elif (
            days_since_waste >= shortterm_change_in_days
            and status == ItemStatus.red
        ):
            status = ItemStatus.yellow

    return status, was_logged_as_purchased


def calculate_ratios(
    household_id: str,
    purchased: list,
    discarded: list,
) -> dict[str, float]:
    calculated_ratios = {}
    discarded_unique = {
        normalize_item_name(d.get("item_name"))
        for d in discarded
        if normalize_item_name(d.get("item_name"))
    }
    total_discarded = sum(
        float(item.get("quantity_discarded") or 0)
        for item in discarded
    )

    for name in discarded_unique:
        purchased_quantity = sum(
            float(item.get("quantity") or 0)
            for item in purchased
            if normalize_item_name(item.get("item_name")) == name
        )
        discarded_quantity = sum(
            float(item.get("quantity_discarded") or 0)
            for item in discarded
            if normalize_item_name(item.get("item_name")) == name
        )
        portion = (
            discarded_quantity / total_discarded
            if total_discarded
            else 0
        )

        if purchased_quantity == 0:
            ratio = None
        else:
            ratio = min(discarded_quantity / purchased_quantity, 1.0)
            calculated_ratios[name] = ratio

        try:
            supabase.table("ratios").upsert(
                {
                    "item_name": name,
                    "household_id": household_id,
                    "ratio": ratio,
                    "portion": portion,
                },
                on_conflict="item_name,household_id",
            ).execute()
        except Exception as e:
            print(f"could not save ratio for {name}: {e}")

    return calculated_ratios


def detect_missing_purchase_log(
    purchased_items: list,
    discarded_items: list,
    recent_purchase_window_days: int = 30,
) -> bool:
    now = datetime.now(timezone.utc)
    purchase_dates = get_sorted_timestamps(purchased_items)
    discard_dates = get_sorted_timestamps(discarded_items)

    if not discard_dates:
        return False

    recent_purchase_dates = [
        purchase_date
        for purchase_date in purchase_dates
        if (now - purchase_date).days <= recent_purchase_window_days
    ]

    return not recent_purchase_dates


def was_never_logged_as_bought(
    purchased_items: list,
    discarded_items: list,
) -> bool:
    return bool(discarded_items) and not purchased_items


def total_quantity(items: list, quantity_key: str) -> float:
    return sum(float(item.get(quantity_key) or 0) for item in items)


def is_fresh_produce_category(category_name: str | None) -> bool:
    if not category_name:
        return False

    normalized = category_name.strip().lower()
    produce_categories = {
        "fruit",
        "fruits",
        "vegetable",
        "vegetables",
        "fresh produce",
        "produce",
    }
    return normalized in produce_categories


def pick_tip_template_key(category_name: str | None) -> str:
    if is_fresh_produce_category(category_name):
        return "use_soon_tip"

    return "nutrition_tip"


def choose_highest_scoring_plan(
    candidates: list[RecommendationPlan],
) -> RecommendationPlan | None:
    if not candidates:
        return None

    type_priority = {
        "alert": 3,
        "ask": 2,
        "tip": 1,
    }
    return max(
        candidates,
        key=lambda plan: (
            plan.score,
            type_priority.get(plan.card_type, 0),
        ),
    )


def plan_recommendation(
    item_name: str,
    purchased_items: list,
    discarded_items: list,
    ratio: float,
    item_weight: float = 1.0,
    category_name: str | None = None,
    shortterm_change_in_days: int = 30,
    longterm_change_in_days: int = 90,
) -> RecommendationPlan | None:
    status, was_logged_as_purchased = evaluate_item_status(
        purchased_items,
        discarded_items,
        shortterm_change_in_days,
        longterm_change_in_days,
    )
    forgot_to_log = detect_missing_purchase_log(
        purchased_items,
        discarded_items,
    )
    never_bought = was_never_logged_as_bought(purchased_items, discarded_items)
    now = datetime.now(timezone.utc)
    discard_dates = get_sorted_timestamps(discarded_items)
    last_discard = discard_dates[-1] if discard_dates else None

    if not discarded_items:
        return None

    recent_waste_risk = (
        clamp(1 - ((now - last_discard).days / 30))
        if last_discard
        else 0.0
    )
    waste_ratio_risk = clamp(ratio or 0)
    discard_frequency_risk = clamp(len(discarded_items) / 3)
    confidence_weight = clamp(item_weight / 3)

    risk_score = (
        waste_ratio_risk * 0.45
        + recent_waste_risk * 0.25
        + discard_frequency_risk * 0.25
        + confidence_weight * 0.05
    )
    adaptive_score = risk_score * max(item_weight, 0.1)
    candidates = []

    if forgot_to_log or never_bought:
        if item_weight >= 0.25:
            reason = (
                "Discard was logged with no purchase history for this item."
                if never_bought
                else (
                    "Discard was logged without a matching recent "
                    "purchase log."
                )
            )
            candidates.append(
                RecommendationPlan(
                    item_name=item_name,
                    card_type="ask",
                    score=min(adaptive_score + 0.75, 5.0),
                    reason=reason,
                    template_key="missing_purchase",
                )
            )

    purchased_quantity = total_quantity(purchased_items, "quantity")
    discarded_quantity = total_quantity(discarded_items, "quantity_discarded")
    if len(purchased_items) >= 2 and purchased_quantity > discarded_quantity:
        if item_weight >= 0.35:
            candidates.append(
                RecommendationPlan(
                    item_name=item_name,
                    card_type="ask",
                    score=min(adaptive_score + 0.6, 5.0),
                    reason=(
                        "Item has been bought more than once and only "
                        "partly discarded."
                    ),
                    template_key="inventory_check",
                )
            )

    if waste_ratio_risk >= 0.75:
        candidates.append(
            RecommendationPlan(
                item_name=item_name,
                card_type="alert",
                score=min(adaptive_score + 1.2, 5.0),
                reason=(
                    "High waste risk from discard history, ratio, and "
                    "missing purchase data."
                ),
                template_key="high_waste_risk",
            )
        )

    if status == ItemStatus.red or risk_score >= 0.7:
        if item_weight >= 0.2 or risk_score >= 0.85:
            candidates.append(
                RecommendationPlan(
                    item_name=item_name,
                    card_type="alert",
                    score=min(adaptive_score + 1.0, 5.0),
                    reason=(
                        "Repeated discard history suggests the item needs "
                        "attention soon."
                    ),
                    template_key="expiration_risk",
                )
            )

    if discarded_items and (
        status == ItemStatus.yellow or was_logged_as_purchased
    ):
        if item_weight >= 0.5:
            template_key = pick_tip_template_key(category_name)
            candidates.append(
                RecommendationPlan(
                    item_name=item_name,
                    card_type="tip",
                    score=min(adaptive_score + 0.45, 5.0),
                    reason=(
                        "Item has been discarded before; a gentle action "
                        "may prevent repeat waste."
                    ),
                    template_key=template_key,
                )
            )

    return choose_highest_scoring_plan(candidates)


def render_template(template_text: str, item_name: str) -> str:
    return (
        template_text
        .replace("!ITEM!", item_name)
        .replace("!item!", item_name)
        .replace("{ITEM}", item_name)
        .replace("{item}", item_name)
    )
