# this file is to insert rows into households/users table
# manage database functions


import requests

from api.supabase_auth import SUPABASE_URL, SUPABASE_ANON_KEY


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