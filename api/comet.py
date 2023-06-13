import requests
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()
URL = "https://192.168.100.2/api/v1/"

def _request_admin(endpoint: str, additional_params: dict = {}) -> dict:
    """Make a request to comet in admin context (ie. any request to https://192.168.100.2/api/v1/admin/).

    Args:
        endpoint: The endpoint of the API request.
        additional_params: A dictionary of any additional parameters. 
    
    Returns:
        The JSON response from the API.
    """
    data = {
        "Username": os.getenv('COMET_USER'),
        "AuthType": "Password",
        "Password": os.getenv('COMET_PASS'),
        **additional_params
    }
    request = requests.post(URL + "admin/" + endpoint, data=data, verify=False)
    return request.json()

def _get_user_key(username: str) -> str | bool:
    """Make a request to comet for a user session key.

    Args:
        username: The user to get a session key for. 
    
    Returns:
        The session key or False (if failed).
    """
    data = {
        "TargetUser": username
    }
    request = _request_admin("account/session-start-as-user", additional_params=data)
    if request['Status'] == 200:
        return request['SessionKey']
    else:
        return False

def _request_user(endpoint: str, username: str, key: str, additional_params: dict = {}) -> dict:
    """Make a request to comet in user context (ie. any request to https://192.168.100.2/api/v1/user/). Requires a session key generated from _get_user_key().

    Args:
        endpoint: The endpoint of the API request.
        username: The user to use.
        key: The session key generated from _get_user_key().
        additional_params: A dictionary of any additional parameters. 
    
    Returns:
        The JSON response from the API.
    """
    data = {
        "Username": username,
        "AuthType": "SessionKey",
        "Password": key,
        **additional_params
    }
    request = requests.post(URL + "user/" + endpoint, data=data, verify=False)
    return request.json()

def counts() -> dict:
    """Get various device counts.

    Args:
        None    
    
    Returns:
        A dictionary in the form of {total, online, offline, outdated} 
    """
    version = _request_admin('meta/version')['Version']
    ret = {
        "total": 0,
        "online": 0,
        "offline": 0,
        "outdated": 0
    }
    total = _request_admin('list-users-full').values()
    active = _request_admin('dispatcher/list-active').values()
    
    ret['total'] = len(total)
    ret['online'] = len(active)
    ret['offline'] = len(total) - len(active)

    for device in active:
        if device['ReportedVersion'] != version:
            ret['outdated'] += 1

    for val in ret:
        if ret[val] < 0:
            ret[val] = 0

    return ret

def get_jobs_24h():
    """Get all jobs in the last 24 hours.

    Args:
        None 
    
    Returns:
        A dictionary of all jobs done in the last 24 hours.
    """
    now = int(time.time())
    yesterday = int(now - 86400)
    data = {
        "Start": yesterday,
        "End": now
    }
    return _request_admin('get-jobs-for-date-range', data)

def get_jobs_status(jobs: dict = None):
    if not jobs:
        jobs = get_jobs_24h()

    statuses = {
        "Total": len(jobs),
        "Success": 0,
        "Error": 0,
        "Warning": 0,
        "Missed": 0,
        "Running": 0,
        "Skipped": 0
    }

    for job in jobs:
        if (5000 <= job["Status"] <= 5999):
            statuses["Success"] += 1
        elif (6000 <= job["Status"] <= 6999):
            statuses["Running"] += 1
        elif (job["Status"] == 7001):
            statuses["Warning"] += 1
        elif (job["Status"] == 7004):
            statuses["Missed"] += 1
        elif (job["Status"] == 7006):
            statuses["Skipped"] += 1
        else:
            statuses["Error"] += 1

    return statuses

def update_cache():
    jobs = get_jobs_24h()

    with open('cache/comet/jobs.json', 'w+') as f:
            json.dump(jobs, f)

    return jobs

def get_cached_jobs():
    jobs = {}
    try:
        # try to read from jobs.json
        with open('cache/comet/jobs.json', 'r') as f:
            jobs = json.load(f)
    except:
        # if no jobs.json, force update the cache
        jobs = update_cache()

    return jobs