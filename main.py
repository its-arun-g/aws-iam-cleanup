import argparse
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
from src.key_manager import enable_key, disable_key, delete_key
from src.user_manager import delete_user, disable_console_login
from src.utils import assume_role, assume_central_role, get_logger

logger = get_logger()


def process_items(items, action, object_type, session, max_threads=10):
    """Process keys or users concurrently."""
    with ThreadPoolExecutor(max_threads) as executor:
        if object_type == "key":
            if action == "enable":
                futures = {
                    executor.submit(enable_key, session, item): item for item in items
                }
            elif action == "disable":
                futures = {
                    executor.submit(disable_key, session, item): item for item in items
                }
            elif action == "delete":
                futures = {
                    executor.submit(delete_key, session, item): item for item in items
                }
        elif object_type == "user":
            if action == "disable":
                futures = {
                    executor.submit(disable_console_login, session, item): item
                    for item in items
                }
            elif action == "delete":
                futures = {
                    executor.submit(delete_user, session, item): item for item in items
                }
        else:
            raise ValueError(f"Unsupported object and action: {object_type}, {action}")

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing item: {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage AWS access keys and users.")
    parser.add_argument(
        "--object",
        type=str,
        required=True,
        choices=["key", "user"],
        help="The object type to manage (key or user).",
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
        help="Path to the csv file containing account_id and object",
    )
    parser.add_argument(
        "--central-account-id",
        type=str,
        required=True,
        help="Central AWS account ID where the initial role exists",
    )
    parser.add_argument(
        "--role-name",
        type=str,
        required=True,
        help="Name of the IAM role (same name in central account and all target accounts)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of threads to use for processing.",
    )

    args = parser.parse_args()

    # Read CSV file - preserve account_id as string to maintain leading zeros
    try:
        input_df = pd.read_csv(args.csv_file_path, dtype={"account_id": str, "object": str})
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        return

    # Validate CSV columns
    required_columns = ["account_id", "object"]
    missing_columns = [col for col in required_columns if col not in input_df.columns]
    if missing_columns:
        logger.error(f"CSV file is missing required columns: {missing_columns}")
        logger.error(f"Expected columns: {required_columns}")
        return

    # Step 1: Assume role in central account (first tier)
    try:
        logger.info(f"Assuming role in central account {args.central_account_id}")
        central_session = assume_central_role(args.central_account_id, args.role_name)
    except Exception as e:
        logger.error(f"Failed to assume central account role: {e}")
        return

    # Group by account_id to optimize role assumptions
    # account_id is already read as string, so leading zeros are preserved
    distinct_accounts = input_df["account_id"].unique().tolist()
    
    logger.info(f"Processing {len(distinct_accounts)} account(s)")

    for account_id in distinct_accounts:
        account_df = input_df[input_df["account_id"] == account_id]
        
        logger.info(f"Processing account {account_id}: {len(account_df)} item(s)")
        
        try:
            # Step 2: Assume cross-account role in target account (second tier)
            # Use the central session credentials to assume the target account role
            session = assume_role(account_id, args.role_name, base_session=central_session)
            
            # Extract items from CSV
            items = [str(row["object"]).strip() for _, row in account_df.iterrows()]
            
            # Process items with the specified object type
            if items:
                process_items(
                    items,
                    args.action,
                    args.object,
                    session,
                    max_threads=args.threads,
                )
        except Exception as e:
            logger.error(f"Error processing account {account_id}: {e}")
            continue


if __name__ == "__main__":
    main()
