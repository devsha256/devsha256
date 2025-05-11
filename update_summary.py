import requests
import json
import yaml
import random
import argparse
from datetime import datetime

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Update Naukri profile summary.")
parser.add_argument("--username", required=True, help="Naukri login username")
parser.add_argument("--password", required=True, help="Naukri login password")
parser.add_argument("--profile-id", required=True, help="Profile ID")
args = parser.parse_args()

# --- Step 1: Authenticate and get access token & cookies ---
login_url = "https://www.naukri.com/central-login-services/v1/login"
login_payload = json.dumps({
    "username": args.username,
    "password": args.password
})
login_headers = {
  'accept': 'application/json',
  'accept-language': 'en-GB,en;q=0.9',
  'appid': '103',
  'cache-control': 'no-cache',
  'clientid': 'd3skt0p',
  'content-type': 'application/json',
  'origin': 'https://www.naukri.com',
  'priority': 'u=1, i',
  'referer': 'https://www.naukri.com/',
  'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'systemid': 'jobseeker',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
}

login_response = requests.post(login_url, headers=login_headers, data=login_payload)

if login_response.status_code != 200:
    print("Failed to log in:", login_response.text)
    exit(1)

login_json = login_response.json()
cookies = login_json.get("cookies", [])

if not cookies or not isinstance(cookies, list):
    print("Invalid or missing cookies in login response.")
    exit(1)

# Get access_token from the first cookie
access_token = cookies[0].get("value")
print(access_token)
if not access_token:
    print("Access token not found in the first cookie.")
    exit(1)

# Compose Cookie header from all cookies
cookie_header = "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies if "name" in cookie and "value" in cookie)

# --- Step 2: Load YAML summaries and calculate years ---
with open("summaries.yml", "r") as f:
    summaries = yaml.safe_load(f)

experience_start = datetime(2020, 2, 24)
now = datetime.now()
years_of_experience = round((now - experience_start).days / 365.25, 2)

if not summaries:
    raise Exception("No summaries found in YAML file.")

chosen_summary = random.choice(summaries).replace("{years}", str(years_of_experience))

# --- Step 3: Update profile summary ---
update_url = "https://www.naukri.com/cloudgateway-mynaukri/resman-aggregator-services/v1/users/self/fullprofiles"
update_payload = json.dumps({
    "profile": {
        "summary": chosen_summary
    },
    "profileId": args.profile_id
})

update_headers = {
    'accept': 'application/json',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'appid': '105',
    'authorization': f'Bearer {access_token}',
    'clientid': 'd3skt0p',
    'content-type': 'application/json',
    'origin': 'https://www.naukri.com',
    'priority': 'u=1, i',
    'referer': 'https://www.naukri.com/mnjuser/profile?id=&altresid&action=modalOpen',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'systemid': 'Naukri',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'x-http-method-override': 'PUT',
    'x-requested-with': 'XMLHttpRequest',
    'Cookie': cookie_header
}

response = requests.post(update_url, headers=update_headers, data=update_payload)

print(f"Response Status: {response.status_code}")
print(response.text)
