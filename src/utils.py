import boto3
import logging


def assume_role(account_id, role_name, session_name="IAMCleanupSession", base_session=None):
    """
    Assume a cross-account IAM role.
    
    Args:
        account_id: Target AWS account ID
        role_name: Name of the role to assume
        session_name: Name for the assumed role session
        base_session: Optional boto3.Session to use for assuming the role (for 2-tier assumption)
    
    Returns:
        boto3.Session: Session with assumed role credentials
    """
    if base_session:
        sts_client = base_session.client("sts")
    else:
        sts_client = boto3.client("sts")
    
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        credentials = response["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
        return session
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise


def assume_central_role(central_account_id, central_role_name, session_name="CentralAccountSession"):
    """
    Assume a role in the central account (first tier of 2-tier role assumption).
    
    Args:
        central_account_id: Central AWS account ID
        central_role_name: Name of the role in central account
        session_name: Name for the assumed role session
    
    Returns:
        boto3.Session: Session with assumed role credentials from central account
    """
    sts_client = boto3.client("sts")
    role_arn = f"arn:aws:iam::{central_account_id}:role/{central_role_name}"
    
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        credentials = response["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
        return session
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to assume central account role {role_arn}: {e}")
        raise


def get_username_from_key(session, access_key):
    """Fetch the username associated with an access key."""
    iam_client = session.client("iam")
    try:
        response = iam_client.get_access_key_last_used(AccessKeyId=access_key)
        return response.get("UserName")
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error fetching username for key {access_key}: {e}")
        return None


def get_logger() -> logging.Logger:
    format = "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
    logging.basicConfig(format=format)
    logger = logging.getLogger("aws-keys-cleanup")
    logger.setLevel("INFO")
    return logger
