import requests

from utils import utils


def get_org_by_id(env, orgId):
    """
    Retrieves organization information by ID from a specified environment.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.

    Returns:
        dict: The organization information.
    """
    url = f"http://cromag.{utils.convert_env(env)}.milezero.com/retail/api/organization/{orgId}"

    return requests.get(url=url, timeout=5).json()
