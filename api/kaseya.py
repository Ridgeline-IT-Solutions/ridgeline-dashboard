import requests
import os
from dotenv import load_dotenv
import json
# from random import randint
# import hashlib
import base64
from datetime import datetime, timedelta, timezone

load_dotenv()

# Data warehouse (odata) API endpoint
ENDPOINT = "https://serverus01.techstogether.com/api/odata/1.0/"

# token is in form of "username:apikey"
token = f"{os.getenv('VSA_USERNAME')}:{os.getenv('VSA_APIKEY')}".encode("ascii")
# Base64 encode the token
payload = base64.b64encode(token).decode("ascii")

HEADERS = {"Authorization": f"Basic {payload}"}

def data_request(query: str) -> dict:
    request = requests.get(ENDPOINT + query, headers=HEADERS)
    return request.json()['value']

def update_cache() -> None:
    """
    Updates all Kaseya API caches.

    Args:
        None
    
    Returns:
        None

    Raises:
        None
    """
    update_agents_cache()
    update_patches_cache()
    update_alarms_cache()

def update_agents_cache() -> dict:
    """
    Pulls agents from Kaseya API and updates agents.json

    Args:
        None

    Returns:
        A dictionary of all agents.

    Raises:
        None
    """
    agents = data_request("Agents?$orderby=GroupId")

    with open('cache/kaseya/agents.json', 'w+') as f:
            json.dump(agents, f)

    return agents


def get_agents() -> dict:
    """
    Attempts to read agents cache and get all of the agents.

    Args:
        None

    Returns:
        A dictionary of all agents.

    Raises:
        None
    """
    agents = {}
    try:
        # try to read from agents.json
        with open('cache/kaseya/agents.json', 'r') as f:
            agents = json.load(f)
    except:
        # if no agents.json, force update the cache
        agents = update_agents_cache()

    return agents


def update_patches_cache() -> dict:
    """
    Pulls patches from Kaseya API and updates patches.json

    Args:
        None

    Returns:
        A dictionary of all agents with their patch information.

    Raises:
        None
    """
    agents = data_request("SoftwareManagementByAgentStats?$orderby=GroupName")

    with open('cache/kaseya/patches.json', 'w+') as f:
            json.dump(agents, f)

    return agents

def get_patches() -> dict:
    """
    Returns SoftwareManagement stats.

    Args:
        None

    Returns:
        A dictionary of all agents with thier patch information.

    Raises:
        None
    """
    agents = {}

    try:
        # try to read from patches.json
        with open('cache/kaseya/patches.json', 'r') as f:
            agents = json.load(f)
    except:
        # if no patches.json, force update the cache
        agents = update_patches_cache()

    return agents

def update_alarms_cache() -> dict:
    """
    Pulls alarms from Kaseya API and updates alarms.json

    Args:
        None

    Returns:
        A dictionary of all alarms.

    Raises:
        None
    """
    alarms = data_request("MonitorAlarms")

    with open('cache/kaseya/alarms.json', 'w+') as f:
            json.dump(alarms, f)

    return alarms

def get_alarms():
    """
    Returns MonitorAlarms stats.

    Args:
        None

    Returns:
        A dictionary of all alarms.

    Raises:
        None
    """
    alarms = {}

    try:
        # try to read from alarms.json
        with open('cache/kaseya/alarms.json', 'r') as f:
            alarms = json.load(f)
    except:
        # if no alarms.json, force update the cache
        alarms = update_alarms_cache()

    return alarms


### The following is old and uses the Kaseya REST API; leaving this here in case it should be needed in the future.

# ENDPOINT = "https://serverus01.techstogether.com/api/v1.0/"

# REST Authentication not necessary at the moment
# def get_auth():
#     def get_new_token():
#         """Get VSA session token. Reference: https://help.kaseya.com/webhelp/EN/restapi/9040000/#37320.htm"""
#         request = ENDPOINT + "auth"
#         ### OLD AUTHENTICATION METHOD
#         # keep this for documentation

#         # random = randint(1, 10000)
#         # raw_SHA256_hash = hashlib.sha256(os.getenv('VSA_APIKEY').encode('ascii'))
#         # covered_SHA256_hash_temp = hashlib.sha256((os.getenv('VSA_APIKEY') + os.getenv('VSA_USERNAME')).encode('ascii'))
#         # covered_SHA256_hash = hashlib.sha256((covered_SHA256_hash_temp.hexdigest() + str(random)).encode('ascii'))
#         # raw_SHA1_hash = hashlib.sha1(os.getenv('VSA_APIKEY').encode('ascii'))
#         # covered_SHA1_hash_temp = hashlib.sha1((os.getenv('VSA_APIKEY') + os.getenv('VSA_USERNAME')).encode('ascii'))
#         # covered_SHA1_hash = hashlib.sha1((covered_SHA1_hash_temp.hexdigest() + str(random)).encode('ascii'))
#         # payload_body = {
#         #     "user": os.getenv('VSA_USERNAME'),
#         #     "pass2": covered_SHA256_hash.hexdigest(),
#         #     "pass1": covered_SHA1_hash.hexdigest(),
#         #     "rpass2": raw_SHA256_hash.hexdigest(),
#         #     "rpass1": raw_SHA1_hash.hexdigest(),
#         #     "rand2": random
#         # }
#         # payload_unencoded = []
#         # for item in payload_body:
#         #     payload_unencoded.append(f"{item}={payload_body[item]}")
#         # payload_unencoded = ','.join(payload_unencoded)

#         # payload = base64.b64encode(payload_unencoded.encode("ascii")).decode("ascii")
#         ### NEW (PAT) AUTHENTICATION METHOD
#         # create token in form of "username:pat" and encode
#         token = f"{os.getenv('VSA_USERNAME')}:{os.getenv('VSA_APIKEY')}".encode("ascii")
#         # Base64 encode the token
#         payload = base64.b64encode(token).decode("ascii")

#         headers = {"Authorization": f"Basic {payload}"}
#         auth_request = requests.get(request, headers=headers)

#         return auth_request.json()['Result']

#     auth = {}
#     try:
#         # try to read from auth.json
#         with open('cache/kaseya/auth.json', 'r') as f:
#             auth = json.load(f)
#     except:
#         # if no auth.json, get a new one
#         auth = get_new_token()
#         with open('cache/kaseya/auth.json', 'w+') as f:
#             json.dump(auth, f)

#     # check expiration
#     expiration = datetime.fromisoformat(auth['SessionExpiration'])
#     if expiration < datetime.now(timezone.utc):
#         # token has expired, get a new one
#         auth = get_new_token()
#         # write to auth.json
#         with open('cache/kaseya/auth.json', 'w') as f:
#             json.dump(auth, f)

#     return auth['Token']

# def get_agents(query: str = ""):
#     request = ENDPOINT + f"assetmgmt/agents?{query}"
#     auth_token = get_auth()
#     headers = {"Authorization": f"Bearer {auth_token}"}
#     agents = requests.get(request, headers=headers)
#     return agents.json()['Result']