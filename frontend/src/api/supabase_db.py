# this file is to insert rows into households/users table
# manage database functions


import re

import requests

import random
import string

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

# fetch login user
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

    url = f'{SUPABASE_URL}/rest/v1/purchased_items'
    body = {
        'household_id': household_id,
        'item_name': item_name,
        'quantity': quantity
    }
    response = requests.post(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 201]:

        raise Exception(response.text)

    return response.json()

def log_discarded_item(access_token, household_id, item_name, quantity_discarded):

    url = f'{SUPABASE_URL}/rest/v1/discarded_items'
    body = {
        'household_id': household_id,
        'item_name': item_name,
        'quantity_discarded': quantity_discarded
    }
    response = requests.post(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 201]:

        raise Exception(response.text)

    return response.json()

def mark_household_modified(access_token, household_id):

    url = f'{SUPABASE_URL}/rest/v1/households?id=eq.{household_id}'
    body = {'modified': True}
    response = requests.patch(url, headers=auth_headers(access_token), json=body)

    if response.status_code not in [200, 204]:

        raise Exception(response.text)

def generate_join_code(access_token, household_id):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    url = f"{SUPABASE_URL}/rest/v1/households?id=eq.{household_id}"
    body = {"join_code": code}
    response = requests.patch(url, headers=auth_headers(access_token), json=body)
    if response.status_code not in [200, 204]:
        raise Exception(response.text)
    return code
