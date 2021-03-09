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


def chengeGetTime(timeWord):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE discord_config SET value = %s WHERE key = whenget', [timeWord])
        conn.commit()


def whenGetTime():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT EXISTS (SELECT * FROM discord_config WHERE key = whenget)')
            res = cur.fetchone()
        conn.commit()
        timeWord = res[0]
        timeList = timeWord.split(',')
    return timeList


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
