import uuid
from datetime import datetime, timezone

import algorithm
from db import supabase


template_rules = {
    "missing_purchase": {
        "preferred_ids": [1],
        "keywords": ["recently buy", "forgot", "forget", "log"],
    },
    "inventory_check": {
        "preferred_ids": [2],
        "keywords": ["still in your inventory"],
    },
    "high_waste_risk": {
        "preferred_ids": [3],
        "keywords": ["high risk", "go bad", "eat or donate"],
    },
    "expiration_risk": {
        "preferred_ids": [4],
        "keywords": ["expiration", "exparation", "process"],
    },
    "use_soon_tip": {
        "preferred_ids": [5],
        "keywords": ["fresh salad"],
    },
    "nutrition_tip": {
        "preferred_ids": [6],
        "keywords": ["next meal", "nutrition"],
    },
}


def get_modified_households():
    try:
        response = (
            supabase.table("households")
            .select("id")
            .eq("modified", True)
            .execute()
        )
        return [row["id"] for row in response.data]
    except Exception as e:
        print(
            "could not fetch modified households "
            f"(worker.get_modified_households): {e}"
        )
        return []


def process_modified_households(
    shortterm_change_in_days: int = 30,
    longterm_change_in_days: int = 90,
) -> int:
    modified_households = get_modified_households()

    if not modified_households:
        return 0

    templates = get_recommendation_templates()
    for household_id in modified_households:
        process_household(
            household_id,
            templates,
            shortterm_change_in_days,
            longterm_change_in_days,
        )

    return len(modified_households)


def get_purchased_and_discarded_items(household_id: str):
    try:
        purchased = (
            supabase.table("purchased_items")
            .select("*")
            .eq("household_id", household_id)
            .execute()
        )

        discarded = (
            supabase.table("discarded_items")
            .select("*")
            .eq("household_id", household_id)
            .execute()
        )

        return purchased.data, discarded.data
    except Exception as e:
        print(
            "could not fetch purchased and discarded items "
            f"(worker.get_items): {e}"
        )
        return [], []


def get_item_weights(household_id: str) -> dict[str, float]:
    try:
        response = (
            supabase.table("item_intelligence")
            .select("item_name,item_weight")
            .eq("household_id", household_id)
            .execute()
        )
        weights = {}
        for row in response.data:
            item_name = row.get("item_name")
            if not item_name:
                continue

            item_weight = float(row.get("item_weight") or 1.0)
            weights[item_name] = item_weight
            weights[algorithm.normalize_item_name(item_name)] = item_weight

        return weights
    except Exception as e:
        print(f"could not fetch item weights (worker.get_item_weights): {e}")
        return {}


def get_weight_for_item(
    item_weights: dict[str, float],
    item_name: str,
) -> float:
    return item_weights.get(
        item_name,
        item_weights.get(algorithm.normalize_item_name(item_name), 1.0),
    )


def parse_responded_at(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def apply_alert_feedback_decay(
    household_id: str,
    item_weights: dict[str, float],
    shortterm_change_in_days: int,
    longterm_change_in_days: int,
) -> dict[str, float]:
    adjusted_weights = item_weights.copy()

    try:
        response = (
            supabase.table("recommendations")
            .select("item_name,responded_at")
            .eq("household_id", household_id)
            .eq("type", "alert")
            .eq("feedback", 0)
            .order("responded_at", desc=True)
            .execute()
        )
    except Exception as e:
        print(
            "could not fetch alert feedback history "
            f"(worker.apply_alert_feedback_decay): {e}"
        )
        return adjusted_weights

    now = datetime.now(timezone.utc)
    seen_items = set()

    for row in response.data or []:
        item_name = (row.get("item_name") or "").strip()
        item_key = item_name.lower()

        if not item_name or item_key in seen_items:
            continue

        responded_at = parse_responded_at(row.get("responded_at"))
        if not responded_at:
            continue

        seen_items.add(item_key)
        days_since_negative_alert = (now - responded_at).days
        current_weight = get_weight_for_item(adjusted_weights, item_name)
        restored_weight = current_weight

        if days_since_negative_alert >= longterm_change_in_days:
            restored_weight = max(current_weight, 1.0)
            print(
                f"reset {item_name} weight to default after old "
                "negative alert feedback"
            )
        elif days_since_negative_alert >= shortterm_change_in_days:
            restored_weight = max(current_weight, 0.6)
            print(
                f"partly restored {item_name} weight after negative "
                "alert feedback cooled down"
            )

        if restored_weight > current_weight:
            adjusted_weights[item_name] = restored_weight
            adjusted_weights[item_key] = restored_weight
            try:
                supabase.table("item_intelligence").upsert(
                    {
                        "household_id": household_id,
                        "item_name": item_name,
                        "item_weight": restored_weight,
                    },
                    on_conflict="household_id,item_name",
                ).execute()
            except Exception as e:
                print(
                    f"could not persist restored weight for {item_name}: "
                    f"{e}"
                )

    return adjusted_weights


def get_item_categories() -> dict[str, str]:
    try:
        category_response = (
            supabase.table("categories")
            .select("id,name")
            .execute()
        )
        category_names = {
            str(row.get("id")): row.get("name")
            for row in category_response.data
            if row.get("id") and row.get("name")
        }

        item_category_response = (
            supabase.table("item_categories")
            .select("item_name,category_id")
            .execute()
        )

        return {
            (row.get("item_name") or "").strip().lower(): category_names.get(
                str(row.get("category_id"))
            )
            for row in item_category_response.data
            if row.get("item_name")
            and category_names.get(str(row.get("category_id")))
        }
    except Exception as e:
        print(
            "could not fetch item categories "
            f"(worker.get_item_categories): {e}"
        )
        return {}


def get_recommendation_templates() -> dict[str, list[dict]]:
    try:
        response = (
            supabase.table("recommendation_templates")
            .select("*")
            .execute()
        )
        templates = {"ask": [], "alert": [], "tip": []}

        for row in response.data:
            card_type = (row.get("type") or "").strip().lower()
            template_text = (
                row.get("template_text")
                or row.get("template")
                or row.get("text")
                or row.get("content")
                or row.get("message")
            )

            if card_type in templates and template_text:
                templates[card_type].append(
                    {
                        "id": row.get("id"),
                        "type": card_type,
                        "template_text": template_text,
                        "source": "database",
                    }
                )

        loaded_count = sum(len(items) for items in templates.values())
        print(
            "loaded recommendation templates from database: "
            f"ask={len(templates['ask'])}, "
            f"tip={len(templates['tip'])}, "
            f"alert={len(templates['alert'])}"
        )

        if loaded_count == 0:
            print(
                "recommendation template table is empty; "
                "no recommendations will be generated"
            )

        return templates
    except Exception as e:
        print(
            "could not fetch recommendation templates "
            f"(worker.get_recommendation_templates): {e}"
        )
        return {"ask": [], "alert": [], "tip": []}


def choose_template(
    templates: dict[str, list[dict]],
    card_type: str,
    item_name: str,
    template_key: str,
) -> dict:
    candidates = templates.get(card_type) or []
    if not candidates:
        return {}

    rule = template_rules.get(template_key, {})

    preferred_ids = {
        str(template_id)
        for template_id in rule.get("preferred_ids", [])
    }
    for candidate in candidates:
        if str(candidate.get("id")) in preferred_ids:
            return candidate

    keywords = rule.get("keywords", [])
    for candidate in candidates:
        template_text = (candidate.get("template_text") or "").lower()
        if any(keyword in template_text for keyword in keywords):
            return candidate

    if rule:
        print(
            f"no matching database template found for {template_key}; "
            f"skipping {item_name}"
        )
        return {}

    stable_index = sum(ord(char) for char in item_name) % len(candidates)
    return candidates[stable_index]


def get_logged_category(items: list) -> str | None:
    for item in items:
        category = (item.get("category") or "").strip()
        if category:
            return category

    return None


def group_logged_items_by_name(
    purchased: list,
    discarded: list,
) -> dict[str, dict]:
    grouped_items = {}

    for item in discarded + purchased:
        item_key = algorithm.normalize_item_name(item.get("item_name"))
        if not item_key:
            continue

        grouped_items.setdefault(
            item_key,
            {
                "display_name": item_key,
                "purchased": [],
                "discarded": [],
            },
        )

        raw_name = (item.get("item_name") or "").strip()
        if raw_name and grouped_items[item_key]["display_name"] == item_key:
            grouped_items[item_key]["display_name"] = raw_name

    for item in purchased:
        item_key = algorithm.normalize_item_name(item.get("item_name"))
        if item_key in grouped_items:
            grouped_items[item_key]["purchased"].append(item)

    for item in discarded:
        item_key = algorithm.normalize_item_name(item.get("item_name"))
        if item_key in grouped_items:
            grouped_items[item_key]["discarded"].append(item)

    return grouped_items


def deactivate_current_recommendations(household_id: str):
    try:
        (
            supabase.table("recommendations")
            .update({"is_active": False})
            .eq("household_id", household_id)
            .eq("is_active", True)
            .execute()
        )
    except Exception as e:
        print(
            "could not deactivate old recommendations "
            f"(worker.deactivate_current_recommendations): {e}"
        )


def save_recommendations(
    household_id: str,
    plans: list[algorithm.RecommendationPlan],
    templates: dict,
):
    rows = []
    seen_cards = set()

    for plan in plans:
        card_key = (plan.item_name.strip().lower(), plan.card_type)
        if card_key in seen_cards:
            print(f"duplicate {plan.card_type}/{plan.item_name}; skipping")
            continue
        seen_cards.add(card_key)

        candidates = templates.get(plan.card_type) or []
        if not candidates:
            print(
                f"no database template found for {plan.card_type}; "
                f"skipping {plan.item_name}"
            )
            continue

        template = choose_template(
            templates,
            plan.card_type,
            plan.item_name,
            plan.template_key,
        )
        if not template:
            continue

        rows.append(
            {
                "id": str(uuid.uuid4()),
                "household_id": household_id,
                "template_id": template.get("id"),
                "item_name": plan.item_name,
                "type": plan.card_type,
                "subtitle": algorithm.render_template(
                    template["template_text"],
                    plan.item_name,
                ),
                "score": float(plan.score),
                "is_active": True,
            }
        )
        print(
            f"using {template.get('source', 'database')} template "
            f"{template.get('id')} for {plan.card_type}/{plan.item_name}"
        )

    if not rows:
        return 0

    try:
        deactivate_current_recommendations(household_id)
        supabase.table("recommendations").insert(rows).execute()
        return len(rows)
    except Exception as e:
        print(
            "could not save recommendations "
            f"(worker.save_recommendations): {e}"
        )
        return 0


def process_household(
    household_id: str,
    templates: dict,
    shortterm_change_in_days: int,
    longterm_change_in_days: int,
):
    print()
    print(f"Recommendations for {fetch_household_name(household_id)}:")
    print()

    purchased, discarded = get_purchased_and_discarded_items(household_id)
    item_ratios = algorithm.calculate_ratios(
        household_id,
        purchased,
        discarded,
    )
    item_weights = apply_alert_feedback_decay(
        household_id=household_id,
        item_weights=get_item_weights(household_id),
        shortterm_change_in_days=shortterm_change_in_days,
        longterm_change_in_days=longterm_change_in_days,
    )
    item_categories = get_item_categories()
    grouped_items = group_logged_items_by_name(purchased, discarded)
    plans = []

    for item_key, item_group in grouped_items.items():
        item_name = item_group["display_name"]
        specific_purchases = item_group["purchased"]
        specific_discards = item_group["discarded"]
        ratio = item_ratios.get(item_key, 0.0)
        weight = get_weight_for_item(item_weights, item_name)
        category_name = (
            item_categories.get(item_key)
            or get_logged_category(specific_purchases + specific_discards)
        )

        print(
            f"checking {item_name}: "
            f"purchased={len(specific_purchases)}, "
            f"discarded={len(specific_discards)}, "
            f"ratio={ratio:.1%}, weight={weight:.2f}, "
            f"category={category_name or 'unknown'}"
        )

        plan = algorithm.plan_recommendation(
            item_name=item_name,
            purchased_items=specific_purchases,
            discarded_items=specific_discards,
            ratio=ratio,
            item_weight=weight,
            category_name=category_name,
            shortterm_change_in_days=shortterm_change_in_days,
            longterm_change_in_days=longterm_change_in_days,
        )

        if plan:
            plans.append(plan)
            print(
                f"{plan.card_type.upper()} {item_name}: "
                f"template={plan.template_key}, "
                f"score={plan.score:.2f}, ratio={ratio:.1%}, "
                f"weight={weight:.2f}, reason={plan.reason}"
            )

    saved_count = 0
    if plans:
        saved_count = save_recommendations(household_id, plans, templates) or 0
    else:
        deactivate_current_recommendations(household_id)

    print(f"saved {saved_count} recommendation(s)")

    try:
        (
            supabase.table("households")
            .update({"modified": False})
            .eq("id", household_id)
            .execute()
        )
    except Exception as e:
        print(f"could not reset modified (worker.process_household): {e}")


def fetch_household_name(household_id: str):
    try:
        response = (
            supabase.table("households")
            .select("name")
            .eq("id", household_id)
            .single()
            .execute()
        )
        return response.data["name"]
    except Exception as e:
        print(
            "could not fetch household name "
            f"(worker.fetch_household_name): {e}"
        )
        return "no household name"
