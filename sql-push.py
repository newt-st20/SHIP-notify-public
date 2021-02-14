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


if os.environ['CHANNEL_TYPE'] == "public":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]


def main():
    now = datetime.datetime.now()
    getTime = now.strftime('%Y/%m/%d %H:%M:%S')
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
    ship_id.send_keys('shj181152')
    password.send_keys('ry9k5btx')
    driver.find_element_by_name('login').click()
    time.sleep(getWaitSecs())

    driver.get("https://ship.sakae-higashi.jp/connection/search.php?obj_id=&depth=&search=&s_y=2011&s_m=01&s_d=01&e_y=2030&e_m=12&e_d=31")
    con = driver.page_source
    conSoup = BeautifulSoup(con, 'html.parser')
    conLinks = conSoup.find_all(class_='allc')[0].find_all('a')
    conEachPage = []
    for conLink in conLinks:
        conOnclick = conLink.get('onclick')
        conId = re.findall("'([^']*)'", conOnclick)[0]
        driver.get(
            "https://ship.sakae-higashi.jp/sub_window_anke/?obj_id="+conId+"&t=3")
        conEachPage.append(driver.page_source)

    driver.get("https://ship.sakae-higashi.jp/study/search.php?obj_id=&depth=&search=&s_y=2011&s_m=01&s_d=01&e_y=2030&e_m=12&e_d=31")
    study = driver.page_source
    studySoup = BeautifulSoup(study, 'html.parser')
    driver.quit()

    conBody = conSoup.find("body")
    conTrs = conSoup.find_all(class_='allc')[0].find_all('tr')
    conTrs.pop(0)
    conList = []
    conc = 0
    for conTr in conTrs:
        eachconList = []
        conTrTds = conTr.find_all('td')
        try:
            stage = conTrTds[2].find('a').get('onclick')
            eachconList.append(re.findall("'([^']*)'", stage))
        except:
            eachconList.append([0, 0])
        eachconList.append(conTrTds[0].text)
        try:
            eachconList.append(conTrTds[1].find('span').get('title'))
        except:
            eachconList.append(conTrTds[1].text)
        eachconList.append(conTrTds[2].text.replace("\n", ""))
        conEachPageSoup = BeautifulSoup(conEachPage[conc], 'html.parser')
        conPageMain = conEachPageSoup.find_all(
            class_='ac')[0].find_all("table")[1]
        conPageDescription = conPageMain.find_all(
            "table")[-2].text.replace("\n", "")
        eachconList.append(conPageDescription)
        conList.append(eachconList)
        conc += 1
    print(conList)

    studyBody = studySoup.find("body")
    studyTrs = studySoup.find_all(class_='allc')[0].find_all('tr')
    studyTrs.pop(0)
    studyList = []
    studyc = 0
    for studyTr in studyTrs:
        eachstudyList = []
        studyTrTds = studyTr.find_all('td')
        try:
            stage = studyTrTds[2].find('a').get('onclick')
            eachstudyList.append(re.findall("'([^']*)'", stage))
        except:
            eachstudyList.append([0, 0])
        eachstudyList.append(studyTrTds[0].text)
        try:
            eachstudyList.append(studyTrTds[1].find('span').get('title'))
        except:
            eachstudyList.append(studyTrTds[1].text)
        eachstudyList.append(studyTrTds[2].text.replace("\n", ""))
        studyList.append(eachstudyList)
        studyc += 1
    print(studyList)

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
        mail = "更新はありません"

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
