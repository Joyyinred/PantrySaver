import uuid

import algorithm
from db import supabase


FALLBACK_TEMPLATES = {
    "ask": [
        {"id": None, "template_text": "Did you forget to log a recent !ITEM! purchase?"},
        {"id": None, "template_text": "Is the !ITEM! discard correct, or is there missing purchase data?"},
    ],
    "alert": [
        {"id": None, "template_text": "!ITEM! looks high-risk now. Use it, freeze it, or donate it soon."},
        {"id": None, "template_text": "Your household pattern suggests !ITEM! may become waste soon."},
    ],
    "tip": [
        {"id": None, "template_text": "Plan one meal around !ITEM! before the next grocery trip."},
        {"id": None, "template_text": "Move !ITEM! to the front of the fridge so it gets used first."},
    ],
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
        print(f"could not fetch modified households (worker.get_modified_households): {e}")
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
        print(f"could not fetch purchased and discarded items (worker.get_items): {e}")
        return [], []


def get_item_weights(household_id: str) -> dict[str, float]:
    try:
        response = (
            supabase.table("item_intelligence")
            .select("item_name,item_weight")
            .eq("household_id", household_id)
            .execute()
        )
        return {
            row["item_name"]: float(row.get("item_weight") or 1.0)
            for row in response.data
        }
    except Exception as e:
        print(f"could not fetch item weights (worker.get_item_weights): {e}")
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
            print("recommendation template table is empty; using fallback templates")
            return FALLBACK_TEMPLATES

        return templates
    except Exception as e:
        print(f"could not fetch recommendation templates (worker.get_recommendation_templates): {e}")
        return FALLBACK_TEMPLATES


def choose_template(templates: dict[str, list[dict]], card_type: str, item_name: str) -> dict:
    candidates = templates.get(card_type) or FALLBACK_TEMPLATES[card_type]
    stable_index = sum(ord(char) for char in item_name) % len(candidates)
    return candidates[stable_index]


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
        print(f"could not deactivate old recommendations (worker.deactivate_current_recommendations): {e}")


def save_recommendations(household_id: str, plans: list[algorithm.RecommendationPlan], templates: dict):
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
            print(f"no database template found for {plan.card_type}; skipping {plan.item_name}")
            continue

        template = choose_template(templates, plan.card_type, plan.item_name)
        rows.append(
            {
                "id": str(uuid.uuid4()),
                "household_id": household_id,
                "template_id": template.get("id"),
                "item_name": plan.item_name,
                "type": plan.card_type,
                "subtitle": algorithm.render_template(template["template_text"], plan.item_name),
                "score": float(plan.score),
                "is_active": True,
            }
        )
        print(
            f"using {template.get('source', 'fallback')} template "
            f"{template.get('id')} for {plan.card_type}/{plan.item_name}"
        )

    if not rows:
        return 0

    try:
        deactivate_current_recommendations(household_id)
        supabase.table("recommendations").insert(rows).execute()
        return len(rows)
    except Exception as e:
        print(f"could not save recommendations (worker.save_recommendations): {e}")
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
    item_ratios = algorithm.calculate_ratios(household_id, purchased, discarded)
    item_weights = get_item_weights(household_id)
    unique_items = {
        item["item_name"]
        for item in purchased + discarded
        if item.get("item_name")
    }
    plans = []

    for item_name in unique_items:
        specific_purchases = [
            item for item in purchased if item.get("item_name") == item_name
        ]
        specific_discards = [
            item for item in discarded if item.get("item_name") == item_name
        ]
        ratio = item_ratios.get(item_name, 0.0)
        weight = item_weights.get(item_name, 1.0)

        plan = algorithm.plan_recommendation(
            item_name=item_name,
            purchased_items=specific_purchases,
            discarded_items=specific_discards,
            ratio=ratio,
            item_weight=weight,
            shortterm_change_in_days=shortterm_change_in_days,
            longterm_change_in_days=longterm_change_in_days,
        )

        if plan:
            plans.append(plan)
            print(
                f"{plan.card_type.upper()} {item_name}: "
                f"score={plan.score:.2f}, ratio={ratio:.1%}, "
                f"weight={weight:.2f}, reason={plan.reason}"
            )

    saved_count = 0
    if plans:
        saved_count = save_recommendations(household_id, plans, templates) or 0
    print(f"saved {saved_count} recommendation(s)")

    try:
        supabase.table("households").update({"modified": False}).eq("id", household_id).execute()
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
        print(f"could not fetch household name (worker.fetch_household_name): {e}")
        return "no household name"
