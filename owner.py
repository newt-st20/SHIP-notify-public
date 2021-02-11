from linebot.models import TextSendMessage
from linebot import LineBotApi
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json
import gspread
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import re

if os.environ['CHANNEL_TYPE'] == "public":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)


def main():
    deviveryDay = (datetime.datetime.now() -
                   datetime.timedelta(days=1)).strftime('%Y%m%d')
    followersDay = (datetime.datetime.now() -
                    datetime.timedelta(days=1)).strftime('%Y%m%d')
    print(deviveryDay)
    delivery = 'https://api.line.me/v2/bot/insight/message/delivery?date='+deviveryDay
    followers = 'https://api.line.me/v2/bot/insight/followers?date='+followersDay
    left = 'https://api.line.me/v2/bot/message/quota/consumption'
    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    deliveryData = requests.get(delivery, headers=headers)
    followersData = requests.get(followers, headers=headers)
    leftData = requests.get(left, headers=headers)
    sendText = deviveryDay + str(deliveryData.json()) + \
        "\n" + followersDay + str(followersData.json()) + \
        "\n" + str(leftData.json())
    jsonOpen = open('json/other.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonData = jsonLoad['ownerVerify']
    jsonData['to'] = os.environ["OWNER_USER_ID"]
    jsonData['messages'][0]['text'] = sendText.replace('"', "'")
    pushEndPoint = "https://api.line.me/v2/bot/message/push"
    requests.post(pushEndPoint, json=jsonData, headers=headers)


if __name__ == "__main__":
    main()
