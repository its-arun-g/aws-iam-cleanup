import argparse
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from src.key_manager import enable_key, disable_key, delete_key
from src.user_manager import delete_user, disable_console_login


def process_items(items, action, object_type, profile, max_threads=10):
    """Process keys or users concurrently."""
    with ThreadPoolExecutor(max_threads) as executor:
        if object_type == "key":
            if action == "enable":
                futures = {
                    executor.submit(enable_key, profile, item): item for item in items
                }
            elif action == "disable":
                futures = {
                    executor.submit(disable_key, profile, item): item for item in items
                }
            elif action == "delete":
                futures = {
                    executor.submit(delete_key, profile, item): item for item in items
                }
        elif object_type == "user":
            if action == "disable":
                futures = {
                    executor.submit(disable_console_login, profile, item): item
                    for item in items
                }
            elif action == "delete":
                futures = {
                    executor.submit(delete_user, profile, item): item for item in items
                }
        else:
            raise ValueError(f"Unsupported object and action: {object_type}, {action}")

        for future in as_completed(futures):
            future.result()


def main():
    parser = argparse.ArgumentParser(description="Manage AWS access keys and users.")
    parser.add_argument(
        "--object",
        type=str,
        required=True,
        choices=["key", "user"],
        help="The object to manage (key or user).",
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["enable", "disable", "delete"],
        help="The action to perform (enable, disable, or delete).",
    )
    parser.add_argument(
        "--csv-file-path",
        type=str,
        required=True,
        help="Path to the csv file containing account and object",
    )
    parser.add_argument(
        "--profile-name",
        type=str,
        required=True,
        help="Profile name existing in all accounts to be used for deletion",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of threads to use for processing.",
    )

    args = parser.parse_args()

    input_df = pd.read_csv(args.csv_file_path)

    distinct_accounts = input_df["account"].unique().tolist()

    for account in distinct_accounts:
        items = input_df[input_df["account"] == account]["object"].unique().tolist()
        try:
            process_items(
                items,
                args.action,
                args.object,
                f"{account}:{args.profile_name}",
                max_threads=args.threads,
            )
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
