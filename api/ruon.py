import requests
import xmltodict
import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv('RUON_KEY')

def get_agents():
    def _get_status_from(val: str):
        parsed = {}
        for field in val.split('<br>'):
            parse = field.split(': ')
            parsed[parse[0]] = parse[1]
        return parsed['State']

    endpoint = "https://rss.r-u-on.com/rssagents?id=" + KEY
    request = requests.get(endpoint)
    data_raw = xmltodict.parse(request.content)
    data = {}
    for val in data_raw['rss']['channel']['item']:
        data[val['title']] = _get_status_from(val['description'])

    return data

def get_alarms():
    endpoint = "https://rss.r-u-on.com/rssalarms?id=" + KEY
    request = requests.get(endpoint)
    data_raw = xmltodict.parse(request.content)
    data = {}
    try:
        for val in data_raw['rss']['channel']['item']:
            parsed = val['title'].split(": ")
            data[parsed[0]] = parsed[1]
    except:
        pass
        
    return data