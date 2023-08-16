import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

from api.caching import *

ENDPOINT = "https://app.mojohelpdesk.com/api/v2/"
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

load_dotenv()

def update_tickets() -> dict:
    request = ENDPOINT + "tickets/search?per_page=100&sf=created_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
    tickets = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        page_json = this_page.json()
        if len(page_json) < 1:
            break
        else:
            # set the id as the key for the object
            for ticket in page_json:
                tickets[ticket['id']] = ticket

    cache('mojo/tickets.json', tickets)

    return tickets

def update_users() -> dict:
    request = ENDPOINT + "users?per_page=100&access_key=" + os.getenv('MOJO_APIKEY')
    users = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            for user in this_page.json():
                users[user['id']] = user

    cache('mojo/users.json', users)

    return users

def update_groups() -> dict:
    request = ENDPOINT + "groups/?per_page=100&access_key=" + os.getenv('MOJO_APIKEY')
    groups = {}
    for i in range(1, 100):
        this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
        if len(this_page.json()) < 1:
            break
        else:
            for group in this_page.json():
                groups[group['id']] = group

    cache('mojo/groups.json', groups)

    return groups

# def get_tickets_updated_within_day(days: int) -> list:
#     """
#     Get all tickets updated within the last `days` day(s)

#     Args:
#         None

#     Returns:
#         `list` of tickets

#     Raises:
#         None
#     """
#     request = ENDPOINT + f"tickets/search?query=updated_on:[{datetime.isoformat(datetime.utcnow() - timedelta(days = days))} TO *]&per_page=100&sf=updated_on&r=0&access_key=" + os.getenv('MOJO_APIKEY')
#     tickets = []
#     for i in range(1, 100):
#         this_page = requests.get(f"{request}&page={i}", headers=HEADERS)
#         if len(this_page.json()) < 1:
#             break
#         else:
#             tickets += this_page.json()
#     return tickets

# def update_cache(days = 1):
#     update_tickets = get_tickets_updated_within_day(days)
#     tickets = {}
#     with open('cache/mojo/tickets.json', 'r') as f:
#         try:
#             tickets = json.load(f)
#         except:
#             # cache is likely empty
#             #get_cache()
#             pass

#         for ticket in update_tickets:
#             tickets.update({str(ticket['id']): ticket})

#     with open('cache/mojo/tickets.json', 'w+') as f:
#         json.dump(tickets, f)

def get_tickets() -> list:
    tickets = get_cache('mojo/tickets.json', timedelta(minutes = 10), update_tickets)
    
    return tickets
    
def get_users() -> list:
    users = get_cache('mojo/users.json', timedelta(minutes = 10), update_users)
    
    return users
    
def get_groups() -> list:
    groups = get_cache('mojo/groups.json', timedelta(minutes = 10), update_groups)
    
    return groups