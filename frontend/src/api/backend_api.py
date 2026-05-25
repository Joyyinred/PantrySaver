# talks to Spring Boot REST API

import requests


BACKEND_URL = "http://localhost:8080"


def auth_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def sync_user(access_token: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/auth/sync",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_current_user(access_token: str) -> dict:
    response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_my_household(access_token: str) -> dict:
    response = requests.get(
        f"{BACKEND_URL}/households/me",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_household_members(access_token: str) -> list:
    response = requests.get(
        f"{BACKEND_URL}/households/me/members",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def create_household(access_token: str, name: str, location: str | None = None) -> dict:
    body = {
        "name": name,
        "location": location,
    }

    response = requests.post(
        f"{BACKEND_URL}/households",
        headers=auth_headers(access_token),
        json=body,
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def join_household(access_token: str, household_id: str) -> dict:
    body = {
        "householdId": household_id,
    }

    response = requests.post(
        f"{BACKEND_URL}/households/join",
        headers=auth_headers(access_token),
        json=body,
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()

def generate_join_code(access_token: str) -> str:

    url = f"{BACKEND_URL}/households/generate_join_code"
    response = requests.post(
        url,
        headers=auth_headers(access_token),
    )
    if response.status_code != 200:
        raise Exception(response.text)
    return response.json().get("join_code")

def join_household_by_code(access_token: str, join_code: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/households/join_by_code",
        headers=auth_headers(access_token),
        json={"join_code": join_code},
    )
    if response.status_code != 200:
        raise Exception(response.text)
    return response.json()
    

def update_household(access_token: str, name: str, location: str | None = None) -> dict:
    body = {
        "name": name,
        "location": location,
    }

    response = requests.put(
        f"{BACKEND_URL}/households/me",
        headers=auth_headers(access_token),
        json=body,
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def leave_household(access_token: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/households/leave",
        headers=auth_headers(access_token),
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()