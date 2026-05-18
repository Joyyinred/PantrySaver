from db import supabase
import algorithm


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
        print()
        print(f"could not fetch modified households (worker.get_households): {e}")

        return []


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


def map_items_with_categories():

    try:
        response = (
            supabase.table("item_categories")
            .select("item_name, categories(name)")
            .execute()
        )

        item_categories = {}

        for row in response.data:

            name = row["item_name"]

            cat_name = (
                row["categories"]["name"]
                if isinstance(row["categories"], dict)
                else row["categories"][0]["name"]
            )

            if name not in item_categories:
                item_categories[name] = []
            item_categories[name].append(cat_name)

        return item_categories

    except Exception as e:
        print(f"could not fetch item categories (worker.map_items_with_categories): {e}")
        return {}


def process_household(household_id: str, item_categories: dict):

    print()
    print(f"recommendations for {fetch_household_name(household_id)}")
    purchased, discarded = get_purchased_and_discarded_items(household_id)

    unique_items = set()

    for purchase in purchased:
        unique_items.add(purchase["item_name"])
    for discard in discarded:
        unique_items.add(discard["item_name"])

    for item_name in unique_items:
        specific_purchases = []
        for p in purchased:
            if p["item_name"] == item_name:
                specific_purchases.append(p)

        specific_discards = []
        for d in discarded:
            if d["item_name"] == item_name:
                specific_discards.append(d)

        categories = item_categories.get(item_name, [])

        status, is_in_stock = algorithm.evaluate_item_status(
            specific_purchases,
            specific_discards
            )

        recommendations = algorithm.give_recommendation(
            item_name, status,
            is_in_stock,
            categories
            )

        for recommendation in recommendations:
            print(recommendation)

    # TODO: add logic for changing modified variable in the database
    try:
        supabase.table("households").update({"modified": False}).eq("id", household_id).execute()
    except Exception as e:
        print(f"could not reset modified (woker.process_household): {e}")


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
