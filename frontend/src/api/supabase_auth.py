import requests


SUPABASE_URL = "https://mhavpdfogtoanjdaluox.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_WSh3sw_jmKTqJdd7SYf__Q_iSj15XoA"


def signup(email: str, password: str) -> dict:
    url = f"{SUPABASE_URL}/auth/v1/signup"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "email": email,
        "password": password,
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()


def login(email: str, password: str) -> dict:
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "email": email,
        "password": password,
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()