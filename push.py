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
else:
    SPREADSHEET_KEY = '1OwuiunNnZcZ3l2QbnGsricHwSfyWliTpRX68-6W5ji0'

driver_path = '/app/.chromedriver/bin/chromedriver'

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument('--start-maximized')
options.add_argument('--headless')

driver = webdriver.Chrome(executable_path=driver_path, options=options)
driver.get('https://ship.sakae-higashi.jp/')
time.sleep(1)
ship_id = driver.find_element_by_name("ship_id")
password = driver.find_element_by_name("pass")
ship_id.send_keys(os.environ['SHIP_ID'])
password.send_keys(os.environ['SHIP_PASS'])
driver.find_element_by_name('login').click()
time.sleep(1)
driver.get("https://ship.sakae-higashi.jp/connection/connection_main.php")
connection = driver.page_source
driver.get("https://ship.sakae-higashi.jp/study/study_main.php")
study = driver.page_source
driver.quit()

connectionSoup = BeautifulSoup(connection, 'html.parser')
connectionText = connectionSoup.find_all('table')[7].find_all('tr')
connectionList = []
for i in range(len(connectionSoup.find_all('table')[7].find_all('tr'))):
    for j in range(len(connectionSoup.find_all('table')[7].find_all('tr')[i].find_all('td')[0])):
        connectionList.append([connectionSoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[0].text, connectionSoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[1].text, connectionSoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[2].text])
connectionList.pop(0)
studySoup = BeautifulSoup(study, 'html.parser')
studyText = studySoup.find_all('table')[7].find_all('tr')
studyList = []
for i in range(len(studySoup.find_all('table')[7].find_all('tr'))):
    for j in range(len(studySoup.find_all('table')[7].find_all('tr')[i].find_all('td')[0])):
        studyList.append([studySoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[0].text, studySoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[1].text, studySoup.find_all('table')[
            7].find_all('tr')[i].find_all('td')[2].text])
studyList.pop(0)

now = datetime.datetime.now()
time = now.strftime('%Y-%m-%d %H:%M:%S')
connectionSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('connection')
connectionSheetLow = len(connectionSheet.col_values(1))
connectionData = [str(connectionText), str(connectionList), time]
connectionSheet.append_row(connectionData)
connectionOldData = connectionSheet.cell(connectionSheetLow, 2).value
connectionNewData = connectionList
message1 = ""
try:
    if connectionOldData != str(connectionNewData):
        for a in connectionNewData:
            print(str(a))
            if str(a) in str(connectionOldData):
                pass
            else:
                message1 += "\n連絡事項:" + a[0] + "-" + \
                    a[1] + "-" + a[2].replace("\n", "")
    else:
        message1 = "\n連絡事項:更新はありません"
except:
    message1 = "\n連絡事項取得エラー:更新の有無を取得できませんでした"

studySheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('study')
studySheetLow = len(studySheet.col_values(1))
studyData = [str(studyText), str(studyList), time]
studySheet.append_row(studyData)
studyOldData = studySheet.cell(studySheetLow, 2).value
studyNewData = studyList
message2 = ""
try:
    if studyOldData != str(studyNewData):
        for b in studyNewData:
            print(str(b))
            if str(b) in str(studyOldData):
                pass
            else:
                message2 += "\n学習教材:" + b[0] + "-" + \
                    b[1] + "-" + b[2].replace("\n", "")
    else:
        message2 = "\n学習教材:更新はありません"
except:
    message2 = "\n学習教材取得エラー:更新の有無を取得できませんでした"

if os.environ['CHANNEL_TYPE'] == "public":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)


def main():
    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    reportSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('report')
    reportSheetLow = len(reportSheet.col_values(1))
    mail = "【" + time + "】\n" + message1 + message2
    if "連絡事項:更新はありません" in message1 and "学習教材:更新はありません" in message2:
        userId = useridSheet.col_values(1)
        userSetting = useridSheet.col_values(5)
        sendList = []
        userNum = 0
        for userEach in userId:
            if userSetting[userNum] == "not-change-notify-on":
                sendList.append(userEach)
            userNum += 1
        finalSendList = list(set(sendList))
        multicastEndPoint = "https://api.line.me/v2/bot/message/multicast"
        jsonData = jsonLoad['pushForNotifyEnabledUser']
        jsonData['messages'][0]['text'] = mail
        jsonData['to'] = finalSendList
        print(jsonData)
        requests.post(multicastEndPoint, json=jsonData, headers=headers)
        logMessage = "send message:" + \
            str(mail)+" send for:"+str(finalSendList)
        print(logMessage)
        reportSheet.update_cell(reportSheetLow+1, 1,
                                logMessage.replace("\n", ""))
    else:
        broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
        jsonData = jsonLoad['pushForAll']
        jsonData['messages'][0]['text'] = mail
        print(jsonData)
        requests.post(broadcastEndPoint, json=jsonData, headers=headers)
        logMessage = "send message:" + \
            str(mail)+" send for all followed user."
        print(logMessage)
        reportSheet.update_cell(reportSheetLow+1, 1,
                                logMessage.replace("\n", ""))


if __name__ == "__main__":
    main()
