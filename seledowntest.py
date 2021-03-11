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
import urllib.request

DATABASE_URL = os.environ['DATABASE_URL']

now = datetime.datetime.now()
getTime = now.strftime('%Y-%m-%d %H:%M:%S')


def main():
    urllib.request.urlretrieve(
        'https://ship.sakae-higashi.jp/img/main.jpg', 'logo.png')
