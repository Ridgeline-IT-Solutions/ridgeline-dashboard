# ridgeline-dashboard
## Prerequisites
- Python 3.11.3+ recommended (> 3.7 should work)
- pip packages:
  - python-dotenv
  - requests
  - flask
  - xmltodict
  - geopy (for map)

## Installation/Run Instructions
1. Clone code
2. Install above pip packages if not already done
3. Run main.py
4. Flask server should be on http://localhost:5000

## Technical Considerations
- API updates every 10 minutes
- Need to set environment variables in /api/.env file
```
# Mojo
MOJO_APIKEY   = 'mojo_access_key'

# VSA
VSA_USERNAME  = 'vsa_username'
VSA_APIKEY    = 'vsa_api_accesskey'

# Comet
COMET_USER    = 'comet_username'
COMET_PASS    = 'comet_password'

# R-U-ON
RUON_KEY      = 'ruon_account_key'

# DNSFilter
DNSF_USER     = 'dnsfilter_user_email'
DNSF_PASS     = 'dnsfilter_user_password'
DNSF_2FAK     = 'dnsfilter_user_totp'

# Huntress
HUNTRESS_PUBLIC = 'huntress_public_key'
HUNTRESS_SECRET = 'huntress_secret_key'
```
