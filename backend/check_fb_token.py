"""Quick script to check Facebook token validity and rate limits."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("FACEBOOK_ACCESS_TOKEN")
r = requests.get(f"https://graph.facebook.com/v21.0/me?fields=id,name&access_token={token}")

print("=== Rate Limit Headers ===")
for k, v in r.headers.items():
    if "usage" in k.lower() or "limit" in k.lower() or "throttle" in k.lower():
        print(f"  {k}: {v}")

print(f"\n=== Response ===")
print(f"  Status: {r.status_code}")
print(f"  Body: {r.json()}")

if r.status_code == 200:
    print("\n✅ Token is VALID")
else:
    print("\n❌ Token is EXPIRED or INVALID")
