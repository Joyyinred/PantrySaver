# this file is to insert rows into households/users table
# manage database functions

import random
import string
from collections import Counter

import requests

from api.supabase_auth import SUPABASE_ANON_KEY, SUPABASE_URL


def auth_headers(access_token):
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def create_household(access_token, name, location):
    url = f"{SUPABASE_URL}/rest/v1/households"

    body = {
        "name": name,
        "location": location,
    }

    response = requests.post(
        url,
        headers=auth_headers(access_token),
        json=body,
    )

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()[0]


def create_user_profile(access_token, user_id, email, household_id, first_name, last_name):
    url = f"{SUPABASE_URL}/rest/v1/users"

    body = {
        "id": user_id,
        "email": email,
        "household_id": household_id,
        "first_name": first_name,
        "last_name": last_name,
    }

    response = requests.post(
        url,
        headers=auth_headers(access_token),
        json=body,
    )

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()[0]


def get_user_profile(access_token, user_id):
    url = f"{SUPABASE_URL}/rest/v1/users"

    response = requests.get(
        f"{url}?id=eq.{user_id}&select=*",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    if not data:
        return None

    return data[0]


def get_admin_profile(access_token, user_id, email=None):
    url = f"{SUPABASE_URL}/rest/v1/admins"
    query = f"{url}?user_id=eq.{user_id}&select=*"

    response = requests.get(query, headers=auth_headers(access_token))

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    if not data and email:
        response = requests.get(
            f"{url}?email=eq.{email}&select=*",
            headers=auth_headers(access_token),
        )

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()

    if not data:
        return None

    admin_profile = data[0]
    if admin_profile.get("is_active") is False:
        return None

    return admin_profile


def get_household(access_token, household_id):
    url = f"{SUPABASE_URL}/rest/v1/households"

    response = requests.get(
        f"{url}?id=eq.{household_id}&select=*",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    if not data:
        return None

    return data[0]


def log_purchased_items(access_token, household_id, item_name, quantity):
    url = f"{SUPABASE_URL}/rest/v1/purchased_items"
    body = {
        "household_id": household_id,
        "item_name": item_name,
        "quantity": quantity,
    }
    response = requests.post(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()


def log_discarded_item(access_token, household_id, item_name, quantity_discarded):
    url = f"{SUPABASE_URL}/rest/v1/discarded_items"
    body = {
        "household_id": household_id,
        "item_name": item_name,
        "quantity_discarded": quantity_discarded,
    }
    response = requests.post(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()


def get_log_entry_suggestions(access_token, household_id, is_purchase=True, item_name=None):
    table = "purchased_items" if is_purchase else "discarded_items"
    quantity_column = "quantity" if is_purchase else "quantity_discarded"
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {
        "household_id": f"eq.{household_id}",
        "select": f"item_name,{quantity_column},logged_at",
        "order": "logged_at.desc",
        "limit": "200",
    }

    if item_name:
        params["item_name"] = f"eq.{item_name}"

    response = requests.get(url, headers=auth_headers(access_token), params=params)

    if response.status_code != 200:
        print(f"could not fetch log suggestions: {response.text}")
        return {
            "recent_items": [],
            "popular_items": [],
            "recent_quantities": [],
            "popular_quantities": [],
        }

    rows = response.json()
    recent_items = []
    item_counts = Counter()
    recent_quantities = []
    quantity_counts = Counter()

    for row in rows:
        row_item_name = (row.get("item_name") or "").strip()
        quantity = row.get(quantity_column)

        if row_item_name:
            item_counts[row_item_name] += 1
            if row_item_name not in recent_items and len(recent_items) < 3:
                recent_items.append(row_item_name)

        if quantity is not None:
            quantity_value = float(quantity)
            quantity_counts[quantity_value] += 1
            if quantity_value not in recent_quantities and len(recent_quantities) < 1:
                recent_quantities.append(quantity_value)

    popular_items = [
        item
        for item, _ in item_counts.most_common()
        if item not in recent_items
    ][:3]
    popular_quantities = [
        quantity
        for quantity, _ in quantity_counts.most_common()
        if quantity not in recent_quantities
    ][:2]

    return {
        "recent_items": recent_items,
        "popular_items": popular_items,
        "recent_quantities": recent_quantities,
        "popular_quantities": popular_quantities,
    }


def mark_household_modified(access_token, household_id):
    url = f"{SUPABASE_URL}/rest/v1/households?id=eq.{household_id}"
    body = {"modified": True}
    response = requests.patch(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 204]:
        raise Exception(response.text)


def generate_join_code(access_token, household_id):
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    url = f"{SUPABASE_URL}/rest/v1/households?id=eq.{household_id}"
    body = {"join_code": code}
    response = requests.patch(url, headers=auth_headers(access_token), json=body)
    if response.status_code not in [200, 204]:
        raise Exception(response.text)
    return code


def get_household_by_join_code(access_token, join_code):
    url = f"{SUPABASE_URL}/rest/v1/households"
    response = requests.get(
        f"{url}?join_code=eq.{join_code}&select=*",
        headers=auth_headers(access_token),
    )
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if not data:
        return None
    return data[0]


def clear_join_code(access_token, household_id):
    url = f"{SUPABASE_URL}/rest/v1/households?id=eq.{household_id}"
    body = {"join_code": None}
    response = requests.patch(url, headers=auth_headers(access_token), json=body)
    if response.status_code not in [200, 204]:
        raise Exception(response.text)


def get_item_intelligence_weight(access_token, household_id, item_name):
    """Fetches the specific adaptive modifier weight for an item."""
    url = f"{SUPABASE_URL}/rest/v1/item_intelligence?household_id=eq.{household_id}&item_name=eq.{item_name}"
    response = requests.get(url, headers=auth_headers(access_token))
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    return data[0]["item_weight"] if data else 1.0


def upsert_item_intelligence_weight(access_token, household_id, item_name, item_weight):
    """Saves or updates item weights when users click buttons on cards."""
    url = f"{SUPABASE_URL}/rest/v1/item_intelligence"
    headers = auth_headers(access_token)
    headers["Prefer"] = "resolution=merge-duplicates,return=representation"
    body = {
        "household_id": household_id,
        "item_name": item_name,
        "item_weight": item_weight,
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code not in [200, 201]:
        raise Exception(response.text)
    return response.json()


def get_recommendations(access_token, household_id):
    """Fetches only active recommendations for the UI cards, sorted by priority score."""
    url = f"{SUPABASE_URL}/rest/v1/recommendations?household_id=eq.{household_id}&is_active=eq.true&order=score.desc"
    response = requests.get(url, headers=auth_headers(access_token))
    if response.status_code != 200:
        raise Exception(response.text)

    unique_recommendations = []
    seen_cards = set()

    for recommendation in response.json():
        key = (
            (recommendation.get("item_name") or "").strip().lower(),
            (recommendation.get("type") or "").strip().lower(),
            (recommendation.get("subtitle") or "").strip().lower(),
        )

        if key in seen_cards:
            continue

        seen_cards.add(key)
        unique_recommendations.append(recommendation)

    return unique_recommendations


def get_recommendation(access_token, recommendation_id):
    url = f"{SUPABASE_URL}/rest/v1/recommendations?id=eq.{recommendation_id}&select=*"
    response = requests.get(url, headers=auth_headers(access_token))

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    return data[0] if data else None


def update_recommendation_feedback(access_token, recommendation_id, was_positive: bool):
    """Soft-dismisses a card, stores feedback, and adjusts its score."""
    from datetime import datetime, timezone

    url = f"{SUPABASE_URL}/rest/v1/recommendations?id=eq.{recommendation_id}"
    recommendation = get_recommendation(access_token, recommendation_id)
    current_score = float(recommendation.get("score") or 0.0) if recommendation else 0.0
    card_type = recommendation.get("type") if recommendation else None
    feedback_value = 1 if was_positive else 0
    positive_delta_by_type = {
        "ask": -0.05,
        "tip": 0.05,
        "alert": -0.25,
    }
    negative_delta_by_type = {
        "ask": -0.25,
        "tip": -0.45,
        "alert": -0.8,
    }
    score_delta = (
        positive_delta_by_type.get(card_type, 0.2)
        if was_positive
        else negative_delta_by_type.get(card_type, -0.5)
    )
    updated_score = max(current_score + score_delta, 0.0)

    body = {
        "is_active": False,
        "feedback": feedback_value,
        "score": updated_score,
        "responded_at": datetime.now(timezone.utc).isoformat(),
    }

    response = requests.patch(url, headers=auth_headers(access_token), json=body)
    if response.status_code not in [200, 204]:
        raise Exception(response.text)
