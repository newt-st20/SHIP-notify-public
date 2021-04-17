import datetime
import os
import random
import re
import time

import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']




def main():
    now = datetime.datetime.now()
    getTime = now.strftime('%H:%M:%S')
    if os.environ['STATUS'] == "local":
        driver_path = 'C:\chromedriver.exe'
    else:
        driver_path = '/app/.chromedriver/bin/chromedriver'
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get('http://www.sakaehigashi.ed.jp/news/')
    news = driver.page_source
    newsSoup = BeautifulSoup(news, 'html.parser')
    newsTextList = []
    newsEntryList = newsSoup.find_all(class_='entry')
    for newsEntry in newsEntryList:
        title = newsEntry.find_all('h3')[0].text
        date = newsEntry.find_all(class_='date')[0].text
        gtime = newsEntry.find_all(class_='time')[0].text.strip("投稿時刻")
        postDateTime = date + gtime
        link = newsEntry.find_all('a')[0].get('href')
        category = newsEntry.find_all(class_='cat')[0].find_all('a')[0].text
        imageAreas = newsEntry.find_all('img')
        images = []
        for imageArea in imageAreas:
            images.append(imageArea.get('src'))
        body = newsEntry.text.replace(title, "").replace(date, "").replace(
            "カテゴリー："+category, "").replace("投稿時刻", "").replace(gtime, "").replace("\n", "")
        if len(body) > 100:
            body = body[0:100] + "...((省略))"
        newsTextList.append(
            [title, postDateTime, body, link, category, images])
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
                    cur.execute('INSERT INTO sh_news (title, datetime, body, link, category, images) VALUES (%s, %s, %s, %s, %s, %s)', [
                                i[0], i[1], i[2], i[3], i[4], i[5]])
                    if len(i[2]) > 100:
                        body = i[2][0:100] + "...((省略))"
                    newsSendData.append(
                        [i[0], i[1], i[2], i[3], i[4], i[5]])
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
