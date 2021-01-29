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
import random


def main():
        if os.environ['CHANNEL_TYPE'] == "public":
        YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
        YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
    else:
        YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
        YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

    line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('other.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    jsonData = jsonLoad['instantNormal']
    jsonData['messages'][0]['text'] = ""
    print(jsonData)
    requests.post(broadcastEndPoint, json=jsonData, headers=headers)
    logMessage = "send message:" + \
        str(mail)+" send for all followed user."
    print(logMessage)
    reportSheet.update_cell(reportSheetLow+1, 1,
                            logMessage.replace("\n", ""))


if __name__ == "__main__":
    main()
