import json
from requests_oauthlib import OAuth1
import requests
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

CONSUMER_KEY = os.environ['TWITTER_API_KEY']
CONSUMER_SECRET = os.environ['TWITTER_API_SECRET_KEY']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']


def main(logid, updateList):
    now = datetime.datetime.now()
    date = now.strftime("%y%m%d")
    endpoint = "https://api.twitter.com/1.1/statuses/update.json"
    parameter = {
        "status": str(updateList)+"に更新がありました。\n https://ship-assistant.web.app/log/"+str(logid)+"?utm_source=tw_"+date+"&utm_medium=twitter"
    }
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    response = requests.post(endpoint, params=parameter, auth=auth).json()
    print(json.dumps(response))
    tweetUrl = "https://twitter.com/ShipNotify/status/"+response['id_str']
    return tweetUrl

if __name__ == '__main__':
    main()