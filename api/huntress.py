import requests
import os
from dotenv import load_dotenv
import json
import base64
from datetime import datetime, timedelta, timezone

from api.caching import *

load_dotenv()

# Data warehouse (odata) API endpoint
ENDPOINT = "https://api.huntress.io/v1/"

# token is in form of "username:apikey"
token = f"{os.getenv('HUNTRESS_PUBLIC')}:{os.getenv('HUNTRESS_SECRET')}".encode("ascii")
# Base64 encode the token
payload = base64.b64encode(token).decode("ascii")

HEADERS = {"Authorization": f"Basic {payload}"}

def data_request(query: str, limit: int = 500) -> dict:
    result = []
    request = requests.get(ENDPOINT + query + f'?limit={limit}', headers=HEADERS)
    result.append(request.json()[query])

    more = True
    while more:
        if request.json()['pagination'].get('next_page'):
            request = requests.get(request.json()['pagination']['next_page_url'], headers=HEADERS)
            result.append(request.json()[query])
        else:
            more = False

    return result[0]

def update_agents():
    agents = data_request('agents')

    cache('huntress/agents.json', agents)

    return agents

def get_agents():
    agents = get_cache('huntress/agents.json', timedelta(minutes=10), update_agents)
    return agents

def update_incidents():
    incidents = data_request('incident_reports')

    cache('huntress/incidents.json', incidents)

    return incidents

def get_incidents():
    incidents = get_cache('huntress/incidents.json', timedelta(minutes=10), update_incidents)
    return incidents