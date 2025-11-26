import boto3
from src.utils import get_logger

logger = get_logger()


def __detach_managed_policies(iam_client, username):
    try:
        response = iam_client.list_attached_user_policies(UserName=username)
        for policy in response["AttachedPolicies"]:
            iam_client.detach_user_policy(
                UserName=username, PolicyArn=policy["PolicyArn"]
            )
            logger.debug(
                f"Detached managed policy {policy['PolicyName']} from user {username}."
            )
    except Exception as e:
        logger.error(f"Failed to detach managed policies from user {username}: {e}")
    return


def __delete_inline_policies(iam_client, username):
    try:
        response = iam_client.list_user_policies(UserName=username)
        for policy in response["PolicyNames"]:
            iam_client.delete_user_policy(UserName=username, PolicyName=policy)
            logger.debug(f"Deleted inline policy {policy} from user {username}.")
    except Exception as e:
        logger.error(f"Failed to delete inline policies from user {username}: {e}")
    return


def __remove_user_from_groups(iam_client, username):
    try:
        groups = iam_client.list_groups_for_user(UserName=username)
        for group in groups["Groups"]:
            iam_client.remove_user_from_group(
                UserName=username, GroupName=group["GroupName"]
            )
            logger.debug(f"Removed {username} from group {group['GroupName']}")
    except Exception as e:
        logger.error(f"Failed to remove user {username} from groups: {e}")
    return


def __delete_access_keys(iam_client, username):
    try:
        response = iam_client.list_access_keys(UserName=username)
        for key in response.get("AccessKeyMetadata", []):
            iam_client.delete_access_key(
                AccessKeyId=key["AccessKeyId"], UserName=username
            )
        logger.debug(f"Deleted access keys for user {username}.")
    except Exception as e:
        logger.error(f"Failed to delete access keys for user {username}: {e}")
    return


def __remove_mfa_devices(iam_client, username):
    try:
        response = iam_client.list_mfa_devices(UserName=username)
        for device in response.get("MFADevices", []):
            iam_client.deactivate_mfa_device(
                UserName=username, SerialNumber=device["SerialNumber"]
            )
            iam_client.delete_virtual_mfa_device(SerialNumber=device["SerialNumber"])
        logger.debug(f"Removed MFA devices for user {username}.")
    except Exception as e:
        logger.error(f"Failed to remove MFA devices for user {username}: {e}")
    return


def __delete_signing_certificates(iam_client, username):
    try:
        response = iam_client.list_signing_certificates(UserName=username)
        for cert in response.get("Certificates", []):
            iam_client.delete_signing_certificate(
                UserName=username, CertificateId=cert["CertificateId"]
            )
        logger.debug(f"Deleted signing certificates for user {username}.")
    except Exception as e:
        logger.error(f"Failed to delete signing certificates for user {username}: {e}")
    return


def __delete_ssh_public_keys(iam_client, username):
    try:
        response = iam_client.list_ssh_public_keys(UserName=username)
        for key in response.get("SSHPublicKeys", []):
            iam_client.delete_ssh_public_key(
                UserName=username, SSHPublicKeyId=key["SSHPublicKeyId"]
            )
        logger.debug(f"Deleted SSH public keys for user {username}.")
    except Exception as e:
        logger.error(f"Failed to delete SSH public keys for user {username}: {e}")
    return


def __service_specific_credentials(iam_client, username):
    try:
        response = iam_client.list_service_specific_credentials(UserName=username)
        for cred in response.get("ServiceSpecificCredentials", []):
            iam_client.delete_service_specific_credential(
                UserName=username,
                ServiceSpecificCredentialId=cred["ServiceSpecificCredentialId"],
            )
        logger.debug(f"Deleted service-specific credentials for user {username}.")
    except Exception as e:
        logger.error(
            f"Failed to delete service-specific credentials for user {username}: {e}"
        )
    return


def __delete_login_profile(iam_client, username):
    try:
        iam_client.delete_login_profile(UserName=username)
        logger.debug(f"Deleted login profile for user {username}.")
    except iam_client.exceptions.NoSuchEntityException:
        logger.debug(f"No login profile found for user {username}")
    except Exception as e:
        logger.error(f"Failed to delete login profile for user {username}: {e}")
    return


def __perform_delete_user(iam_client, username):
    try:
        iam_client.delete_user(UserName=username)
        logger.info(f"Deleted user {username}.")
    except iam_client.exceptions.NoSuchEntityException:
        logger.info(f"User {username} does not exist")
    except Exception as e:
        logger.error(f"Failed to delete user {username}: {e}")
    return


def disable_console_login(session, username):
    """Disable console login for a user by deleting their login profile."""
    iam_client = session.client("iam")
    __delete_login_profile(iam_client, username)
    logger.info(f"Console login disabled for user {username}.")
    return


def delete_user(session, username):
    iam_client = session.client("iam")
    __detach_managed_policies(iam_client, username)
    __delete_inline_policies(iam_client, username)
    __remove_user_from_groups(iam_client, username)
    __delete_access_keys(iam_client, username)
    __remove_mfa_devices(iam_client, username)
    __delete_signing_certificates(iam_client, username)
    __delete_ssh_public_keys(iam_client, username)
    __service_specific_credentials(iam_client, username)
    __delete_login_profile(iam_client, username)
    __perform_delete_user(iam_client, username)
    return
