from db import supabase


def main():
    response = supabase.table("test_item").select("*").limit(5).execute()
    print(response.data)


if __name__ == "__main__":
    main()
