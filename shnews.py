import datetime
import os

import pyrebase
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()

config = {
    'apiKey': os.environ['FIREBASE_API_KEY'],
    'authDomain': os.environ['FIREBASE_AUTH_DOMAIN'],
    "databaseURL": "xxxxxx",
    'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET']
}
firebase = pyrebase.initialize_app(config)


if not firebase_admin._apps:
    CREDENTIALS = credentials.Certificate({
    'type': 'service_account',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'project_id': os.environ['FIREBASE_PROJECT_ID'],
    'client_email': os.environ['FIREBASE_CLIENT_EMAIL'],
    'private_key': os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n')
    })
    firebase_admin.initialize_app(CREDENTIALS,{'databaseURL': 'https://'+os.environ['FIREBASE_PROJECT_ID']+'.firebaseio.com'})

db = firestore.client()

def main():
    docs = db.collection('shnews').stream()
    gotList = [doc.to_dict()['title'] for doc in docs]

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
    newsList = []
    newsEntryList = newsSoup.find_all(class_='entry')
    for newsEntry in newsEntryList:
        newsData = {}
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
            body = body[0:100] + "......"
        newsData = {
            "title": title,
            "postDateTime": postDateTime,
            "body": body,
            "link": link,
            "category": category,
            "images": images
        }
        newsList.append(newsData)
    driver.quit()

    sendNewsData = []
    for value in reversed(newsList):
        if value["title"] not in gotList:
            sendNewsData.append(value)
            db.collection('shnews').add({
                "title": value["title"],
                "postDateTime": value["postDateTime"],
                "link": value["link"],
                "category": value["category"],
                "images": value["images"],
                'timestamp': firestore.SERVER_TIMESTAMP
            })
    print(sendNewsData)
    returnData = {
        "newsData": sendNewsData,
        "getTime": getTime
    }
    return returnData


if __name__ == "__main__":
    main()
