import uuid
from datetime import datetime, timedelta, timezone
from db import supabase


def normalize(text: str) -> str:
    return text.strip().lower()


def add_mock_data_to_supabase():
    
    print()
    print("connecting...")

    household_id = str(uuid.uuid4())
    john_id = str(uuid.uuid4())
    jane_id = str(uuid.uuid4())

    now = datetime.now(timezone.utc)
    recent_date = (now - timedelta(days=2)).isoformat()
    old_date = (now - timedelta(days=35)).isoformat()
    super_old_date = (now - timedelta(days=100)).isoformat()

    categories = [
        {"id": str(uuid.uuid4()), "name": "fruit"},
        {"id": str(uuid.uuid4()), "name": "fruit & vegetables"},
        {"id": str(uuid.uuid4()), "name": "dairy"},
        {"id": str(uuid.uuid4()), "name": "vegetables"},
        {"id": str(uuid.uuid4()), "name": "bakery"},
    ]

    supabase.table("categories").insert(categories).execute()

    mapped_categories = {}

    for category in categories:
        category_name = category["name"]
        category_id = category["id"]
        mapped_categories[category_name] = category_id

    supabase.table("households").insert({
        "id": household_id,
        "name": "doe household",
        "location": "växjö, sweden",
        "modified": True
    }).execute()

    users = [
        {
            "id": john_id,
            "email": "john.doe@gmail.com",
            "household_id": household_id
        },
        {
            "id": jane_id,
            "email": "jane.doe@gmail.com",
            "household_id": household_id
        }
    ]

    supabase.table("users").insert(users).execute()

    purchased_items = [
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "bananas",
            "quantity": 5.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "milk",
            "quantity": 2.0,
            "logged_at": old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "cheese",
            "quantity": 1.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "spinach",
            "quantity": 3.0,
            "logged_at": super_old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "apples",
            "quantity": 6.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "yogurt",
            "quantity": 4.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "tomatoes",
            "quantity": 8.0,
            "logged_at": old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "carrots",
            "quantity": 10.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "bread",
            "quantity": 2.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "eggs",
            "quantity": 12.0,
            "logged_at": recent_date
        }
    ]

    supabase.table("purchased_items").insert(purchased_items).execute()

    discarded_items = [
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "bananas",
            "quantity_discarded": 1.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "bananas",
            "quantity_discarded": 1.0,
            "logged_at": recent_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "milk",
            "quantity_discarded": 1.0,
            "logged_at": old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "milk",
            "quantity_discarded": 1.0,
            "logged_at": old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": jane_id,
            "household_id": household_id,
            "item_name": "spinach",
            "quantity_discarded": 1.0,
            "logged_at": super_old_date
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": john_id,
            "household_id": household_id,
            "item_name": "bread",
            "quantity_discarded": 1.0,
            "logged_at": recent_date
        }
    ]

    supabase.table("discarded_items").insert(discarded_items).execute()

    item_categories = [
        {"item_name": "bananas", "category_id": mapped_categories["fruit"]},
        {"item_name": "bananas", "category_id": mapped_categories["fruit & vegetables"]},
        {"item_name": "milk", "category_id": mapped_categories["dairy"]},
        {"item_name": "cheese", "category_id": mapped_categories["dairy"]},
        {"item_name": "yogurt", "category_id": mapped_categories["dairy"]},
        {"item_name": "spinach", "category_id": mapped_categories["fruit & vegetables"]},
        {"item_name": "spinach", "category_id": mapped_categories["vegetables"]},
        {"item_name": "tomatoes", "category_id": mapped_categories["fruit & vegetables"]},
        {"item_name": "carrots", "category_id": mapped_categories["vegetables"]},
        {"item_name": "bread", "category_id": mapped_categories["bakery"]},
        {"item_name": "apples", "category_id": mapped_categories["fruit"]},
    ]

    supabase.table("item_categories").insert(item_categories).execute()

    print()
    print("added mock data succesfully")
    print(f"housegold id: {household_id}")
    print(f"john doe id: {john_id}")
    print(f"john doe email: {users[0]['email']}")
    print(f"jane doe id: {jane_id}")
    print(f"jane doe email: {users[1]['email']}")


if __name__ == "__main__":
    add_mock_data_to_supabase()