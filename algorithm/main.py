import time
import worker
import argparse


def run_algorithm(how_frequent: int = 60):
    print()
    print("running algorithm...")
    print(f"checking every {how_frequent} seconds")

    while True:
        modified_households = worker.get_modified_households()

        if modified_households:
            item_categories = worker.map_items_with_categories()

            for household_id in modified_households:
                worker.process_household(household_id, item_categories)

        time.sleep(how_frequent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=int, default=60)
    args = parser.parse_args()
    run_algorithm(args.freq)
