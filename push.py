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

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credential_list = {
    "type": "service_account",
    "project_id": os.environ['SHEET_PROJECT_ID'],
    "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
    "private_key": os.environ['SHEET_PRIVATE_KEY'].replace('\\n', '\n'),
    "client_email": os.environ['SHEET_CLIENT_EMAIL'],
    "client_id": os.environ['SHEET_CLIENT_ID'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
}
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credential_list, scope)
gc = gspread.authorize(credentials)

if os.environ['CHANNEL_TYPE'] == "public":
    SPREADSHEET_KEY = '1XylqIA4R8rlIcvA113nEJ_PTYMQTGEBsrsT315glFYM'
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    SPREADSHEET_KEY = '1OwuiunNnZcZ3l2QbnGsricHwSfyWliTpRX68-6W5ji0'
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)


def main(conSendData, studySendData, getTime):
    message1 = ""
    try:
        for a in conSendData:
            message1 += "\n・連絡事項:" + a[0] + "-" + a[1] + "-" + a[2]
            if a[3] != "":
                message1 += "\n《" + a[3] + "》"
    except:
        message1 = "\n・連絡事項取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()

    message2 = ""
    try:
        for b in studySendData:
            message2 += "\n・学習教材:" + b[0] + "-" + b[1] + "-" + b[2]
    except:
        message2 = "\n・学習教材取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()

    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    reportSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('report')
    reportSheetLow = len(reportSheet.col_values(1))
    mail = "【" + getTime + "】\n" + message1 + message2
    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    jsonData = jsonLoad['default']
    jsonData['messages'][0]['text'] = mail
    print(jsonData)
    requests.post(broadcastEndPoint, json=jsonData, headers=headers)
    logMessage = "send message:" + \
        str(mail)+" send for all followed user."
    print(logMessage)
    reportSheet.update_cell(reportSheetLow+1, 1,
                            logMessage.replace("\n", ""))
    # beta-user
    multicastEndPoint = "https://api.line.me/v2/bot/message/multicast"
    jsonData = jsonLoad['pushForAll']
    BetaSendList = findUser(6, "beta-on")
    jsonData['to'] = BetaSendList
    jsonData['messages'][0]['contents']['header']['contents'][1]['text'] = "最終取得: " + \
        getTime.replace("-", "/")
    jsonData['messages'][0]['contents']['body']['contents'][1]['text'] = message1.replace(
        "連絡事項:", "")
    jsonData['messages'][0]['contents']['body']['contents'][4]['text'] = message2.replace(
        "学習教材:", "")
    print(jsonData)
    requests.post(multicastEndPoint, json=jsonData, headers=headers)


def getWaitSecs():
    # 画面の待機秒数の取得
    max_wait = 7.0  # 最大待機秒
    min_wait = 3.0  # 最小待機秒
    mean_wait = 5.0  # 平均待機秒
    sigma_wait = 1.0  # 標準偏差（ブレ幅）
    return min([max_wait, max([min_wait, round(random.normalvariate(mean_wait, sigma_wait))])])


def findUser(row, text):
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    userId = useridSheet.col_values(1)
    userSetting = useridSheet.col_values(row)
    sendList = []
    sendAllList = []
    userNum = 0
    for userEach in userId:
        if text in userSetting[userNum]:
            sendAllList.append(userEach)
        userNum += 1
    return list(set(sendAllList))


if __name__ == "__main__":
    main()
