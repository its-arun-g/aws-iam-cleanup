import boto3
from src.utils import get_username_from_key
from src.utils import get_logger


logger = get_logger()


def enable_key(session, access_key):
    """Enable a single AWS access key."""
    username = get_username_from_key(session, access_key)
    iam_client = session.client("iam")
    if not username:
        return
    try:
        iam_client.update_access_key(
            AccessKeyId=access_key, Status="Active", UserName=username
        )
        logger.info(f"Enabled key {access_key} for user {username}.")
        return
    except Exception as e:
        logger.error(f"Failed to enable key {access_key}: {e}")
        return


def disable_key(session, access_key):
    """Disable a single AWS access key."""
    username = get_username_from_key(session, access_key)
    iam_client = session.client("iam")
    if not username:
        return
    try:
        iam_client.update_access_key(
            AccessKeyId=access_key, Status="Inactive", UserName=username
        )
        logger.info(f"Disabled key {access_key} for user {username}.")
        return
    except Exception as e:
        logger.error(f"Failed to disable key {access_key}: {e}")
        return


def delete_key(session, access_key):
    """Delete a single AWS access key."""
    username = get_username_from_key(session, access_key)
    iam_client = session.client("iam")
    if not username:
        return
    try:
        iam_client.delete_access_key(AccessKeyId=access_key, UserName=username)
        logger.info(f"Deleted key {access_key} for user {username}.")
        return
    except Exception as e:
        logger.error(f"Failed to delete key {access_key}: {e}")
        return
