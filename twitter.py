import json
from requests_oauthlib import OAuth1
import requests
import os
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.environ['TWITTER_API_KEY']
CONSUMER_SECRET = os.environ['TWITTER_API_SECRET_KEY']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']


def main(logid):
    endpoint = "https://api.twitter.com/1.1/statuses/update.json?status=https://ship-assistant.web.app/getlog/"+logid
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    response = requests.post(endpoint, auth=auth).json()
    print(json.dumps(response, indent=4))

if __name__ == '__main__':
    main()