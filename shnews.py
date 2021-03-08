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

now = datetime.datetime.now()
getTime = now.strftime('%Y-%m-%d %H:%M:%S')


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
    driver.get('http://www.sakaehigashi.ed.jp/news/')
    news = driver.page_source
    newsSoup = BeautifulSoup(news, 'html.parser')
    newsTextList = []
    newsEntryList = conSoup.find_all(class_='entry')
    for newsEntry in newsEntryList:
        title = newsEntry.find_all('h3')[0].text
        date = newsEntry.find_all(class_='date')[0].text
        time = newsEntry.find_all(class_='time')[0].find_all(
            class_='time')[0].text.strip("投稿時刻")
        postDateTime = date + time
        body = newsEntry.text.strip(title).strip(date)
        link = newsEntry.find_all('a')[0].get('href')
        category = newsEntry.find_all(class_='cat')[0].find_all('a')[0].text
        newsTextList.append([title, postDateTime, body, link, category])
    time.sleep(getWaitSecs())
    driver.quit()

    with get_connection() as conn:
        with conn.cursor() as cur:
            newsSendData = []
            for i in newsTextList:
                cur.execute('SELECT EXISTS (SELECT * FROM sh_news WHERE title = %s)',
                            [i[0]])
                (b,) = cur.fetchone()
                if b == False:
                    cur.execute('INSERT INTO con_junior (title, datetime, body, link, category) VALUES (%s, %s, %s, %s, %s)', [
                                i[0], i[1], i[2], i[3], i[4]])
                    newsSendData.append(
                        [i[0], i[1], i[2], i[3], i[4]])
        conn.commit()
    sortedNewsSendData = []
    for value in reversed(newsSendData):
        sortedNewsSendData.append(value)
    print(sortedNewsSendData)
    return sortedNewsSendData, getTime


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def getWaitSecs():
    # 画面の待機秒数の取得
    max_wait = 7.0  # 最大待機秒
    min_wait = 3.0  # 最小待機秒
    mean_wait = 5.0  # 平均待機秒
    sigma_wait = 1.0  # 標準偏差（ブレ幅）
    return min([max_wait, max([min_wait, round(random.normalvariate(mean_wait, sigma_wait))])])


if __name__ == "__main__":
    main()
