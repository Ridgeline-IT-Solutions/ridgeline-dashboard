import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

ENDPOINT = "https://app.mojohelpdesk.com/api/v2/"
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

load_dotenv()

def get_all_tickets() -> dict:
    request = ENDPOINT + "tickets/search?per_page=100&sf=created_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
    tickets = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            # set the id as the key for the object
            for ticket in this_page.json():
                tickets[ticket['id']] = ticket
    return tickets

def get_all_users() -> dict:
    request = ENDPOINT + "users?per_page=100&access_key=" + os.getenv('MOJO_APIKEY')
    users = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            for user in this_page.json():
                users[user['id']] = user
    return users

def get_all_groups() -> dict:
    request = ENDPOINT + "groups/?per_page=100&access_key=" + os.getenv('MOJO_APIKEY')
    groups = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            for group in this_page.json():
                groups[group['id']] = group
    return groups

# def get_all_open_tickets():
#     request = ENDPOINT + "tickets/search?query=status.id:(<50)&per_page=100&sf=updated_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
#     tickets = []
#     for i in range(1, 100):
#         this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
#         if len(this_page.json()) < 1:
#             break
#         else:
#             tickets += this_page.json()
#     return tickets

# def get_closed_tickets():
#     """Return tickets closed in the last 30 days"""
#     request = ENDPOINT + f"tickets/search?query=status.id:(60) AND updated_on:[{datetime.isoformat(datetime.utcnow() - timedelta(days = 30))} TO *]&per_page=100&sf=updated_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
#     tickets = []
#     for i in range(1, 100):
#         this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
#         if len(this_page.json()) < 1:
#             break
#         else:
#             tickets += this_page.json()
#     return tickets

def get_tickets_updated_within_day(days: int) -> list:
    """
    Get all tickets updated within the last `days` day(s)

    Args:
        None

    Returns:
        `list` of tickets

    Raises:
        None
    """
    request = ENDPOINT + f"tickets/search?query=updated_on:[{datetime.isoformat(datetime.utcnow() - timedelta(days = days))} TO *]&per_page=100&sf=updated_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
    tickets = []
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            tickets += this_page.json()
    return tickets

def get_cache():
    """
    Get all tickets, clients, and companies from mojo and cache. Should only be run once, afterwards use update_cache.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    all_tickets = get_all_tickets()
    with open('cache/mojo/tickets.json', 'w+') as f:
        json.dump(all_tickets, f)
    all_users = get_all_users()
    with open('cache/mojo/users.json', 'w+') as f:
        json.dump(all_users, f)
    all_groups = get_all_groups()
    with open('cache/mojo/groups.json', 'w+') as f:
        json.dump(all_groups, f)

def update_cache(days = 1):
    update_tickets = get_tickets_updated_within_day(days)
    tickets = {}
    with open('cache/mojo/tickets.json', 'r') as f:
        try:
            tickets = json.load(f)
        except:
            # cache is likely empty
            #get_cache()
            pass

        for ticket in update_tickets:
            tickets.update({str(ticket['id']): ticket})

    with open('cache/mojo/tickets.json', 'w+') as f:
        json.dump(tickets, f)

def get_cached_tickets() -> list:
    tickets = []
    with open('cache/mojo/tickets.json', 'r') as f:
        tickets = list(json.load(f).values())
    
    return tickets
    
def get_cached_users() -> list:
    users = []
    with open('cache/mojo/users.json', 'r') as f:
        users = list(json.load(f).values())
    
    return users
    
def get_cached_groups() -> list:
    groups = []
    with open('cache/mojo/groups.json', 'r') as f:
        groups = list(json.load(f).values())
    
    return groups