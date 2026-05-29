import argparse
import time

import worker


def run_worker_once(
    shortterm_change_in_days: int = 30,
    longterm_change_in_days: int = 90,
) -> int:
    return worker.process_modified_households(
        shortterm_change_in_days=shortterm_change_in_days,
        longterm_change_in_days=longterm_change_in_days,
    )


def run_worker_forever(
    interval_seconds: int = 60,
    shortterm_change_in_days: int = 30,
    longterm_change_in_days: int = 90,
):
    print()
    print("running recommendation worker...")
    print(f"checking every {interval_seconds} seconds")

    while True:
        processed_count = run_worker_once(
            shortterm_change_in_days=shortterm_change_in_days,
            longterm_change_in_days=longterm_change_in_days,
        )
        if processed_count:
            print(f"processed {processed_count} household(s)")
        print("finished iteration")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=int, default=60)
    parser.add_argument("--shortterm", type=int, default=30)
    parser.add_argument("--longterm", type=int, default=90)
    args = parser.parse_args()

    run_worker_forever(
        interval_seconds=args.freq,
        shortterm_change_in_days=args.shortterm,
        longterm_change_in_days=args.longterm,
    )
