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

DATABASE_URL = os.environ['DATABASE_URL']


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
        time.sleep(getWaitSecs())
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

    return conList, studyList


def getWaitSecs():
    # 画面の待機秒数の取得
    max_wait = 7.0  # 最大待機秒
    min_wait = 3.0  # 最小待機秒
    mean_wait = 5.0  # 平均待機秒
    sigma_wait = 1.0  # 標準偏差（ブレ幅）
    return min([max_wait, max([min_wait, round(random.normalvariate(mean_wait, sigma_wait))])])


if __name__ == "__main__":
    main()
