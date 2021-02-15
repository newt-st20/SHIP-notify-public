import os
import psycopg2
from psycopg2.extras import DictCursor
import json
import time
import datetime
import requests
import re
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import get

DATABASE_URL = os.environ['DATABASE_URL']

if os.environ['CHANNEL_TYPE'] == "public":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]


def main():
    result = get.main()
    conList = result[0]
    studyList = result[1]
    with get_connection() as conn:
        with conn.cursor() as cur:
            conSendData = []
            studySendData = []
            for i in conList:
                if i[0][0] != 0:
                    cur.execute('SELECT EXISTS (SELECT * FROM con_junior WHERE id = %s)',
                                [int(i[0][0])])
                    (b,) = cur.fetchone()
                    if b == False:
                        date = i[1].replace(
                            "年", "/").replace("月", "/").replace("日", "")
                        cur.execute('INSERT INTO con_junior (id, date, folder, title, description) VALUES (%s, %s, %s, %s, %s)', [
                                    i[0][0], date, i[2], i[3], i[4]])
                        conSendData.append([date, i[2], i[3], i[4]])
            for i in studyList:
                if i[0][0] != 0:
                    cur.execute('SELECT EXISTS (SELECT * FROM study_junior WHERE id = %s)',
                                [int(i[0][0])])
                    (b,) = cur.fetchone()
                    if b == False:
                        date = i[1].replace(
                            "年", "/").replace("月", "/").replace("日", "")
                        cur.execute('INSERT INTO study_junior (id, date, folder, title) VALUES (%s, %s, %s, %s)', [
                                    i[0][0], date, i[2], i[3]])
                        studySendData.append([date, i[2], i[3]])
        conn.commit()

    print(conSendData)
    print(studySendData)

    if len(conSendData) != 0 or len(studySendData) != 0:
        mail = "【" + getTime + "】"
        if len(conSendData) != 0:

            for conEachSendData in conSendData:
                mail += "\n・連絡事項:" + \
                    conEachSendData[0] + "-" + \
                        conEachSendData[1] + "-" + conEachSendData[2]
                if conEachSendData[3] != "":
                    mail += "《" + conEachSendData[3] + "》"
                mail += "\n"
        else:
            mail += "\n連絡事項:更新はありません"
        if len(studySendData) != 0:
            for studyEachSendData in studySendData:
                mail += "\n・連絡事項:" + \
                    studyEachSendData[0] + "-" + \
                        studyEachSendData[1] + "-" + studyEachSendData[2]
                mail += "\n"
        else:
            mail += "\n学習教材:更新はありません"
    else:
        mail = "【" + getTime + "】\n更新はありません"

    print(mail)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                'SELECT id FROM users WHERE notify_status LIKE %s', ["%all%"])
            notifyAllUserList = []
            for row in cur:
                notifyAllUserList.append(row)
            cur.execute(
                'SELECT id FROM users WHERE notify_status LIKE %s', ["%middle%"])
            notifyMiddleUserList = []
            for row in cur:
                notifyMiddleUserList.append(row)
            cur.execute(
                'SELECT id FROM users WHERE notify_status LIKE %s', ["%few%"])
            notifyFewUserList = []
            for row in cur:
                notifyFewUserList.append(row)
            cur.execute(
                'SELECT url FROM discord_webhooks')
            discordWebhookList = []
            for row in cur:
                discordWebhookList.append(row)
        conn.commit()

    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)

    if len(conSendData) != 0 or len(studySendData) != 0:
        broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
        jsonData = jsonLoad['default']
        jsonData['messages'][0]['text'] = mail
        print(jsonData)
        requests.post(broadcastEndPoint, json=jsonData, headers=headers)
        log = "[For]all following user\n[Message]" + mail.replace("\n", "")

        for discordWebhook in discordWebhookList:
            webhook_url = discordWebhook
            main_content = {'content': mail}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                webhook_url, json.dumps(main_content), headers=headers)
    else:
        multicastEndPoint = "https://api.line.me/v2/bot/message/multicast"
        jsonAllData = jsonLoad['pushForNotifyAllUser']
        jsonAllData['messages'][0]['text'] = mail
        jsonData['to'] = notifyAllUserList
        requests.post(multicastEndPoint, json=jsonAllData, headers=headers)
        num = random.randrange(10)
        if num == 0:
            multicastEndPoint = "https://api.line.me/v2/bot/message/multicast"
            jsonAllData = jsonLoad['pushForNotifyMiddleUser']
            jsonAllData['messages'][0]['text'] = "【定期通知】SHIP-notifyは正常に動作しています。"
            jsonData['to'] = notifyMiddleUserList
            requests.post(multicastEndPoint, json=jsonAllData, headers=headers)
            log = "[For]setting notify-all user and notify-middle user\n[Random-num]" + \
                num + "\n[Message]" + mail.replace("\n", "")
        else:
            log = "[For]setting notify-all user\n[Random-num]" + \
                num + "\n[Message]" + mail.replace("\n", "")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO push_log (time, log) VALUES (%s, %s)', [getTime, log])
            conn.commit()
    except:
        import traceback
        traceback.print_exc()


def getWaitSecs():
    # 画面の待機秒数の取得
    max_wait = 7.0  # 最大待機秒
    min_wait = 3.0  # 最小待機秒
    mean_wait = 5.0  # 平均待機秒
    sigma_wait = 1.0  # 標準偏差（ブレ幅）
    return min([max_wait, max([min_wait, round(random.normalvariate(mean_wait, sigma_wait))])])


if __name__ == "__main__":
    main()
