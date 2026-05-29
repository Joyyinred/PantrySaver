import uuid

import algorithm
from db import supabase


TEMPLATE_RULES = {
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
        "preferred_ids": [5, 6],
        "keywords": ["fresh salad", "next meal", "nutrition"],
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
            print("recommendation template table is empty; no recommendations will be generated")

        return templates
    except Exception as e:
        print(f"could not fetch recommendation templates (worker.get_recommendation_templates): {e}")
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

    rule = TEMPLATE_RULES.get(template_key, {})

    preferred_ids = {str(template_id) for template_id in rule.get("preferred_ids", [])}
    for candidate in candidates:
        if str(candidate.get("id")) in preferred_ids:
            return candidate

    keywords = rule.get("keywords", [])
    for candidate in candidates:
        template_text = (candidate.get("template_text") or "").lower()
        if any(keyword in template_text for keyword in keywords):
            return candidate

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

        template = choose_template(templates, plan.card_type, plan.item_name, plan.template_key)
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

        print(
            f"checking {item_name}: "
            f"purchased={len(specific_purchases)}, "
            f"discarded={len(specific_discards)}, "
            f"ratio={ratio:.1%}, weight={weight:.2f}"
        )

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
    else:
        deactivate_current_recommendations(household_id)

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
