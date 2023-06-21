import requests
import datetime
from pyotp import totp
import os
from dotenv import load_dotenv
import json

from api.caching import *

load_dotenv()

def _authenticate():
    """Get a new token from Auth0 for DNSFilter"""
    data = {
        'client_id': 'zJ1WJHavuUFx89cConwlipxoOc2J3TVQ',
        'realm': 'Username-Password-Authentication',
        'audience': 'https://dnsfilter.auth0.com/mfa/',
        'grant_type': 'http://auth0.com/oauth/grant-type/password-realm',
        'scope': 'enroll read:authenticators remove:authenticators offline_access openid picture name email',
        'username': os.getenv('DNSF_USER'),
        'password': os.getenv('DNSF_PASS')
    }
    # request mfa_token (this logs in but will require MFA)
    mfa_token_request = requests.post('https://dnsfilter.auth0.com/oauth/token', data=data)
    mfa_token = mfa_token_request.json()['mfa_token']

    # generate TOTP
    otp = totp.TOTP(os.getenv('DNSF_2FAK'))

    data = {
        'grant_type': 'http://auth0.com/oauth/grant-type/mfa-otp',
        'client_id': 'zJ1WJHavuUFx89cConwlipxoOc2J3TVQ',
        'mfa_token': mfa_token,
        'otp': otp.now()
    }
    # request the access_token
    token_request = requests.post('https://dnsfilter.auth0.com/oauth/token', data=data)
    token = token_request.json()

    cache('dnsfilter/auth.json', token)

    return f'{token["token_type"]} {token["access_token"]}'

def _get_token():
    cache = get_cache('dnsfilter/auth.json', datetime.timedelta(minutes=10), _authenticate)

    token = f'{cache["token_type"]} {cache["access_token"]}'

    return token

def _get_organizations():
    request = requests.get('https://api.dnsfilter.com/v1/organizations', headers={'authorization': _get_token()}, data={'basic_info':1})
    organizations = {}
    for org in request.json()['data']:
        if not org['attributes']['canceled']:
            organizations[org['id']] = org['attributes']['name']

    cache('dnsfilter/organizations.json', organizations)

    return organizations

def _get_total_stats(offset: int = 24):
    time_from = (datetime.datetime.now() - datetime.timedelta(hours=offset)).isoformat() + "Z"
    request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_organizations_stats', headers={'authorization': _get_token()}, data={'msp_id':1557,'from': time_from})
    
    ret = {
        'total': request.json()['data']['total_requests'], 
        'allowed': request.json()['data']['allowed_requests'], 
        'blocked': request.json()['data']['blocked_requests'],
        'threats': request.json()['data']['threat_requests']
    }

    cache(f'dnsfilter/total_stats_{offset}.json', ret)
    
    return ret

def _get_breakdown_stats(offset: int = 24):
    time_from = (datetime.datetime.now() - datetime.timedelta(hours=offset)).isoformat() + "Z"
    request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_threats', headers={'authorization': _get_token()}, data={'organization_ids':','.join(get_cache('dnsfilter/organizations.json', datetime.timedelta(minutes=10), _get_organizations).keys()),'show_individual_networks':1,'from': time_from})
    ret = {}
    for bucket in request.json()['data']['values']:
        if bucket['network_name'] not in ret:
            ret[bucket['network_name']] = 0
        ret[bucket['network_name']] += bucket['total']

    cache(f'dnsfilter/breakdown_stats_{offset}.json', ret)

    return ret

def get_most_threats(top: int = 3, offset: int = 24):
    stats = get_cache(f'dnsfilter/breakdown_stats_{offset}.json', datetime.timedelta(minutes=10), _get_breakdown_stats, (offset))
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top])