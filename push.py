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


def getWaitSecs():
    # 画面の待機秒数の取得
    max_wait = 7.0  # 最大待機秒
    min_wait = 3.0  # 最小待機秒
    mean_wait = 5.0  # 平均待機秒
    sigma_wait = 1.0  # 標準偏差（ブレ幅）
    return min([max_wait, max([min_wait, round(random.normalvariate(mean_wait, sigma_wait))])])


def main():
    now = datetime.datetime.now()
    getTime = now.strftime('%Y-%m-%d %H:%M:%S')

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
    time.sleep(getWaitSecs())
    ship_id = driver.find_element_by_name("ship_id")
    password = driver.find_element_by_name("pass")
    ship_id.send_keys(os.environ['SHIP_ID'])
    password.send_keys(os.environ['SHIP_PASS'])
    driver.find_element_by_name('login').click()
    time.sleep(getWaitSecs())
    driver.get("https://ship.sakae-higashi.jp/connection/search.php?obj_id=&depth=&search=&s_y=2011&s_m=01&s_d=01&e_y=2030&e_m=12&e_d=31")
    con = driver.page_source
    conSoup = BeautifulSoup(con, 'html.parser')
    conSource = conSoup.find("body")
    conTable = conSoup.find_all(class_='allc')[0]
    conLinks = conTable.find_all('a')
    conTrs = conTable.find_all("tr")
    conDataLists = []
    for conTr in conTrs:
        conDataList = []
        conTds = conTr.find_all("td")
        for conTd in conTds:
            conDataList.append(conTd.text)
        conDataLists.append(conDataList)
    conDataLists.pop(0)
    conPageDescriptions = []
    for conLink in conLinks:
        conOnclick = conLink.attrs['onclick']
        conLeft = conOnclick.find("'")
        conRight = conOnclick.find("'", conLeft+1)
        conId = format(conOnclick[conLeft+1:conRight])
        time.sleep(getWaitSecs())
        driver.get(
            "https://ship.sakae-higashi.jp/sub_window_anke/?obj_id="+conId+"&t=3")
        conEachPage = driver.page_source
        conEachPageSoup = BeautifulSoup(conEachPage, 'html.parser')
        conPageMain = conEachPageSoup.find_all(
            class_='ac')[0].find_all("table")[1]
        conPageDescription = conPageMain.find_all("table")[-2].text
        conPageDescriptions.append(conPageDescription)
    conAllDataCounter = 0
    conAllDataList = []
    for conData in range(len(conDataLists)):
        conDatas = []
        conDatas.append(conDataLists[conAllDataCounter][0])
        conDatas.append(conDataLists[conAllDataCounter][1])
        conDatas.append(conDataLists[conAllDataCounter][2])
        conDatas.append(conPageDescriptions[conAllDataCounter])
        conAllDataList.append(conDatas)
        conAllDataCounter += 1
    print(conAllDataList)
    driver.get("https://ship.sakae-higashi.jp/study/study_main.php")
    study = driver.page_source
    driver.quit()

    studySoup = BeautifulSoup(study, 'html.parser')
    studySource = studySoup.find("body")
    studyText = studySoup.find_all(class_='allc')[0].find_all('tr')
    studyList = []
    for i in range(len(studySoup.find_all(class_='allc')[0].find_all('tr'))):
        for j in range(len(studySoup.find_all(class_='allc')[0].find_all('tr')[i].find_all('td')[0])):
            studyList.append([studySoup.find_all(class_='allc')[0].find_all('tr')[i].find_all('td')[0].text, studySoup.find_all(class_='allc')[
                             0].find_all('tr')[i].find_all('td')[1].text, studySoup.find_all(class_='allc')[0].find_all('tr')[i].find_all('td')[2].text])
    studyList.pop(0)

    connectionSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('connection')
    connectionSheetLow = len(connectionSheet.col_values(1))
    connectionData = [str(conSource), str(conAllDataList), getTime]
    connectionOldData = connectionSheet.cell(connectionSheetLow, 2).value
    message1 = ""
    try:
        conFlex0 = conFlex1 = conFlex2 = conFlex3 = []
        if connectionOldData != str(conAllDataList):
            connectionSheet.append_row(connectionData)
            for a in conAllDataList:
                print("135:"+a[3])
                if str(a) in str(connectionOldData):
                    pass
                else:
                    message1 += "\n・連絡事項:" + \
                        a[0] + "-" + a[1] + "-" + \
                        a[2].replace("\n", "")
                    if a[3].replace("\n", "") != "":
                        message1 += "\n《" + a[3].replace("\n", "") + "》"
                    conFlex0.append(a[0])
                    conFlex1.append(a[1])
                    conFlex2.append(a[2])
                    conFlex3.append(a[3])
        else:
            connectionSheet.update_cell(connectionSheetLow, 4, getTime)
            message1 = "\n・連絡事項:更新はありません"
    except:
        message1 = "\n・連絡事項取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()

    studySheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('study')
    studySheetLow = len(studySheet.col_values(1))
    studyData = [str(studySource), str(studyList), getTime]
    studyOldData = studySheet.cell(studySheetLow, 2).value
    studyNewData = studyList
    message2 = "\n"
    try:
        if studyOldData != str(studyList):
            studySheet.append_row(studyData)
            for b in studyList:
                print(str(b))
                if str(b) in str(studyOldData):
                    pass
                else:
                    message2 += "\n・学習教材:" + b[0] + "-" + \
                        b[1] + "-"
                    if b[2].replace("\n", " ") != "":
                        message2 += b[2].replace("\n", " ")
                    studyFlex0 = studyFlex1 = studyFlex2 = []
                    studyFlex0.append(b[0])
                    studyFlex1.append(b[1])
                    studyFlex2.append(b[2])
        else:
            studySheet.update_cell(studySheetLow, 4, getTime)
            message2 = "\n・学習教材:更新はありません"
    except:
        message2 = "\n・学習教材取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()

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
    jsonOpen = open('push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    reportSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('report')
    reportSheetLow = len(reportSheet.col_values(1))
    mail = "【" + getTime.replace("-", "/") + "】\n" + message1 + message2
    if "連絡事項:更新はありません" in message1 and "学習教材:更新はありません" in message2:
        multicastEndPoint = "https://api.line.me/v2/bot/message/multicast"
        jsonAllData = jsonLoad['pushForNotifyAllUser']
        jsonAllData['messages'][0]['text'] = mail
        userId = useridSheet.col_values(1)
        userSetting = useridSheet.col_values(5)
        sendList = []
        # all
        sendAllList = []
        userNum = 0
        for userEach in userId:
            if "notify-all" in userSetting[userNum]:
                sendAllList.append(userEach)
            userNum += 1
        finalAllSendList = list(set(sendAllList))
        jsonAllData['to'] = finalAllSendList
        requests.post(multicastEndPoint, json=jsonAllData, headers=headers)
        num = random.randrange(30)
        logMessage = "send message:" + \
            str(mail)+" send for:" + str(finalAllSendList) + \
            ". Random number is " + str(num)
        if num == 0:
            # middle
            jsonMiddleData = jsonLoad['pushForNotifyMiddleUser']
            sendMiddleList = []
            userNum = 0
            for userEach in userId:
                if "notify-middle" in userSetting[userNum]:
                    sendMiddleList.append(userEach)
                userNum += 1
            finalMiddleSendList = list(set(sendMiddleList))
            jsonMiddleData['to'] = finalMiddleSendList
            requests.post(multicastEndPoint,
                          json=jsonMiddleData, headers=headers)
            logMessage = "send message:" + \
                str(mail)+"[all] send for:" + str(finalAllSendList) + ",[middle] send for:" + str(finalMiddleSendList) + \
                ". Random number is " + str(num)
        print(logMessage)
        reportSheet.update_cell(reportSheetLow+1, 1,
                                logMessage.replace("\n", ""))
    else:
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
        jsonData = jsonLoad['pushForAll']
        counter = 0
        text = ""
        for conFlex in range(len(conFlex0)):
            text += "\n日付:" + conFlex0[counter] + "\nフォルダ:" + conFlex1[counter] + \
                "\nタイトル:" + conFlex2[counter] + "\n説明:" + conFlex3[counter]
            counter += 1
        jsonData['messages'][0]['body']['contents'][1]['text'] = text
        requests.post(broadcastEndPoint, json=jsonData, headers=headers)


if __name__ == "__main__":
    main()
