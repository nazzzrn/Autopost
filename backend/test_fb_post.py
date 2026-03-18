import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("FACEBOOK_ACCESS_TOKEN")
post_id = "911247978748239_122105138655274710"

url = f"https://graph.facebook.com/v21.0/{post_id}"
params = {
    "fields": "likes.summary(true),comments.summary(true)",
    "access_token": token
}
res = requests.get(url, params=params)
print("Likes/comments:", res.json())

params_ins = {
    "fields": "insights.metric(post_impressions)",
    "access_token": token
}
res_ins = requests.get(url, params=params_ins)
print("Insights:", res_ins.json())
