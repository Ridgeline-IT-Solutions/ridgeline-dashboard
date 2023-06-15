import requests
import datetime
from pyotp import totp
import os
from dotenv import load_dotenv
import json

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
    token['last_updated'] = datetime.datetime.now().timestamp()

    # save to auth.json
    with open('cache/dnsfilter/auth.json', 'w+') as f:
        json.dump(token, f)
    
    return f'{token["token_type"]} {token["access_token"]}'

def _get_token():
    """Validate cached access token, and get a new one if it's expired or doesn't exist."""
    try:
        with open('cache/dnsfilter/auth.json', 'r+') as f:
            token = json.load(f)
            if datetime.datetime.fromtimestamp(token['last_updated'] + token['expires_in']) < datetime.datetime.now():
                #print('out of date')
                return _authenticate()
            else:
                #print('up to date')
                return f'{token["token_type"]} {token["access_token"]}'
    except:
        #print('no token')
        return _authenticate()

def _get_organizations():
    request = requests.get('https://api.dnsfilter.com/v1/organizations', headers={'authorization': _get_token()}, data={'basic_info':1})
    organizations = {}
    for org in request.json()['data']:
        if not org['attributes']['canceled']:
            organizations[org['id']] = org['attributes']['name']

    return organizations

# def get_total_requests(offset: int):
#     time_from = (datetime.datetime.now() - datetime.timedelta(days=offset)).isoformat() + "Z"
#     request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_requests', headers={'authorization': _get_token()}, data={'msp_id':1557,'from': time_from})
#     retval = 0
#     for bucket in request.json()['data']['values']:
#         retval += bucket['total']

#     return retval

# def get_total_threats(offset: int):
#     time_from = (datetime.datetime.now() - datetime.timedelta(days=offset)).isoformat() + "Z"
#     request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_threats', headers={'authorization': _get_token()}, data={'organization_ids':','.join(_get_organizations().keys()),'from': time_from})
#     retval = 0
#     for bucket in request.json()['data']['values']:
#         retval += bucket['total']

#     return retval

# print(get_total_requests(7))
# print(get_total_threats(7))

def get_total_stats(offset: int = 24):
    time_from = (datetime.datetime.now() - datetime.timedelta(hours=offset)).isoformat() + "Z"
    request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_organizations_stats', headers={'authorization': _get_token()}, data={'msp_id':1557,'from': time_from})
    return {
        'total': request.json()['data']['total_requests'], 
        'allowed': request.json()['data']['allowed_requests'], 
        'blocked': request.json()['data']['blocked_requests'],
        'threats': request.json()['data']['threat_requests']
    }

def get_breakdown_stats(offset: int = 24):
    time_from = (datetime.datetime.now() - datetime.timedelta(hours=offset)).isoformat() + "Z"
    request = requests.get('https://api.dnsfilter.com/v1/traffic_reports/total_threats', headers={'authorization': _get_token()}, data={'organization_ids':','.join(_get_organizations().keys()),'show_individual_networks':1,'from': time_from})
    ret = {}
    for bucket in request.json()['data']['values']:
        if bucket['network_name'] not in ret:
            ret[bucket['network_name']] = 0
        ret[bucket['network_name']] += bucket['total']
    return ret

def get_most_threats(top: int = 3, offset: int = 24):
    stats = get_breakdown_stats(offset)
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top])
